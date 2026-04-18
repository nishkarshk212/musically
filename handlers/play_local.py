"""
Play Local Files Handler
Handles playing audio/video files from Telegram messages
"""

from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatAction, ParseMode
from pyrogram.errors import MessageNotModified
from core.queue import queue_manager, Song
from core.call_manager import call_manager
from utils.decorators import bot_can_manage_vc, admin_check
from utils.strings import build_playing_message, SUCCESS_ADDED_TO_QUEUE, ERROR_QUEUE_FULL, SUPPORT_CHANNEL_USERNAME
from utils.formatter import format_time
from config import MAX_QUEUE_SIZE
from core.bot import bot_app
import os
import asyncio
import logging

logger = logging.getLogger(__name__)


async def send_playing_message(client: Client, chat_id: int, song):
    """Send playing message for local files"""
    try:
        # Get bot info
        bot_info = await client.get_me()
        bot_name = bot_info.first_name
        bot_username = bot_info.username
        
        # Build the playing message
        playing_caption = build_playing_message(
            title=song.title,
            title_url=None,
            duration=format_time(song.duration),
            requester=song.requester,
            bot_name=bot_name
        )
        
        # Create inline keyboard
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="✦ ᴧᴅᴅ ϻє ✦",
                        url=f"https://t.me/{bot_username}?startgroup=true"
                    ),
                    InlineKeyboardButton(
                        text="ꜱᴜᴘᴘσʀᴛ",
                        url=f"https://t.me/{SUPPORT_CHANNEL_USERNAME}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="ᴄʟσꜱє",
                        callback_data="close_playing"
                    )
                ]
            ]
        )
        
        # Send message
        await client.send_message(
            chat_id=chat_id,
            text=playing_caption,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Failed to send playing message: {e}")


def get_file_info(message: Message) -> dict:
    """Extract file information from message"""
    file_info = {
        'file_id': None,
        'file_name': None,
        'mime_type': None,
        'file_size': 0,
        'duration': 0,
        'file_type': None  # 'audio', 'video', 'document'
    }
    
    # Check for audio file
    if message.audio:
        file_info.update({
            'file_id': message.audio.file_id,
            'file_name': message.audio.file_name or 'audio.mp3',
            'mime_type': message.audio.mime_type,
            'file_size': message.audio.file_size,
            'duration': message.audio.duration or 0,
            'file_type': 'audio'
        })
    
    # Check for video file
    elif message.video:
        file_info.update({
            'file_id': message.video.file_id,
            'file_name': message.video.file_name or 'video.mp4',
            'mime_type': message.video.mime_type,
            'file_size': message.video.file_size,
            'duration': message.video.duration or 0,
            'file_type': 'video'
        })
    
    # Check for document (might be audio/video file)
    elif message.document:
        mime_type = message.document.mime_type or ''
        file_name = message.document.file_name or ''
        
        # Check if document is actually an audio/video file
        if mime_type.startswith(('audio/', 'video/')):
            file_info.update({
                'file_id': message.document.file_id,
                'file_name': file_name,
                'mime_type': mime_type,
                'file_size': message.document.file_size,
                'duration': 0,  # Documents don't have duration info
                'file_type': 'audio' if mime_type.startswith('audio/') else 'video'
            })
    
    return file_info


def is_supported_file(file_info: dict) -> bool:
    """Check if file type is supported for playback"""
    if not file_info['file_id']:
        return False
    
    supported_audio = ['audio/mpeg', 'audio/mp3', 'audio/mp4', 'audio/x-m4a', 'audio/aac', 'audio/ogg', 'audio/wav', 'audio/flac']
    supported_video = ['video/mp4', 'video/webm', 'video/ogg', 'video/x-matroska']
    
    mime_type = file_info['mime_type'] or ''
    
    # Check if it's a supported audio or video format
    if mime_type in supported_audio or mime_type in supported_video:
        return True
    
    # Also check file extension
    file_name = file_info['file_name'] or ''
    supported_extensions = ['.mp3', '.mp4', '.m4a', '.aac', '.ogg', '.wav', '.flac', '.webm', '.mkv']
    
    for ext in supported_extensions:
        if file_name.lower().endswith(ext):
            return True
    
    return False


async def download_telegram_file(client: Client, file_id: str, file_name: str) -> str:
    """Download file from Telegram"""
    try:
        # Create downloads directory if it doesn't exist
        download_dir = "downloads"
        os.makedirs(download_dir, exist_ok=True)
        
        # Generate unique file path
        file_path = os.path.join(download_dir, f"local_{file_id}_{file_name}")
        
        # Check if file already exists
        if os.path.exists(file_path):
            logger.info(f"✅ File already exists: {file_path}")
            return file_path
        
        # Download file
        logger.info(f"📥 Downloading file: {file_name}")
        await client.download_media(
            message=file_id,
            file_name=file_path
        )
        
        # Verify file was downloaded
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            file_size = os.path.getsize(file_path)
            logger.info(f"✅ Downloaded successfully: {file_path} ({file_size / 1024 / 1024:.2f} MB)")
            return file_path
        else:
            logger.error(f"❌ Download failed or file is empty")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to download file: {e}")
        return None


@admin_check
@bot_can_manage_vc
async def play_local_file(client: Client, message: Message):
    """Handle playing local audio/video files from Telegram"""
    try:
        chat_id = message.chat.id
        chat_username = message.chat.username
        queue = queue_manager.get_queue(chat_id)
        
        # Get file information from the replied message
        if not message.reply_to_message:
            await message.reply_text(
                "❌ **Please reply to an audio, video, or document file!**\n\n"
                "📁 Supported formats:\n"
                "• Audio: MP3, M4A, AAC, OGG, WAV, FLAC\n"
                "• Video: MP4, WEBM, MKV"
            )
            return
        
        reply_msg = message.reply_to_message
        file_info = get_file_info(reply_msg)
        
        # Check if file is supported
        if not is_supported_file(file_info):
            await message.reply_text(
                "❌ **Unsupported file format!**\n\n"
                "📁 Please send one of these formats:\n"
                "• Audio: MP3, M4A, AAC, OGG, WAV, FLAC\n"
                "• Video: MP4, WEBM, MKV"
            )
            return
        
        # Check file size (max 100MB for local files)
        max_file_size = 100 * 1024 * 1024  # 100MB
        if file_info['file_size'] > max_file_size:
            await message.reply_text("❌ **File too large!** Maximum size: 100MB")
            return
        
        # Send downloading message
        status_msg = await message.reply_text("📥 **Downloading file...**")
        
        # Download the file
        file_path = await download_telegram_file(
            client=client,
            file_id=file_info['file_id'],
            file_name=file_info['file_name']
        )
        
        if not file_path:
            await status_msg.edit_text("❌ **Failed to download file!**")
            return
        
        # Extract file name without extension for title
        title = os.path.splitext(file_info['file_name'])[0]
        
        # Create Song object
        song = Song(
            title=title,
            duration=file_info['duration'],
            file_path=file_path,
            thumbnail="",  # No thumbnail for local files
            requester=message.from_user.first_name,
            video_id=f"local_{file_info['file_id']}",
            url="",
            artist="Local File",
            views="0"
        )
        
        # Check if queue is full
        if queue.size() >= MAX_QUEUE_SIZE:
            await status_msg.edit_text(ERROR_QUEUE_FULL.format(max_size=MAX_QUEUE_SIZE))
            return
        
        # Check if already playing
        is_already_playing = call_manager and call_manager.is_playing(chat_id)
        
        if is_already_playing:
            # Add to queue
            position = queue.add_song(song)
            
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟσꜱє", callback_data="close_playing")]])
            
            queued_text = SUCCESS_ADDED_TO_QUEUE.format(
                title=song.title,
                duration=format_time(song.duration) if song.duration else "Unknown",
                requester=song.requester,
                position=position
            )
            
            await status_msg.edit_text(queued_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        else:
            # Join voice chat and play
            join_task = asyncio.create_task(call_manager.join_voice_chat(chat_id, chat_username))
            
            # Set as current song
            queue.current_song = song
            queue.is_playing = True
            
            # Play the file
            play_task = asyncio.create_task(call_manager.play_song(chat_id, song))
            
            # Delete status message
            await status_msg.delete()
            
            # Wait for playback to start
            await play_task
            
            # Ensure join is complete
            if not join_task.done():
                await join_task
            
            # Send playing message
            asyncio.create_task(
                send_playing_message(
                    client=client,
                    chat_id=chat_id,
                    song=song
                )
            )
        
        logger.info(f"Local file played by {message.from_user.id} in {chat_id}: {title}")
        
    except Exception as e:
        logger.error(f"Play local file error: {e}", exc_info=True)
        
        # Send error log
        if bot_app:
            await bot_app.send_error_log(f"Play Local File Error in {message.chat.id}: {str(e)}")
        
        # Send error message
        await message.reply_text(
            "❌ **Failed to play local file!**\n\n"
            "Please try again or send a different file."
        )
