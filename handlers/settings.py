"""
Settings Panel Handler
Manages bot settings and configuration with category sub-menus
Adapted from Annie Music style UI
"""

import random
import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, Message
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import MessageNotModified
from database.mongodb import db_manager
from config import OWNER_ID, SUDOERS

logger = logging.getLogger(__name__)

# Settings panel images
SETTINGS_IMAGES = [
    "https://i.ibb.co/PzYnJRB7/anime-girl-autumn-scenery.jpg",
    "https://i.ibb.co/Fv79FW1/anime-girl-kimono-bamboo-forest.jpg",
    "https://i.ibb.co/LhBbppvL/anime-girl-kimono-misty-lake.jpg",
    "https://i.ibb.co/nqPYXqLh/anime-girl-plays-guitar-by-water-night.jpg",
    "https://i.ibb.co/mVmRx517/anime-girl-rock-by-river-autumn-sunset-scenery.jpg",
    "https://i.ibb.co/wFwqqbjk/anime-landscape-person-traveling.jpg",
    "https://i.ibb.co/gM5B48Br/anime-like-illustration-girl-by-sea.jpg",
    "https://i.ibb.co/LXGTZNhc/anime-like-illustration-girl-portrait.jpg",
    "https://i.ibb.co/s9CGyfYK/anime-style-couple-characters-with-fire.jpg",
    "https://i.ibb.co/xStZGy0J/anime-style-scene-with-people-showing-affection-outdoors-street.jpg",
    "https://i.ibb.co/prj9V4vz/anime-character-traveling-2.jpg",
]

async def is_admin_check(callback_query: CallbackQuery):
    """Utility to check if user is admin or owner/sudoer"""
    user_id = callback_query.from_user.id
    if user_id in OWNER_ID or user_id in SUDOERS:
        return True
    if callback_query.message.chat.type == ChatType.PRIVATE:
        return user_id in OWNER_ID or user_id in SUDOERS
    try:
        member = await callback_query.message.chat.get_member(user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False

async def get_settings_markup(chat_id: int):
    """Generate main settings markup with specific requested structure"""
    settings = await db_manager.get_chat_settings(chat_id)
    
    play_mode = settings.get("play_mode", "everyone")
    skip_mode = settings.get("skip_mode", "admins")
    voting_mode = settings.get("voting_mode", "disable")
    
    pm_text = "ᴇᴠᴇʀʏᴏɴᴇ" if play_mode == "everyone" else "ᴀᴅᴍɪɴs"
    sm_text = "ᴇᴠᴇʀʏᴏɴᴇ" if skip_mode == "everyone" else "ᴀᴅᴍɪɴs"
    
    # Voting mode button only appears or works when skip permission is set to Admins
    vm_text = "ᴇɴᴀʙʟᴇ" if voting_mode == "enable" else "ᴅɪsᴀʙʟᴇ"
    
    keyboard = []
    
    # 1. Play Mode Row
    keyboard.append([
        InlineKeyboardButton(f"ᴘʟᴀʏ ᴍᴏᴅᴇ : {pm_text}", callback_data="toggle_playmode")
    ])
    
    # 2. Skip Permission Row
    keyboard.append([
        InlineKeyboardButton(f"sᴋɪᴘ ᴘᴇʀᴍɪssɪᴏɴ : {sm_text}", callback_data="toggle_skipmode")
    ])
    
    # 3. Voting Mode Row (Only if Skip Permission is Admins)
    if skip_mode == "admins":
        keyboard.append([
            InlineKeyboardButton(f"ᴠᴏᴛɪɴɢ ᴍᴏᴅᴇ : {vm_text}", callback_data="toggle_votingmode")
        ])
    
    # 4. Close Row
    keyboard.append([
        InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close_playing")
    ])
    
    return InlineKeyboardMarkup(keyboard)

async def settings_callback(client: Client, callback_query: CallbackQuery):
    """Handle settings main panel with detailed chat info"""
    try:
        if not await is_admin_check(callback_query):
            await callback_query.answer("❌ Admin Only!", show_alert=True)
            return

        chat = callback_query.message.chat
        chat_id = chat.id
        chat_title = chat.title
        
        markup = await get_settings_markup(chat_id)
        
        settings_text = f"""
<b><i>iTunes ✘ Music™ 🎶</i></b>
<b><u>iTunes ✘ Music™ 🎶</u> SETTINGS PANEL</b>

<b>CHAT ID :</b> <code>{chat_id}</code>
<b>CHAT TITLE :</b> <code>{chat_title}</code>

CLICK ON THE BUTTONS BELOW FOR CHANGING SETTINGS.
"""
        selected_image = random.choice(SETTINGS_IMAGES)
        
        try:
            await callback_query.message.edit_media(
                media=InputMediaPhoto(media=selected_image, caption=settings_text),
                reply_markup=markup
            )
        except MessageNotModified:
            pass
        except Exception:
            await callback_query.message.edit_caption(
                caption=settings_text,
                reply_markup=markup
            )
            
        await callback_query.answer("Settings Menu")
        
    except Exception as e:
        logger.error(f"Error in settings_callback: {e}")
        await callback_query.answer(f"Error: {e}", show_alert=True)

# --- Update Handlers ---

async def set_mode_callback(client: Client, callback_query: CallbackQuery):
    """Handle all toggle and setting updates with simple logic"""
    try:
        if not await is_admin_check(callback_query):
            await callback_query.answer("❌ Admin Only!", show_alert=True)
            return

        chat_id = callback_query.message.chat.id
        data = callback_query.data
        settings = await db_manager.get_chat_settings(chat_id)
        
        # 1. Main Toggles
        if data == "toggle_playmode":
            new_mode = "admins" if settings.get("play_mode", "everyone") == "everyone" else "everyone"
            await db_manager.save_chat_settings(chat_id, {"play_mode": new_mode})
            await callback_query.answer(f"✅ Play Mode: {new_mode.title()}")
            
        elif data == "toggle_skipmode":
            new_mode = "everyone" if settings.get("skip_mode", "admins") == "admins" else "admins"
            await db_manager.save_chat_settings(chat_id, {"skip_mode": new_mode})
            await callback_query.answer(f"✅ Skip Mode: {new_mode.title()}")
            
        elif data == "toggle_stopmode":
            new_mode = "everyone" if settings.get("stop_mode", "admins") == "admins" else "admins"
            await db_manager.save_chat_settings(chat_id, {"stop_mode": new_mode})
            await callback_query.answer(f"✅ Stop Mode: {new_mode.title()}")
            
        elif data == "toggle_votingmode":
            new_mode = "enable" if settings.get("voting_mode", "disable") == "disable" else "disable"
            await db_manager.save_chat_settings(chat_id, {"voting_mode": new_mode})
            await callback_query.answer(f"✅ Voting Mode: {new_mode.title()}")
            
        elif data == "toggle_cleanmode":
            new_mode = "disable" if settings.get("clean_mode", "enable") == "enable" else "enable"
            await db_manager.save_chat_settings(chat_id, {"clean_mode": new_mode})
            await callback_query.answer(f"✅ Clean mode: {'ON' if new_mode == 'enable' else 'OFF'}")
            
        elif data == "toggle_logging":
            new_mode = "disable" if settings.get("logging", "enable") == "enable" else "enable"
            await db_manager.save_chat_settings(chat_id, {"logging": new_mode})
            await callback_query.answer(f"✅ Logging: {'ON' if new_mode == 'enable' else 'OFF'}")

        # Update the markup after any toggle
        markup = await get_settings_markup(chat_id)
        try:
            await callback_query.message.edit_reply_markup(reply_markup=markup)
        except MessageNotModified:
            pass
        
    except MessageNotModified:
        pass
    except Exception as e:
        logger.error(f"Error in set_mode_callback: {e}")
        await callback_query.answer(f"Update failed: {e}", show_alert=True)

# --- Category Sub-Panels ---

async def quality_callback(client: Client, callback_query: CallbackQuery):
    """Handle quality settings sub-menu"""
    chat_id = callback_query.message.chat.id
    settings = await db_manager.get_chat_settings(chat_id)
    current = settings.get("quality", "high")
    
    keyboard = [
        [
            InlineKeyboardButton(f"{'✅ ' if current == 'low' else ''}Low", callback_data="set_q_low"),
            InlineKeyboardButton(f"{'✅ ' if current == 'medium' else ''}Medium", callback_data="set_q_medium")
        ],
        [
            InlineKeyboardButton(f"{'✅ ' if current == 'high' else ''}High", callback_data="set_q_high"),
            InlineKeyboardButton(f"{'✅ ' if current == 'studio' else ''}Studio", callback_data="set_q_studio")
        ],
        [InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")]
    ]
    try:
        await callback_query.message.edit_caption(
            caption="📡 **ꜱєʟєᴄᴛ ᴧᴜᴅɪσ ǫᴜᴧʟɪᴛʏ:**",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except MessageNotModified:
        pass
    except Exception as e:
        logger.error(f"Error in quality_callback: {e}")
    await callback_query.answer("Quality Settings")

async def volume_callback(client: Client, callback_query: CallbackQuery):
    """Handle volume settings sub-menu"""
    chat_id = callback_query.message.chat.id
    settings = await db_manager.get_chat_settings(chat_id)
    current = settings.get("volume", 100)
    
    keyboard = [
        [
            InlineKeyboardButton(f"{'✅ ' if current == 50 else ''}50%", callback_data="set_v_50"),
            InlineKeyboardButton(f"{'✅ ' if current == 100 else ''}100%", callback_data="set_v_100")
        ],
        [
            InlineKeyboardButton(f"{'✅ ' if current == 150 else ''}150%", callback_data="set_v_150"),
            InlineKeyboardButton(f"{'✅ ' if current == 200 else ''}200%", callback_data="set_v_200")
        ],
        [InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")]
    ]
    try:
        await callback_query.message.edit_caption(
            caption="🔊 **ꜱєʟєᴄᴛ ᴅєꜰᴧᴜʟᴛ ᴠσʟᴜϻє:**",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except MessageNotModified:
        pass
    except Exception as e:
        logger.error(f"Error in volume_callback: {e}")
    await callback_query.answer("Volume Settings")

async def videomode_callback(client: Client, callback_query: CallbackQuery):
    """Handle video mode settings sub-menu"""
    chat_id = callback_query.message.chat.id
    settings = await db_manager.get_chat_settings(chat_id)
    current = settings.get("video_mode", "720p")
    
    keyboard = [
        [
            InlineKeyboardButton(f"{'✅ ' if current == '480p' else ''}480p", callback_data="set_vid_480p"),
            InlineKeyboardButton(f"{'✅ ' if current == '720p' else ''}720p", callback_data="set_vid_720p")
        ],
        [
            InlineKeyboardButton(f"{'✅ ' if current == '1080p' else ''}1080p", callback_data="set_vid_1080p"),
            InlineKeyboardButton(f"{'✅ ' if current == 'hd' else ''}HD", callback_data="set_vid_hd")
        ],
        [InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")]
    ]
    try:
        await callback_query.message.edit_caption(
            caption="📹 **ꜱєʟєᴄᴛ ᴠɪᴅєσ ǫᴜᴧʟɪᴛʏ:**",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except MessageNotModified:
        pass
    except Exception as e:
        logger.error(f"Error in videomode_callback: {e}")
    await callback_query.answer("Video Mode Settings")

async def update_sub_setting(client: Client, callback_query: CallbackQuery):
    """Update settings from sub-menus (Quality, Volume, Video)"""
    chat_id = callback_query.message.chat.id
    data = callback_query.data
    
    if data.startswith("set_q_"):
        val = data.replace("set_q_", "")
        await db_manager.save_chat_settings(chat_id, {"quality": val})
        await quality_callback(client, callback_query)
    elif data.startswith("set_v_"):
        val = int(data.replace("set_v_", ""))
        await db_manager.save_chat_settings(chat_id, {"volume": val})
        await volume_callback(client, callback_query)
    elif data.startswith("set_vid_"):
        val = data.replace("set_vid_", "")
        await db_manager.save_chat_settings(chat_id, {"video_mode": val})
        await videomode_callback(client, callback_query)
