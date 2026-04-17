"""
Settings Panel Handler
Manages bot settings and configuration
"""

import random
from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import InputMediaPhoto

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


async def settings_callback(client: Client, callback_query: CallbackQuery):
    """Handle settings button callback"""
    try:
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
        playmode_text = """
╭───────────────────▣
│❍ **ᴘʟᴀʏ ϻσᴅє ꜱᴇᴛᴛɪɴɢꜱ :**
├───────────────────▣
│
│🎵 **ᴡʜᴏ ᴄᴀɴ ᴘʟᴀʏ sᴏɴɢs:**
│
│❍ **ᴇᴠᴇʀʏᴏɴᴇ** - ᴀɴʏᴏɴᴇ ᴄᴀɴ ᴘʟᴀʏ
│❍ **ᴀᴅᴍɪɴs** - ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴘʟᴀʏ
│❍ **ᴀᴜᴛʜ ᴜsᴇʀs** - ᴏɴʟʏ ᴀᴜᴛʜ ᴜsᴇʀs
│
╰───────────────────▣
"""
        
        selected_image = random.choice(SETTINGS_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• ᴇᴠᴇʀʏᴏɴᴇ •", callback_data="playmode_everyone"),
                InlineKeyboardButton("• ᴀᴅᴍɪɴs •", callback_data="playmode_admins")
            ],
            [
                InlineKeyboardButton("• ᴀᴜᴛʜ ᴜsᴇʀs •", callback_data="playmode_auth")
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
        skipmode_text = """
╭───────────────────▣
│❍ **ꜱᴋɪᴘ ϻσᴅє ꜱᴇᴛᴛɪɴɢꜱ :**
├───────────────────▣
│
│⏭️ **ᴡʜᴏ ᴄᴀɴ sᴋɪᴘ sᴏɴɢs:**
│
│❍ **ᴇᴠᴇʀʏᴏɴᴇ** - ᴀɴʏᴏɴᴇ ᴄᴀɴ sᴋɪᴘ
│❍ **ᴀᴅᴍɪɴs** - ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ sᴋɪᴘ
│❍ **ᴀᴜᴛʜ ᴜsᴇʀs** - ᴏɴʟʏ ᴀᴜᴛʜ ᴜsᴇʀs
│
╰───────────────────▣
"""
        
        selected_image = random.choice(SETTINGS_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• ᴇᴠᴇʀʏᴏɴᴇ •", callback_data="skipmode_everyone"),
                InlineKeyboardButton("• ᴀᴅᴍɪɴs •", callback_data="skipmode_admins")
            ],
            [
                InlineKeyboardButton("• ᴀᴜᴛʜ ᴜsᴇʀs •", callback_data="skipmode_auth")
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


async def quality_callback(client: Client, callback_query: CallbackQuery):
    """Handle quality settings"""
    try:
        quality_text = """
╭───────────────────▣
│❍ **ǫᴜᴀʟɪᴛʏ ꜱᴇᴛᴛɪɴɢꜱ :**
├───────────────────▣
│
│🎧 **sᴇʟᴇᴄᴛ ᴀᴜᴅɪᴏ ǫᴜᴀʟɪᴛʏ:**
│
│❍ /quality - ᴄʜᴀɴɢᴇ ᴀᴜᴅɪᴏ ǫᴜᴀʟɪᴛʏ
│   ʟᴇᴠᴇʟs: ʟᴏᴡ, ϻᴇᴅɪᴜϻ, ʜɪɢʜ
│
╰───────────────────▣
"""
        
        selected_image = random.choice(SETTINGS_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• ʟᴏᴡ •", callback_data="quality_low"),
                InlineKeyboardButton("• ϻᴇᴅɪᴜϻ •", callback_data="quality_medium")
            ],
            [
                InlineKeyboardButton("• ʜɪɢʜ •", callback_data="quality_high"),
                InlineKeyboardButton("• ꜱᴛᴜᴅɪᴏ •", callback_data="quality_studio")
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
        language_text = """
╭───────────────────▣
│❍ **ʟᴀηɢᴜᴀɢє ꜱᴇᴛᴛɪɴɢꜱ :**
├───────────────────▣
│
│🌐 **sᴇʟᴇᴄᴛ ʙᴏᴛ ʟᴀɴɢᴜᴀɢᴇ:**
│
│❍ /language - ᴄʜᴀɴɢᴇ ʟᴀɴɢᴜᴀɢᴇ
│   sᴜᴘᴘᴏʀᴛᴇᴅ: ᴇɴɢʟɪsʜ, ʜɪɴᴅɪ
│
╰───────────────────▣
"""
        
        selected_image = random.choice(SETTINGS_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• ᴇɴɢʟɪsʜ •", callback_data="lang_en"),
                InlineKeyboardButton("• ʜɪɴᴅɪ •", callback_data="lang_hi")
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
        volume_text = """
╭───────────────────▣
│❍ **ᴠσʟᴜϻє ꜱᴇᴛᴛɪɴɢꜱ :**
├───────────────────▣
│
│🔊 **sᴇᴛ ᴅᴇꜰᴀᴜʟᴛ ᴠᴏʟᴜᴍᴇ:**
│
│❍ /volume [1-200] - sᴇᴛ ᴠᴏʟᴜᴍᴇ
│   ᴅᴇꜰᴀᴜʟᴛ: 100
│
╰───────────────────▣
"""
        
        selected_image = random.choice(SETTINGS_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• 50% •", callback_data="vol_50"),
                InlineKeyboardButton("• 100% •", callback_data="vol_100")
            ],
            [
                InlineKeyboardButton("• 150% •", callback_data="vol_150"),
                InlineKeyboardButton("• 200% •", callback_data="vol_200")
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
        cleanmode_text = """
╭───────────────────▣
│❍ **ᴄʟєᴀη ϻσᴅє ꜱᴇᴛᴛɪɴɢꜱ :**
├───────────────────▣
│
│🧹 **ᴄʟᴇᴀɴ ᴍᴏᴅᴇ sᴇᴛᴛɪɴɢs:**
│
│❍ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ʙᴏᴛ ᴍᴇssᴀɢᴇs
│   ᴀғᴛᴇʀ ᴘʟᴀʏɪɴɢ sᴏɴɢs
│
╰───────────────────▣
"""
        
        selected_image = random.choice(SETTINGS_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• ᴇɴᴀʙʟᴇ •", callback_data="clean_enable"),
                InlineKeyboardButton("• ᴅɪsᴀʙʟᴇ •", callback_data="clean_disable")
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
        logging_text = """
╭───────────────────▣
│❍ **ʟσɢɢɪηɢ ꜱᴇᴛᴛɪɴɢꜱ :**
├───────────────────▣
│
│📝 **ʟᴏɢɢɪɴɢ sᴇᴛᴛɪɴɢs:**
│
│❍ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ʟᴏɢɢɪɴɢ
│   ɪɴ ʟᴏɢ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ
│
╰───────────────────▣
"""
        
        selected_image = random.choice(SETTINGS_IMAGES)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• ᴇɴᴀʙʟᴇ •", callback_data="log_enable"),
                InlineKeyboardButton("• ᴅɪsᴀʙʟᴇ •", callback_data="log_disable")
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
