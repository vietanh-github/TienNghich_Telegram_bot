"""
Message handler
Handles text messages and smart input
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.ext import ContextTypes
from services import SearchService, UserService
from utils.constants import *


search_service = SearchService()
user_service = UserService()


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    
    # Track user
    if update.effective_user:
        user_service.track_user(update.effective_user)

    # Check if text is a number
    if text.isdigit():
        # Check search mode
        search_mode = context.user_data.get('search_mode', '3d')
        
        # Set args for command
        context.args = [text]
        
        if search_mode == '3d':
            from handlers.search_handler import search_3d_command
            await search_3d_command(update, context)
            # Reset mode? Maybe keep it for consecutive searches? Let's keep it for better UX.
        elif search_mode == '2d':
            from handlers.search_handler import search_2d_command
            await search_2d_command(update, context)
        else: # chapter
            from handlers.search_handler import search_chapter_command
            await search_chapter_command(update, context)
        return

    # If text starts with "tập" or "tap" followed by number
    lower_text = text.lower()
    if (lower_text.startswith("tập ") or lower_text.startswith("tap ")) and \
       lower_text.split(" ")[1].isdigit():
        episode_num = lower_text.split(" ")[1]
        
        # Ask user if they mean 3D or 2D
        keyboard = [
            [
                InlineKeyboardButton("🎬 Phim 3D", callback_data=f"nav_3d_{episode_num}"),
                InlineKeyboardButton("📺 Phim 2D", callback_data=f"nav_2d_{episode_num}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"{EMOJI_INFO} Bạn đang tìm tập {episode_num} phiên bản nào?",
            reply_markup=reply_markup
        )
        return

    # Default response for other text
    await update.message.reply_text(
        f"{EMOJI_INFO} Tôi không hiểu yêu cầu của bạn.\n\n"
        f"Gửi số để tìm chương/tập phim.\n"
        f"Bạn có thể chọn chế độ tra cứu từ menu /start.",
        parse_mode='Markdown'
    )
