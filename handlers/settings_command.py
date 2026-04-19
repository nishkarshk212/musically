"""
Settings Command Handler
Opens the settings panel
"""

from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatAction
from utils.decorators import admin_check
import random
import logging

logger = logging.getLogger(__name__)

from handlers.settings import get_settings_markup, SETTINGS_IMAGES
import random
import logging

logger = logging.getLogger(__name__)


@admin_check
async def settings_command(client: Client, message: Message):
    """Handle /settings command"""
    try:
        await message.reply_chat_action(ChatAction.UPLOAD_PHOTO)
        
        # Settings message text
        settings_text = """
╭───────────────────▣
│❍ **ʙᴏᴛ sᴇᴛᴛɪɴɢs ᴘᴀɴᴇʟ**
├───────────────────▣
│
│⚙️ **ᴄᴏɴꜰɪɢᴜʀᴇ ʏᴏᴜʀ ᴘʀᴇꜰᴇʀᴇɴᴄᴇs.**
│   **ᴄʟɪᴄᴋ ᴏɴ ʙᴜᴛᴛᴏɴs ᴛᴏ ᴛᴏɢɢʟᴇ.**
│
╰───────────────────▣
"""
        
        # Randomly select an image
        selected_image = random.choice(SETTINGS_IMAGES)
        
        # Get consistent markup from settings handler
        keyboard = await get_settings_markup(message.chat.id)
        
        # Send photo with caption and buttons
        await message.reply_photo(
            photo=selected_image,
            caption=settings_text,
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error in settings_command: {e}")
        await message.reply_text("❌ An error occurred while opening settings.")
