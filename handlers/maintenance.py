"""
Maintenance Handler - Maintenance mode and logging
"""

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from database.mongodb import db_manager
from utils.decorators import owner_only
import logging

logger = logging.getLogger(__name__)


@owner_only
async def logs_command(client: Client, message: Message):
    """Get bot logs"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Send the log file
        if message.chat.type == 'private':
            await message.reply_document(
                document="bot.log",
                caption="📜 **Bot Logs**"
            )
        else:
            # Send in private chat for security
            await message.reply_text(
                "📜 Logs have been sent to your private chat."
            )
            # Try to send to user's PM
            try:
                await client.send_document(
                    chat_id=message.from_user.id,
                    document="bot.log",
                    caption="📜 **Bot Logs**"
                )
            except:
                pass
        
    except Exception as e:
        logger.error(f"Error in logs_command: {e}")
        await message.reply_text("❌ An error occurred while fetching logs.")


@owner_only
async def logger_command(client: Client, message: Message):
    """Toggle logging"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        if len(message.command) < 2:
            await message.reply_text(
                "❌ Please provide enable/disable.\n\n"
                "**Usage:** `/logger [enable/disable]`"
            )
            return
        
        action = message.command[1].lower()
        
        if action in ['enable', 'on']:
            await db_manager.set_setting('logging_enabled', True)
            await message.reply_text("✅ **Logging enabled!**")
        elif action in ['disable', 'off']:
            await db_manager.set_setting('logging_enabled', False)
            await message.reply_text("✅ **Logging disabled!**")
        else:
            await message.reply_text("❌ Invalid action. Use `enable` or `disable`.")
        
    except Exception as e:
        logger.error(f"Error in logger_command: {e}")
        await message.reply_text("❌ An error occurred while toggling logging.")


@owner_only
async def maintenance_command(client: Client, message: Message):
    """Toggle maintenance mode"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        if len(message.command) < 2:
            await message.reply_text(
                "❌ Please provide enable/disable.\n\n"
                "**Usage:** `/maintenance [enable/disable]`"
            )
            return
        
        action = message.command[1].lower()
        
        if action in ['enable', 'on']:
            await db_manager.set_setting('maintenance_mode', True)
            await message.reply_text(
                "⚠️ **Maintenance mode enabled!**\n\n"
                "The bot is now in maintenance mode.\n"
                "Only sudoers can use the bot."
            )
        elif action in ['disable', 'off']:
            await db_manager.set_setting('maintenance_mode', False)
            await message.reply_text(
                "✅ **Maintenance mode disabled!**\n\n"
                "The bot is now available for all users."
            )
        else:
            await message.reply_text("❌ Invalid action. Use `enable` or `disable`.")
        
    except Exception as e:
        logger.error(f"Error in maintenance_command: {e}")
        await message.reply_text("❌ An error occurred while toggling maintenance mode.")
