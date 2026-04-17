"""
Custom Decorators for Bot Handlers
"""

from functools import wraps
from pyrogram.types import Message
from config import OWNER_ID, SUDOERS
import logging
import time

logger = logging.getLogger(__name__)

# Cache for admin checks to reduce API calls
_admin_cache = {}
CACHE_TTL = 300  # 5 minutes cache


def admin_check(func):
    """Decorator to check if user is admin in the chat"""
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        try:
            # Check if it's a private message
            if message.chat.type == "private":
                return await func(client, message, *args, **kwargs)
            
            # Get user ID
            user_id = message.from_user.id
            chat_id = message.chat.id
            
            # Check if user is owner or sudoer
            if user_id in OWNER_ID or user_id in SUDOERS:
                return await func(client, message, *args, **kwargs)
            
            # Check cache first
            cache_key = f"{chat_id}:{user_id}"
            current_time = time.time()
            if cache_key in _admin_cache:
                cached_time, is_admin = _admin_cache[cache_key]
                if current_time - cached_time < CACHE_TTL:
                    if is_admin:
                        return await func(client, message, *args, **kwargs)
                    else:
                        await message.reply_text(
                            "❌ You need to be an admin to use this command!"
                        )
                        return
            
            # Get chat member status (API call)
            member = await message.chat.get_member(user_id)
            
            # Check if user is admin or creator
            # In Pyrogram 2.x, status is a string: 'administrator', 'creator', 'member', etc.
            is_admin = member.status in ['administrator', 'creator']
            
            # Update cache
            _admin_cache[cache_key] = (current_time, is_admin)
            
            if is_admin:
                return await func(client, message, *args, **kwargs)
            else:
                await message.reply_text(
                    "❌ You need to be an admin to use this command!"
                )
                return
                
        except Exception as e:
            logger.error(f"Admin check error: {e}")
            await message.reply_text("❌ An error occurred while checking permissions.")
            return
    
    return wrapper


def user_in_vc(func):
    """Decorator to check if user is in voice chat"""
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        try:
            # This is a simplified check - in production, you'd check actual VC membership
            # For now, we'll allow all users in group chats
            if message.chat.type in ["group", "supergroup"]:
                return await func(client, message, *args, **kwargs)
            else:
                await message.reply_text(
                    "❌ This command can only be used in group voice chats!"
                )
                return
        except Exception as e:
            logger.error(f"VC check error: {e}")
            await message.reply_text("❌ An error occurred.")
            return
    
    return wrapper


def bot_can_manage_vc(func):
    """Decorator to check if bot has voice chat permissions"""
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        try:
            # In groups, bot should be admin with appropriate permissions
            if message.chat.type in ["group", "supergroup"]:
                bot_member = await message.chat.get_member(client.me.id)
                
                # Bot should be admin
                # In Pyrogram 2.x, status is a string
                if bot_member.status not in ['administrator', 'creator']:
                    await message.reply_text(
                        "❌ I need to be an admin to manage voice chats!\n"
                        "Please promote me to admin with voice chat permissions."
                    )
                    return
            
            return await func(client, message, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Bot permission check error: {e}")
            await message.reply_text("❌ An error occurred while checking permissions.")
            return
    
    return wrapper


def sudo_only(func):
    """Decorator to restrict command to sudo users only"""
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        user_id = message.from_user.id
        
        if user_id in OWNER_ID or user_id in SUDOERS:
            return await func(client, message, *args, **kwargs)
        else:
            await message.reply_text(
                "❌ This command is restricted to authorized users only!"
            )
            return
    
    return wrapper


def owner_only(func):
    """Decorator to restrict command to owner only"""
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        user_id = message.from_user.id
        
        if user_id in OWNER_ID:
            return await func(client, message, *args, **kwargs)
        else:
            await message.reply_text(
                "❌ This command is restricted to the bot owner only!"
            )
            return
    
    return wrapper


def sudo_check(func):
    """Decorator to check if user is sudoer (alias for sudo_only)"""
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        user_id = message.from_user.id
        
        if user_id in OWNER_ID or user_id in SUDOERS:
            return await func(client, message, *args, **kwargs)
        else:
            await message.reply_text(
                "❌ This command is restricted to authorized users only!"
            )
            return
    
    return wrapper
