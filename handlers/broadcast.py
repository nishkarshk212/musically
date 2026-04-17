"""
Broadcast Handler - Broadcast messages to served chats
"""

import asyncio
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from database.mongodb import db_manager
from utils.decorators import owner_only
import logging

logger = logging.getLogger(__name__)


@owner_only
async def broadcast_command(client: Client, message: Message):
    """Broadcast a message to served chats"""
    try:
        await message.reply_chat_action(ChatAction.TYPING)
        
        # Get the message to broadcast
        if message.reply_to_message:
            broadcast_msg = message.reply_to_message
        elif len(message.command) > 1:
            broadcast_msg = message.text.split(None, 1)[1]
        else:
            await message.reply_text(
                "❌ Please provide a message or reply to a message to broadcast.\n\n"
                "**Usage:** `/broadcast [message or reply to a message]`\n\n"
                "**Broadcasting Modes:**\n"
                "- `-pin` : Pins your broadcasted message in served chats.\n"
                "- `-pinloud` : Pins your broadcasted message with notification.\n"
                "- `-user` : Broadcasts to users who have started your bot.\n"
                "- `-assistant` : Broadcast from assistant account.\n"
                "- `-nobot` : Forces the bot to not broadcast the message."
            )
            return
        
        # Parse flags
        command_args = message.command[1:] if len(message.command) > 1 else []
        flags = {
            'pin': '-pin' in command_args,
            'pinloud': '-pinloud' in command_args,
            'user': '-user' in command_args,
            'assistant': '-assistant' in command_args,
            'nobot': '-nobot' in command_args
        }
        
        # Get all chats and users
        all_chats = await db_manager.get_all_chats()
        user_count = await db_manager.get_user_count()
        
        if not all_chats and user_count == 0:
            await message.reply_text(
                "❌ No chats or users found to broadcast to.\n\n"
                "The bot needs to be used in groups or by users first before broadcasting."
            )
            return
        
        # Combine chats and users for broadcasting
        # If -user flag is set, broadcast to users, otherwise to chats
        if flags['user']:
            # Broadcast to individual users who started the bot
            all_users = await db_manager.user_collection.find({}).to_list(length=None) if db_manager.user_collection else []
            broadcast_targets = all_users
            target_type = "users"
        else:
            # Broadcast to chats (groups/channels)
            broadcast_targets = all_chats
            target_type = "chats"
        
        if not broadcast_targets:
            await message.reply_text(f"❌ No {target_type} found to broadcast to.")
            return
        
        # Send broadcast message
        sent_count = 0
        failed_count = 0
        pinned_count = 0
        
        status_msg = await message.reply_text(
            f"📢 **Broadcasting to {target_type}...**\n\n"
            f"Total {target_type}: {len(broadcast_targets)}\n"
            f"Sent: 0 | Failed: 0"
        )
        
        for target in broadcast_targets:
            try:
                # Get chat_id or user_id depending on target type
                if flags['user']:
                    target_id = target.get('user_id')
                else:
                    target_id = target.get('chat_id')
                
                if not target_id:
                    failed_count += 1
                    continue
                
                # Send message
                if isinstance(broadcast_msg, str):
                    await client.send_message(target_id, broadcast_msg)
                else:
                    await broadcast_msg.copy(target_id)
                
                # Pin if requested
                if flags['pin'] or flags['pinloud']:
                    try:
                        last_message = await client.get_messages(target_id, limit=1)
                        await last_message.pin(disable_notification=not flags['pinloud'])
                        pinned_count += 1
                    except:
                        pass
                
                sent_count += 1
                
            except FloodWait as e:
                await asyncio.sleep(e.value)
                continue
            except UserIsBlocked:
                failed_count += 1
                continue
            except InputUserDeactivated:
                failed_count += 1
                continue
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send to {target_id}: {e}")
                continue
            
            # Update status every 10 messages
            if (sent_count + failed_count) % 10 == 0:
                try:
                    await status_msg.edit_text(
                        f"📢 **Broadcasting to {target_type}...**\n\n"
                        f"Total {target_type}: {len(broadcast_targets)}\n"
                        f"Sent: {sent_count} | Failed: {failed_count}"
                    )
                except:
                    pass
        
        # Final status
        await status_msg.edit_text(
            f"✅ **Broadcast Complete!**\n\n"
            f"📊 **Statistics:**\n"
            f"├ Total {target_type}: {len(broadcast_targets)}\n"
            f"├ Sent: {sent_count}\n"
            f"├ Failed: {failed_count}\n"
            f"└ Pinned: {pinned_count}"
        )
        
    except Exception as e:
        logger.error(f"Error in broadcast_command: {e}")
        await message.reply_text("❌ An error occurred during broadcast.")
