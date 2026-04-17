"""
Play Command Handler
Handles /play command for playing songs
"""

from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatAction, ParseMode
from core.queue import queue_manager, Song
from core.call_manager import call_manager
from utils.downloader import downloader
from utils.thumbnail_generator import create_thumbnail
from utils.formatter import format_time
from utils.decorators import bot_can_manage_vc
from utils.strings import build_playing_message, SUCCESS_ADDED_TO_QUEUE, ERROR_NO_RESULTS, ERROR_QUEUE_FULL, SUPPORT_CHANNEL_USERNAME
from utils.html_helper import blockquote
from config import MAX_QUEUE_SIZE
import os
import random
import asyncio
import logging

logger = logging.getLogger(__name__)

# Processing messages - Single clean searching message
AYU = [
    "ᴘʟᴀʏɪɴɢ ꜱσηɢ......"
]


async def send_playing_message(client: Client, message: Message, song, chat_id: int, song_info):
    """Send playing message in background after playback has started"""
    try:
        # Generate thumbnail asynchronously
        thumb_path = None
        if song_info.thumbnail:
            thumb_path = create_thumbnail(
                title=song.title,
                artist=song_info.channel,
                views="",
                duration=format_time(song.duration),
                cover_url=song_info.thumbnail,
                output=f"assets/thumb_{chat_id}_{song_info.video_id}.png"
            )
        
        # Get bot info
        bot_info = await client.get_me()
        bot_name = bot_info.first_name
        bot_username = bot_info.username
        
        # Build the playing message with clickable title
        playing_caption = build_playing_message(
            title=song.title[:35],
            title_url=song.url if hasattr(song, 'url') else None,
            duration=format_time(song.duration),
            requester=song.requester,
            bot_name=bot_name
        )
        
        # Create inline keyboard with buttons
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
        
        # Send message with thumbnail if available
        if thumb_path and os.path.exists(thumb_path):
            await message.reply_photo(
                photo=thumb_path,
                caption=playing_caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
            # Clean up thumbnail
            try:
                os.remove(thumb_path)
            except:
                pass
        else:
            # Send as text if no thumbnail
            await message.reply_text(
                playing_caption,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                reply_markup=keyboard
            )
    except Exception as e:
        logger.error(f"Failed to send playing message: {e}")


@bot_can_manage_vc
async def play_command(client: Client, message: Message):
    """Handle /play command"""
    try:
        chat_id = message.chat.id
        chat_username = message.chat.username  # Get chat username if available
        queue = queue_manager.get_queue(chat_id)
        
        # Check if reply to a message with URL
        if message.reply_to_message and message.reply_to_message.text:
            query = message.reply_to_message.text.strip()
        elif len(message.command) > 1:
            query = " ".join(message.command[1:])
        else:
            # Show usage message with image and buttons
            from utils.group_start import GROUP_START_IMAGES
            
            play_usage_text = """
╭───────────────────▣
│❍ **ᴘʟᴀʏ ᴄᴏᴍᴍᴀɴᴅ ᴜsᴀɢᴇ :**
├───────────────────▣
│
│𝖴𝗌𝖺𝗀𝖾 : /play [ 𝖲𝗈𝗇𝗀 𝖭𝖺𝗆𝖾 / 𝖸𝗈𝗎𝖳𝗎𝖻𝖾 𝖴𝗋𝗅 / 𝖱𝖾𝗉𝗅𝗒 𝖳𝗈 𝖠 𝖠𝗎𝖽𝗂𝗈 / 𝖵𝗂𝖽𝖾𝗈 𝖥𝗂𝗅𝖾 ]
│
╰───────────────────▣
"""
            
            # Randomly select an image
            selected_image = random.choice(GROUP_START_IMAGES)
            
            # Create inline keyboard with support and close buttons only
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⊜ ꜱᴜᴘᴘσʀᴛ ⊜", url=f"https://t.me/{SUPPORT_CHANNEL_USERNAME}"),
                    InlineKeyboardButton("ᴄʟσꜱє", callback_data="close_playing")
                ]
            ])
            
            await message.reply_photo(
                photo=selected_image,
                caption=play_usage_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Check if query is URL and process asynchronously for speed
        is_url = query.startswith(("http://", "https://"))
        
        # Start downloading immediately - NO message yet for maximum speed
        if is_url:
            # Extract info from URL - faster
            song_info = await downloader.extract_info(query)
            if not song_info:
                await message.reply_text(
                    "❌ Failed to extract information from the URL.\n"
                    "Please make sure it's a valid YouTube link."
                )
                return
        else:
            # Search and download - optimized
            song_info = await downloader.search_and_download(query)
            if not song_info:
                await message.reply_text(ERROR_NO_RESULTS.format(query=query))
                return
        
        # Check queue size
        if queue.size() >= MAX_QUEUE_SIZE:
            await message.reply_text(ERROR_QUEUE_FULL.format(max_size=MAX_QUEUE_SIZE))
            return
        
        # Create Song object
        song = Song(
            title=song_info.title,
            duration=song_info.duration,
            file_path=song_info.file_path,
            thumbnail=song_info.thumbnail,
            requester=message.from_user.first_name,
            video_id=song_info.video_id,
            url=song_info.url
        )
        
        # PRIORITY: Start playing IMMEDIATELY (within 1 second)
        if call_manager and call_manager.is_playing(chat_id):
            # Add to queue - fast operation
            position = queue.add_song(song)
            
            # NOW send message (after queue add)
            processing_msg = await message.reply_text(
                f"**{random.choice(AYU)}**"
            )
            
            # Get bot username for buttons
            bot_username = (await client.get_me()).username
            
            # Create keyboard with close button
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("ᴄʟσꜱє", callback_data="close_playing")
                ]
            ])
            
            await processing_msg.edit_text(
                SUCCESS_ADDED_TO_QUEUE.format(
                    title=song.title,
                    duration=format_time(song.duration),
                    requester=song.requester,
                    position=position
                ),
                reply_markup=keyboard
            )
        else:
            # NOT PLAYING - Join VC and play IMMEDIATELY (highest priority)
            if not call_manager:
                await message.reply_text("❌ Call manager not initialized!")
                return
            
            # Show quick processing message
            processing_msg = await message.reply_text(
                f"**{random.choice(AYU)}**"
            )
            
            # IMMEDIATE: Add to queue first, then join voice chat and start playback
            try:
                # Add song to queue FIRST to prevent auto-leave
                queue.add_song(song)
                queue.current_song = song
                queue.is_playing = True  # Mark as playing immediately
                logger.info(f"Song added to queue and marked as playing for chat {chat_id}")
                
                # Join voice chat and start playback
                assistant_already_present = await call_manager.join_voice_chat(chat_id, chat_username)
                logger.info(f"Voice chat joined for chat {chat_id}")
                await call_manager.play_song(chat_id, song)
                logger.info(f"play_song() completed for chat {chat_id}")
                
                # NOW playback has started, delete processing msg
                await processing_msg.delete()
                
                # Send playing message in background (non-blocking)
                asyncio.create_task(
                    send_playing_message(
                        client=client,
                        message=message,
                        song=song,
                        chat_id=chat_id,
                        song_info=song_info
                    )
                )
                
            except Exception as play_error:
                await processing_msg.edit_text(f"❌ Failed to play: {str(play_error)}")
                raise
        
        logger.info(f"Play command executed by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Play command error: {e}", exc_info=True)
        
        # Provide helpful error messages for common issues
        error_msg = str(e)
        if "CHANNEL_INVALID" in error_msg:
            await message.reply_text(
                "❌ **Channel Error:** The bot cannot access this channel.\n\n"
                "**To fix this:**\n"
                "1. Make sure the bot is an admin in the channel\n"
                "2. Make sure your user account (session) is a member of the channel\n"
                "3. Ensure SESSION_STRING is properly configured in .env\n"
                "4. Try using the command in a group instead of a channel"
            )
        elif "User account session is required" in error_msg:
            await message.reply_text(
                "❌ **User Session Required:** Playing in channels requires a user account session.\n\n"
                "**To fix this:**\n"
                "1. Run `python session_generator.py` to generate a session string\n"
                "2. Add the SESSION_STRING to your .env file\n"
                "3. Restart the bot"
            )
        else:
            await message.reply_text(
                f"❌ An error occurred while playing the song.\n\n"
                f"**Error:** `{str(e)}`\n\n"
                "Please try again or contact support."
            )
