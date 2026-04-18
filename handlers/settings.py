"""
Settings Panel Handler
Manages bot settings and configuration
"""

import random
from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from database.mongodb import db_manager
from config import OWNER_ID, SUDOERS

# Settings panel images (same as start images)
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
    
    # Owner and Sudoers bypass everything
    if user_id in OWNER_ID or user_id in SUDOERS:
        return True
        
    # Private chat - only owner/sudoer allowed in settings usually
    if callback_query.message.chat.type == "private":
        return user_id in OWNER_ID or user_id in SUDOERS
        
    # Group chat - check admin status
    try:
        member = await callback_query.message.chat.get_member(user_id)
        return member.status in ['administrator', 'creator']
    except Exception:
        return False

async def settings_callback(client: Client, callback_query: CallbackQuery):
    """Handle settings button callback"""
    try:
        if not await is_admin_check(callback_query):
            await callback_query.answer("❌ ᴛʜɪꜱ ᴘᴧηєʟ ɪꜱ ʀєꜱᴛʀɪᴄᴛєᴅ ᴛσ ɢʀσᴜᴩ ᴧᴅϻɪηꜱ!", show_alert=True)
            return

        # Settings message text
        settings_text = """
╭───────────────────▣
│❍ **ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ ᴘᴀɴᴇʟ :**
├───────────────────▣
│
│⚙️ ᴄᴏɴꜰɪɢᴜʀᴇ ʏᴏᴜʀ ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ
│   ꜰʀᴏᴍ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ.
│
╰───────────────────▣
"""
        
        # Randomly select an image
        selected_image = random.choice(SETTINGS_IMAGES)
        
        # Create settings keyboard with proper symbols
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• ᴘʟᴀʏ ϻσᴅє •", callback_data="set_playmode"),
                InlineKeyboardButton("• ꜱᴋɪᴘ ϻσᴅє •", callback_data="set_skipmode")
            ],
            [
                InlineKeyboardButton("• ǫᴜᴀʟɪᴛʏ •", callback_data="set_quality"),
                InlineKeyboardButton("• ʟᴀηɢᴜᴀɢє •", callback_data="set_language")
            ],
            [
                InlineKeyboardButton("• ᴠσʟᴜϻє •", callback_data="set_volume"),
                InlineKeyboardButton("• ᴠɪᴅєσ ϻσᴅє •", callback_data="set_videomode")
            ],
            [
                InlineKeyboardButton("• ᴄʟєᴀη ϻσᴅє •", callback_data="set_cleanmode"),
                InlineKeyboardButton("• ʟσɢɢɪηɢ •", callback_data="set_logging")
            ],
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="back_to_start")
            ]
        ])
        
        # Edit the same message
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=settings_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Settings Panel", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading settings", show_alert=True)


async def playmode_callback(client: Client, callback_query: CallbackQuery):
    """Handle play mode settings"""
    try:
        if not await is_admin_check(callback_query):
            await callback_query.answer("❌ ᴛʜɪꜱ ᴘᴧηєʟ ɪꜱ ʀєꜱᴛʀɪᴄᴛєᴅ ᴛσ ɢʀσᴜᴩ ᴧᴅϻɪηꜱ!", show_alert=True)
            return

        chat_id = callback_query.message.chat.id
        settings = await db_manager.get_chat_settings(chat_id)
        current_mode = settings.get("play_mode", "everyone")
        
        # Toggle checkmarks
        e_tick = " ✅" if current_mode == "everyone" else ""
        a_tick = " ✅" if current_mode == "admins" else ""
        au_tick = " ✅" if current_mode == "auth" else ""

        playmode_text = f"""
╭───────────────────▣
│❍ **ᴘʟᴀʏ ϻσᴅє ꜱᴇᴛᴛɪɴɢꜱ :**
├───────────────────▣
│
│🎵 **ᴡʜᴏ ᴄᴀɴ ᴘʟᴀʏ sᴏɴɢs:**
│
│❍ **ᴇᴠᴇʀʏᴏɴᴇ**{e_tick}
│❍ **ᴀᴅᴍɪɴs**{a_tick}
│❍ **ᴀᴜᴛʜ ᴜsᴇʀs**{au_tick}
│
╰───────────────────▣
"""
        
        selected_image = random.choice(SETTINGS_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"• ᴇᴠᴇʀʏᴏɴᴇ{e_tick} •", callback_data="pm_everyone"),
                InlineKeyboardButton(f"• ᴀᴅᴍɪɴs{a_tick} •", callback_data="pm_admins")
            ],
            [
                InlineKeyboardButton(f"• ᴀᴜᴛʜ ᴜsᴇʀs{au_tick} •", callback_data="pm_auth")
            ],
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=playmode_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Play Mode Settings", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading play mode settings", show_alert=True)


async def skipmode_callback(client: Client, callback_query: CallbackQuery):
    """Handle skip mode settings"""
    try:
        if not await is_admin_check(callback_query):
            await callback_query.answer("❌ ᴛʜɪꜱ ᴘᴧηєʟ ɪꜱ ʀєꜱᴛʀɪᴄᴛєᴅ ᴛσ ɢʀσᴜᴩ ᴧᴅϻɪηꜱ!", show_alert=True)
            return

        chat_id = callback_query.message.chat.id
        settings = await db_manager.get_chat_settings(chat_id)
        current_mode = settings.get("skip_mode", "admins")
        
        # Toggle checkmarks
        e_tick = " ✅" if current_mode == "everyone" else ""
        a_tick = " ✅" if current_mode == "admins" else ""
        au_tick = " ✅" if current_mode == "auth" else ""

        skipmode_text = f"""
╭───────────────────▣
│❍ **ꜱᴋɪᴘ ϻσᴅє ꜱᴇᴛᴛɪɴɢꜱ :**
├───────────────────▣
│
│⏭️ **ᴡʜᴏ ᴄᴀɴ sᴋɪᴘ sᴏɴɢs:**
│
│❍ **ᴇᴠᴇʀʏᴏɴᴇ**{e_tick}
│❍ **ᴀᴅᴍɪɴs**{a_tick}
│❍ **ᴀᴜᴛʜ ᴜsᴇʀs**{au_tick}
│
╰───────────────────▣
"""
        
        selected_image = random.choice(SETTINGS_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"• ᴇᴠᴇʀʏᴏɴᴇ{e_tick} •", callback_data="sm_everyone"),
                InlineKeyboardButton(f"• ᴀᴅᴍɪɴs{a_tick} •", callback_data="sm_admins")
            ],
            [
                InlineKeyboardButton(f"• ᴀᴜᴛʜ ᴜsᴇʀs{au_tick} •", callback_data="sm_auth")
            ],
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=skipmode_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Skip Mode Settings", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading skip mode settings", show_alert=True)


async def set_mode_callback(client: Client, callback_query: CallbackQuery):
    """Handle setting individual modes"""
    try:
        if not await is_admin_check(callback_query):
            await callback_query.answer("❌ ᴛʜɪꜱ ᴘᴧηєʟ ɪꜱ ʀєꜱᴛʀɪᴄᴛєᴅ ᴛσ ɢʀσᴜᴩ ᴧᴅϻɪηꜱ!", show_alert=True)
            return

        chat_id = callback_query.message.chat.id
        data = callback_query.data
        
        if data.startswith("pm_"):
            mode = data.replace("pm_", "")
            await db_manager.save_chat_settings(chat_id, {"play_mode": mode})
            await callback_query.answer(f"✅ Play mode set to {mode}!", show_alert=False)
            await playmode_callback(client, callback_query)
            
        elif data.startswith("sm_"):
            mode = data.replace("sm_", "")
            await db_manager.save_chat_settings(chat_id, {"skip_mode": mode})
            await callback_query.answer(f"✅ Skip mode set to {mode}!", show_alert=False)
            await skipmode_callback(client, callback_query)
            
        elif data.startswith("quality_"):
            quality = data.replace("quality_", "")
            await db_manager.save_chat_settings(chat_id, {"quality": quality})
            await callback_query.answer(f"✅ Quality set to {quality}!", show_alert=False)
            await quality_callback(client, callback_query)
            
        elif data.startswith("lang_"):
            lang = data.replace("lang_", "")
            await db_manager.save_chat_settings(chat_id, {"language": lang})
            await callback_query.answer(f"✅ Language set to {lang}!", show_alert=False)
            await language_callback(client, callback_query)
            
        elif data.startswith("vol_"):
            vol = int(data.replace("vol_", ""))
            await db_manager.save_chat_settings(chat_id, {"volume": vol})
            await callback_query.answer(f"✅ Volume set to {vol}%!", show_alert=False)
            await volume_callback(client, callback_query)
            
        elif data.startswith("clean_"):
            status = data.replace("clean_", "")
            await db_manager.save_chat_settings(chat_id, {"clean_mode": status})
            await callback_query.answer(f"✅ Clean mode {status}d!", show_alert=False)
            await cleanmode_callback(client, callback_query)
            
        elif data.startswith("log_"):
            status = data.replace("log_", "")
            await db_manager.save_chat_settings(chat_id, {"logging": status})
            await callback_query.answer(f"✅ Logging {status}d!", show_alert=False)
            await logging_callback(client, callback_query)

    except Exception as e:
        await callback_query.answer("Error saving setting", show_alert=True)


async def quality_callback(client: Client, callback_query: CallbackQuery):
    """Handle quality settings"""
    try:
        if not await is_admin_check(callback_query):
            await callback_query.answer("❌ ᴛʜɪꜱ ᴘᴧηєʟ ɪꜱ ʀєꜱᴛʀɪᴄᴛєᴅ ᴛσ ᴧᴅϻɪηꜱ!", show_alert=True)
            return

        chat_id = callback_query.message.chat.id
        settings = await db_manager.get_chat_settings(chat_id)
        current_q = settings.get("quality", "medium")
        
        # Checkmarks
        l_tick = " ✅" if current_q == "low" else ""
        m_tick = " ✅" if current_q == "medium" else ""
        h_tick = " ✅" if current_q == "high" else ""
        s_tick = " ✅" if current_q == "studio" else ""

        quality_text = f"""
╭───────────────────▣
│❍ **ǫᴜᴀʟɪᴛʏ ꜱᴇᴛᴛɪɴɢꜱ :**
├───────────────────▣
│
│🎧 **sᴇʟᴇᴄᴛ ᴀᴜᴅɪᴏ ǫᴜᴀʟɪᴛʏ:**
│
│❍ **ʟᴏᴡ**{l_tick}
│❍ **ϻᴇᴅɪᴜϻ**{m_tick}
│❍ **ʜɪɢʜ**{h_tick}
│❍ **ꜱᴛᴜᴅɪᴏ**{s_tick}
│
╰───────────────────▣
"""
        
        selected_image = random.choice(SETTINGS_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"• ʟᴏᴡ{l_tick} •", callback_data="quality_low"),
                InlineKeyboardButton(f"• ϻᴇᴅɪᴜϻ{m_tick} •", callback_data="quality_medium")
            ],
            [
                InlineKeyboardButton(f"• ʜɪɢʜ{h_tick} •", callback_data="quality_high"),
                InlineKeyboardButton(f"• ꜱᴛᴜᴅɪᴏ{s_tick} •", callback_data="quality_studio")
            ],
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=quality_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Quality Settings", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading quality settings", show_alert=True)


async def language_callback(client: Client, callback_query: CallbackQuery):
    """Handle language settings"""
    try:
        if not await is_admin_check(callback_query):
            await callback_query.answer("❌ ᴛʜɪꜱ ᴘᴧηєʟ ɪꜱ ʀєꜱᴛʀɪᴄᴛєᴅ ᴛσ ᴧᴅϻɪηꜱ!", show_alert=True)
            return

        chat_id = callback_query.message.chat.id
        settings = await db_manager.get_chat_settings(chat_id)
        current_lang = settings.get("language", "en")
        
        en_tick = " ✅" if current_lang == "en" else ""
        hi_tick = " ✅" if current_lang == "hi" else ""

        language_text = f"""
╭───────────────────▣
│❍ **ʟᴀηɢᴜᴀɢє ꜱᴇᴛᴛɪɴɢꜱ :**
├───────────────────▣
│
│🌐 **sᴇʟᴇᴄᴛ ʙᴏᴛ ʟᴀɴɢᴜᴀɢᴇ:**
│
│❍ **ᴇɴɢʟɪsʜ**{en_tick}
│❍ **ʜɪɴᴅɪ**{hi_tick}
│
╰───────────────────▣
"""
        
        selected_image = random.choice(SETTINGS_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"• ᴇɴɢʟɪsʜ{en_tick} •", callback_data="lang_en"),
                InlineKeyboardButton(f"• ʜɪɴᴅɪ{hi_tick} •", callback_data="lang_hi")
            ],
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")
            ]
        ])
        
        await callback_query.answer("Language Settings", show_alert=False)
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=language_text,
            reply_markup=keyboard
        )
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in language_callback: {e}", exc_info=True)
        await callback_query.answer(f"Error loading language settings: {str(e)}", show_alert=True)


async def volume_callback(client: Client, callback_query: CallbackQuery):
    """Handle volume settings"""
    try:
        if not await is_admin_check(callback_query):
            await callback_query.answer("❌ ᴛʜɪꜱ ᴘᴧηєʟ ɪꜱ ʀєꜱᴛʀɪᴄᴛєᴅ ᴛσ ᴧᴅϻɪηꜱ!", show_alert=True)
            return

        chat_id = callback_query.message.chat.id
        settings = await db_manager.get_chat_settings(chat_id)
        current_vol = settings.get("volume", 100)
        
        v50_tick = " ✅" if current_vol == 50 else ""
        v100_tick = " ✅" if current_vol == 100 else ""
        v150_tick = " ✅" if current_vol == 150 else ""
        v200_tick = " ✅" if current_vol == 200 else ""

        volume_text = f"""
╭───────────────────▣
│❍ **ᴠσʟᴜϻє ꜱᴇᴛᴛɪɴɢꜱ :**
├───────────────────▣
│
│🔊 **sᴇᴛ ᴅᴇꜰᴀᴜʟᴛ ᴠᴏʟᴜᴍᴇ:**
│
│❍ **50%**{v50_tick}
│❍ **100%**{v100_tick}
│❍ **150%**{v150_tick}
│❍ **200%**{v200_tick}
│
╰───────────────────▣
"""
        
        selected_image = random.choice(SETTINGS_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"• 50%{v50_tick} •", callback_data="vol_50"),
                InlineKeyboardButton(f"• 100%{v100_tick} •", callback_data="vol_100")
            ],
            [
                InlineKeyboardButton(f"• 150%{v150_tick} •", callback_data="vol_150"),
                InlineKeyboardButton(f"• 200%{v200_tick} •", callback_data="vol_200")
            ],
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=volume_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Volume Settings", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading volume settings", show_alert=True)


async def authmode_callback(client: Client, callback_query: CallbackQuery):
    """Handle auth mode settings"""
    try:
        authmode_text = """
╭───────────────────▣
│❍ **ᴀᴜᴛʜ ϻσᴅє ꜱᴇᴛᴛɪɴɢꜱ :**
├───────────────────▣
│
│🔐 **sᴇʟᴇᴄᴛ ᴀᴜᴛʜ ᴍᴏᴅᴇ:**
│
│❍ /auth - ᴀᴅᴅ ᴀᴅᴍɪɴ
│❍ /unauth - ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ
│❍ /authusers - ʟɪsᴛ ᴀᴅᴍɪɴs
│
╰───────────────────▣
"""
        
        selected_image = random.choice(SETTINGS_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• ᴇᴠᴇʀʏᴏɴᴇ •", callback_data="auth_everyone"),
                InlineKeyboardButton("• ᴀᴅᴍɪɴs •", callback_data="auth_admins")
            ],
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=authmode_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Auth Mode Settings", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading auth mode settings", show_alert=True)


async def videomode_callback(client: Client, callback_query: CallbackQuery):
    """Handle video mode settings"""
    try:
        videomode_text = """
╭───────────────────▣
│❍ **ᴠɪᴅєσ ϻσᴅє ꜱᴇᴛᴛɪɴɢꜱ :**
├───────────────────▣
│
│📹 **sᴇʟᴇᴄᴛ ᴠɪᴅᴇᴏ ᴍᴏᴅᴇ:**
│
│❍ /vplay - ᴘʟᴀʏ ᴠɪᴅᴇᴏ
│❍ /cvplay - ᴄʜᴀɴɴᴇʟ ᴠɪᴅᴇᴏ
│
╰───────────────────▣
"""
        
        selected_image = random.choice(SETTINGS_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• 480ᴘ •", callback_data="video_480"),
                InlineKeyboardButton("• 720ᴘ •", callback_data="video_720")
            ],
            [
                InlineKeyboardButton("• 1080ᴘ •", callback_data="video_1080"),
                InlineKeyboardButton("• ʜᴅ •", callback_data="video_hd")
            ],
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=videomode_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Video Mode Settings", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading video mode settings", show_alert=True)


async def cleanmode_callback(client: Client, callback_query: CallbackQuery):
    """Handle clean mode settings"""
    try:
        if not await is_admin_check(callback_query):
            await callback_query.answer("❌ ᴛʜɪꜱ ᴘᴧηєʟ ɪꜱ ʀєꜱᴛʀɪᴄᴛєᴅ ᴛσ ᴧᴅϻɪηꜱ!", show_alert=True)
            return

        chat_id = callback_query.message.chat.id
        settings = await db_manager.get_chat_settings(chat_id)
        current_clean = settings.get("clean_mode", "enable")
        
        en_tick = " ✅" if current_clean == "enable" else ""
        dis_tick = " ✅" if current_clean == "disable" else ""

        cleanmode_text = f"""
╭───────────────────▣
│❍ **ᴄʟєᴧη ϻσᴅє ꜱᴇᴛᴛɪɴɢꜱ :**
├───────────────────▣
│
│🧹 **ᴄʟᴇᴀɴ ᴍᴏᴅᴇ sᴇᴛᴛɪɴɢs:**
│
│❍ **ᴇɴᴀʙʟᴇ**{en_tick}
│❍ **ᴅɪsᴀʙʟᴇ**{dis_tick}
│
╰───────────────────▣
"""
        
        selected_image = random.choice(SETTINGS_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"• ᴇɴᴀʙʟᴇ{en_tick} •", callback_data="clean_enable"),
                InlineKeyboardButton(f"• ᴅɪsᴀʙʟᴇ{dis_tick} •", callback_data="clean_disable")
            ],
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=cleanmode_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Clean Mode Settings", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading clean mode settings", show_alert=True)


async def logging_callback(client: Client, callback_query: CallbackQuery):
    """Handle logging settings"""
    try:
        if not await is_admin_check(callback_query):
            await callback_query.answer("❌ ᴛʜɪꜱ ᴘᴧηєʟ ɪꜱ ʀєꜱᴛʀɪᴄᴛєᴅ ᴛσ ᴧᴅϻɪηꜱ!", show_alert=True)
            return

        chat_id = callback_query.message.chat.id
        settings = await db_manager.get_chat_settings(chat_id)
        current_log = settings.get("logging", "enable")
        
        en_tick = " ✅" if current_log == "enable" else ""
        dis_tick = " ✅" if current_log == "disable" else ""

        logging_text = f"""
╭───────────────────▣
│❍ **ʟσɢɢɪηɢ ꜱᴇᴛᴛɪɴɢꜱ :**
├───────────────────▣
│
│📝 **ʟᴏɢɢɪɴɢ sᴇᴛᴛɪɴɢs:**
│
│❍ **ᴇɴᴀʙʟᴇ**{en_tick}
│❍ **ᴅɪsᴀʙʟᴇ**{dis_tick}
│
╰───────────────────▣
"""
        
        selected_image = random.choice(SETTINGS_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"• ᴇɴᴀʙʟᴇ{en_tick} •", callback_data="log_enable"),
                InlineKeyboardButton(f"• ᴅɪsᴀʙʟᴇ{dis_tick} •", callback_data="log_disable")
            ],
            [
                InlineKeyboardButton("⊶ ʙᴧᴄᴋ ⊶", callback_data="settings_main")
            ]
        ])
        
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=selected_image)
        )
        
        await callback_query.message.edit_caption(
            caption=logging_text,
            reply_markup=keyboard
        )
        
        await callback_query.answer("Logging Settings", show_alert=False)
        
    except Exception as e:
        await callback_query.answer("Error loading logging settings", show_alert=True)
