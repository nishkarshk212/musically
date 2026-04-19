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
from utils.formatter import format_time, format_views
from utils.decorators import bot_can_manage_vc, admin_check
from utils.strings import build_playing_message, SUCCESS_ADDED_TO_QUEUE, ERROR_NO_RESULTS, ERROR_QUEUE_FULL, SUPPORT_CHANNEL_USERNAME
from utils.html_helper import blockquote
from config import MAX_QUEUE_SIZE
from core.bot import bot_app
import os
import random
import asyncio
import logging

logger = logging.getLogger(__name__)

# Processing messages - Single clean searching message
AYU = [
    "ᴘʟᴀʏɪɴɢ ꜱσηɢ......"
]


async def send_playing_message(client: Client, chat_id: int, song, song_info=None):
    """Send playing message in background after playback has started"""
    try:
        logger.info(f"📤 [SEND_PLAYING_MSG] Sending playing message for: {song.title}")
        
        # Generate thumbnail asynchronously
        thumb_path = None
        
        # Get metadata from song_info or song object
        thumbnail_url = getattr(song_info, 'thumbnail', song.thumbnail) if song_info else song.thumbnail
        artist = getattr(song_info, 'channel', song.artist) if song_info else song.artist
        views = format_views(getattr(song_info, 'views', song.views)) if song_info else format_views(song.views)
        
        if thumbnail_url:
            thumb_path = create_thumbnail(
                title=song.title,
                artist=artist,
                views=views,
                duration=format_time(song.duration),
                cover_url=thumbnail_url,
                output=f"assets/thumb_{chat_id}_{song.video_id}.png"
            )
        
        # Get bot info
        bot_info = await client.get_me()
        bot_name = bot_info.first_name
        bot_username = bot_info.username
        
        # Build the playing message with clickable title
        playing_caption = build_playing_message(
            title=song.title,
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
            await client.send_photo(
                chat_id=chat_id,
                photo=thumb_path,
                caption=playing_caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
            logger.info(f"✅ [SEND_PLAYING_MSG] Photo message sent successfully")
            # Clean up thumbnail
            try:
                os.remove(thumb_path)
            except:
                pass
        else:
            # Send as text if no thumbnail
            await client.send_message(
                chat_id=chat_id,
                text=playing_caption,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                reply_markup=keyboard
            )
            logger.info(f"✅ [SEND_PLAYING_MSG] Text message sent successfully")
    except Exception as e:
        logger.error(f"Failed to send playing message: {e}")


@admin_check
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
        
        # Check if query is a URL
        is_url = query.startswith(("http://", "https://", "www."))
        
        # FAST CACHE CHECK: If song is in cache, play IMMEDIATELY
        if not is_url and query in downloader._search_cache:
            song_info = downloader._search_cache[query]
            logger.info(f"🚀 [ULTRA-FAST] Cache hit for '{query}', playing immediately")
            
            # Create song object
            song = Song(
                title=song_info.title,
                duration=song_info.duration,
                file_path=song_info.file_path,
                thumbnail=song_info.thumbnail,
                requester=message.from_user.first_name,
                video_id=song_info.video_id,
                url=song_info.url,
                artist=getattr(song_info, 'channel', 'Unknown'),
                views=str(getattr(song_info, 'views', '0'))
            )
            
            if not call_manager.is_playing(chat_id):
                # Set queue state IMMEDIATELY
                queue.current_song = song
                queue.is_playing = True
                
                logger.info(f"🎵 [PLAY_CMD] First song, joining voice chat first")
                
                # MUST join voice chat BEFORE playing (sequential, not parallel)
                await call_manager.join_voice_chat(chat_id, chat_username)
                
                logger.info(f"🎵 [PLAY_CMD] Voice chat joined, now playing song")
                
                # Now play the song
                await call_manager.play_song(chat_id, song)
                
                # Send ONLY ONE playing message
                asyncio.create_task(send_playing_message(client, chat_id, song, song_info))
                return
            else:
                position = queue.add_song(song)
                logger.info(f"📝 [PLAY_CMD] Adding to queue at position {position}")
                await message.reply_text(f"✅ **ᴧᴅᴅєᴅ ᴛᴏ ǫᴜєᴜᴇ ᴧᴛ #{position}**")
                return

        # START SEARCH AND JOIN IN PARALLEL
        # PRIORITY 1: Start joining voice chat FIRST
        join_task = asyncio.create_task(call_manager.join_voice_chat(chat_id, chat_username))
        
        # PRIORITY 2: Start search/download in parallel
        if is_url:
            search_task = asyncio.create_task(downloader.extract_info(query))
        else:
            search_task = asyncio.create_task(downloader.search_and_download(query))

        # Show searching message ONLY if search takes more than 200ms (Reduced from 300ms)
        status_msg = None
        try:
            song_info = await asyncio.wait_for(asyncio.shield(search_task), timeout=0.2)
        except asyncio.TimeoutError:
            status_msg = await message.reply_text("🔍 **δєᴧʀᴄʜɪηɢ...**")
            song_info = await search_task
            
        if not song_info:
            if status_msg:
                await status_msg.edit_text(ERROR_NO_RESULTS.format(query=query))
            else:
                await message.reply_text(ERROR_NO_RESULTS.format(query=query))
            return
        
        # Check queue size
        if queue.size() >= MAX_QUEUE_SIZE:
            if status_msg:
                await status_msg.edit_text(ERROR_QUEUE_FULL.format(max_size=MAX_QUEUE_SIZE))
            else:
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
            url=song_info.url,
            artist=getattr(song_info, 'channel', 'Unknown'),
            views=str(getattr(song_info, 'views', '0'))
        )
        
        # FINAL CHECK: Has the bot started playing something else?
        is_already_playing = call_manager and call_manager.is_playing(chat_id)
        
        if is_already_playing:
            # ALREADY PLAYING - Add to queue (NO duplicate message)
            position = queue.add_song(song)
            
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟσꜱє", callback_data="close_playing")]])
            
            queued_text = SUCCESS_ADDED_TO_QUEUE.format(
                title=song.title,
                duration=format_time(song.duration),
                requester=song.requester,
                position=position
            )
            
            # ONLY edit status message or reply ONCE
            if status_msg:
                await status_msg.edit_text(queued_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            else:
                await message.reply_text(queued_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        else:
            # NOT PLAYING - Join VC and play IMMEDIATELY
            if not call_manager:
                err_text = "❌ Call manager not initialized!"
                if status_msg:
                    await status_msg.edit_text(err_text)
                else:
                    await message.reply_text(err_text)
                return
            
            try:
                # Wait for join to complete BEFORE playing
                await join_task
                
                # Set as current song
                queue.current_song = song
                queue.is_playing = True
                
                # NOW play the song (voice chat is joined)
                await call_manager.play_song(chat_id, song)
                
                # Delete status message if exists (non-blocking)
                if status_msg:
                    asyncio.create_task(status_msg.delete())
                
                # Send ONLY ONE playing message in background
                asyncio.create_task(
                    send_playing_message(
                        client=client,
                        chat_id=chat_id,
                        song=song,
                        song_info=song_info
                    )
                )
                
            except Exception as play_error:
                # Reset state if playback failed
                queue.current_song = None
                queue.is_playing = False
                
                # Check for specific admin required error
                error_msg = str(play_error)
                if "CHAT_ADMIN_REQUIRED" in error_msg:
                    await status_msg.edit_text(
                        "❌ **ᴛєʟєɢʀᴧϻ ꜱᴧʏꜱ: [400 CHAT_ADMIN_REQUIRED]**\n\n"
                        "ᴛʜє ᴧꜱꜱɪꜱᴛᴧηᴛ ηєєᴅꜱ ᴛσ ʙє ᴧη **ᴧᴅϻɪη** ᴡɪᴛʜ ᴘєʀϻɪꜱꜱɪση ᴛσ **ϻᴧηᴧɢє ᴠσɪᴄє ᴄʜᴧᴛꜱ** ᴛσ ꜱᴛᴧʀᴛ ᴛʜє ꜱᴛʀєᴧϻ!"
                    )
                else:
                    await status_msg.edit_text(f"❌ Failed to play: {error_msg}")
                raise
        
        logger.info(f"Play command executed by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Play command error: {e}", exc_info=True)
        
        # Send error log to log group
        if bot_app:
            await bot_app.send_error_log(f"Play Command Error in {message.chat.id}: {str(e)}")
            
        # Send sorry message to the group
        sorry_text = (
            "ꜱᴏʀʀʏ ʙᴀʙᴜ ! ᴛʀʏ ᴘʟᴀʏɪɴɢ ᴏᴛʜᴇʀ \n\n"
            "ᴛʜɪs ᴛʀᴀᴄᴋ ᴄᴏᴜʟᴅɴ'ᴛ ʙᴇ ᴘʟᴀʏᴇᴅ. \n"
            "ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɴᴏᴛʜᴇʀ sᴏɴɢ. 🥀"
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⊜ ꜱᴜᴘᴘσʀᴛ ⊜", url=f"https://t.me/{SUPPORT_CHANNEL_USERNAME}")]
        ])
        
        await message.reply_text(sorry_text, reply_markup=keyboard)
