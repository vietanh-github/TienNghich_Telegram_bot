"""
Main entry point for Tien Nghich Telegram Bot
"""
import logging
import telegram
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, filters
from config.settings import settings
from database.connection import db_connection
from handlers import (
    start_command,
    help_command,
    search_chapter_command,
    search_3d_command,
    search_2d_command,
    handle_search_callback,
    list_command,
    handle_list_callback,
    contribution_conv_handler,
    admin_stats_command,
    admin_pending_command,
    admin_review_command,
    admin_approve_command,
    admin_reject_command,
    admin_reject_command,
    admin_help_command,
    handle_admin_callback,
    admin_dashboard_command,
    broadcast_conv_handler,
    add_admin_command,
    remove_admin_command,
    handle_help_callback,
    handle_start_callback

)


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def setup_handlers(application: Application):
    """Setup all command handlers"""
    
    # Basic commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(handle_help_callback, pattern="^help_"))
    application.add_handler(CallbackQueryHandler(handle_start_callback, pattern="^mode_"))
    
    # Search commands
    application.add_handler(CommandHandler("chapter", search_chapter_command))
    application.add_handler(CommandHandler("3d", search_3d_command))
    application.add_handler(CommandHandler("2d", search_2d_command))
    application.add_handler(CallbackQueryHandler(handle_search_callback, pattern="^nav_"))
    
    # List command
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CallbackQueryHandler(handle_list_callback, pattern="^list_page_"))
    
    # Contribution conversation handler (must be added before other handlers)
    application.add_handler(contribution_conv_handler)
    
    # Admin commands
    application.add_handler(CommandHandler("stats", admin_stats_command))
    application.add_handler(CommandHandler("pending", admin_pending_command))
    application.add_handler(CommandHandler("review", admin_review_command))
    application.add_handler(CommandHandler("review", admin_review_command))
    application.add_handler(CommandHandler("approve", admin_approve_command))
    application.add_handler(CommandHandler("reject", admin_reject_command))
    application.add_handler(CommandHandler("adminhelp", admin_help_command))
    application.add_handler(CommandHandler("add_admin", add_admin_command))
    application.add_handler(CommandHandler("remove_admin", remove_admin_command))
    
    # helper for admin dashboard
    application.add_handler(CommandHandler("admin", admin_dashboard_command))
    
    # Broadcast conversation handler (higher priority than callback)
    application.add_handler(broadcast_conv_handler)
    
    # Admin callback handler
    application.add_handler(CallbackQueryHandler(handle_admin_callback, pattern="^(approve|reject|admin|approvelist|rejectlist)_"))
    
    logger.info("✅ All handlers registered successfully")


async def post_init(application: Application):
    """Initialize after application starts"""
    logger.info("🚀 Bot is starting up...")
    
    # Set bot commands
    from telegram import BotCommand
    commands = [
        BotCommand("start", "Bắt đầu tu luyện"),
        BotCommand("chapter", "Dò xét chương truyện"),
        BotCommand("3d", "Dò xét Tiên Nghịch 3D"),
        BotCommand("2d", "Dò xét Tiên Nghịch 2D"),
        BotCommand("contribute", "Cống hiến hương hỏa"),
        BotCommand("list", "Danh mục Tàng Kinh Các"),
        BotCommand("help", "Bí kíp sử dụng")
    ]
    await application.bot.set_my_commands(commands)
    logger.info("✅ Bot commands menu set successfully")
    
    # Connect to database
    try:
        db_connection.connect()
        logger.info("✅ Database connected successfully")
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        raise
    
    # Send startup message to admin
    try:
        await application.bot.send_message(
            chat_id=settings.ADMIN_ID,
            text="🤖 Bot Tiên Nghịch đã khởi động thành công!"
        )
        logger.info(f"✅ Startup notification sent to admin (ID: {settings.ADMIN_ID})")
    except Exception as e:
        logger.warning(f"⚠️  Could not send startup notification to admin: {e}")


async def post_shutdown(application: Application):
    """Cleanup after application stops"""
    logger.info("🛑 Bot is shutting down...")
    
    # Close database connection
    try:
        db_connection.close()
        logger.info("✅ Database connection closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}")
    
    # Send shutdown message to admin
    # Note: Sending message here causes RuntimeError because HTTPX client is closed
    # try:
    #     await application.bot.send_message(
    #         chat_id=settings.ADMIN_ID,
    #         text="🛑 Bot Tiên Nghịch đã dừng hoạt động."
    #     )
    # except Exception as e:
    #     logger.warning(f"⚠️  Could not send shutdown notification to admin: {e}")


def main():
    """Main function to run the bot"""
    
    # Validate settings
    try:
        settings.validate()
        logger.info("✅ Settings validated successfully")
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        return
    
    # Create application
    logger.info("📦 Creating bot application...")
    application = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )
    
    # Setup handlers
    setup_handlers(application)
    
    # Register message handler for smart input
    from handlers.message_handler import message_handler
    application.add_handler(telegram.ext.MessageHandler(telegram.ext.filters.TEXT & ~telegram.ext.filters.COMMAND, message_handler))
    
    # Start bot
    logger.info("🚀 Starting bot polling...")
    logger.info(f"👨‍💼 Admin ID: {settings.ADMIN_ID}")
    logger.info(f"💾 Database: {settings.MONGODB_DATABASE}")
    
    application.run_polling(
        allowed_updates=["message", "callback_query"]
    )


if __name__ == '__main__':
    main()
