#!/usr/bin/env python3
"""
Telegram Music Bot - Main Entry Point
A full-featured music bot for Telegram voice chats
"""

import asyncio
import sys
import os
import logging
from core.bot import bot_app

# Configure logging - optimized for performance
logging.basicConfig(
    level=logging.INFO,  # Temporarily INFO for debugging
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def check_requirements():
    """Check if all required files and configurations are present"""
    
    # Check if session string is configured
    from config import SESSION_STRING
    if not SESSION_STRING:
        logger.error("❌ SESSION_STRING is not set in config.py!")
        logger.error("Please run session_generator.py first to generate a session string.")
        return False
    
    # Check if downloads directory exists
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    
    return True


async def main():
    """Main function to run the bot"""
    
    logger.info("=" * 50)
    logger.info("🎵 Telegram Music Bot")
    logger.info("=" * 50)
    
    # Check requirements
    if not check_requirements():
        logger.error("❌ Requirements check failed. Exiting...")
        sys.exit(1)
    
    try:
        # Run the bot
        await bot_app.run()
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("👋 Bot shutdown complete.")


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
