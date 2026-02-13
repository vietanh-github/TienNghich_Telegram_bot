"""
Contribute handler
Handles user contribution flow using ConversationHandler
"""
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from services import ContributionService
from utils.validators import *
from utils.constants import *
from config.settings import settings


# Conversation states
(CHOOSE_TYPE, MAPPING_CHAPTERS, MAPPING_EP_3D, MAPPING_EP_2D,
 LINK_TYPE, LINK_NUMBER, LINK_SOURCE, LINK_URL) = range(8)

contribution_service = ContributionService()


async def contribute_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start contribution conversation"""
    keyboard = [
        [InlineKeyboardButton("🔗 Mapping (Chương - Tập)", callback_data="contrib_mapping")],
        [InlineKeyboardButton("📖 Link đọc truyện", callback_data="contrib_novel")],
        [
            InlineKeyboardButton("🎬 Link 3D", callback_data="contrib_3d"),
            InlineKeyboardButton("📺 Link 2D", callback_data="contrib_2d")
        ],
        [InlineKeyboardButton("❌ Hủy", callback_data="contrib_cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if update is from callback (e.g. from main menu or search result)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            f"{EMOJI_CONTRIBUTE} **ĐÓNG GÓP THÔNG TIN**\n\n"
            f"Bạn muốn đóng góp loại thông tin nào?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"{EMOJI_CONTRIBUTE} **ĐÓNG GÓP THÔNG TIN**\n\n"
            f"Bạn muốn đóng góp loại thông tin nào?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    return CHOOSE_TYPE


async def choose_contribution_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle contribution type selection"""
    query = update.callback_query
    await query.answer()
    choice = query.data
    
    if choice == "contrib_cancel":
        await query.edit_message_text(f"{EMOJI_INFO} Đã hủy đóng góp.")
        context.user_data.clear()
        return ConversationHandler.END
    
    elif choice == "contrib_mapping":
        context.user_data['contribution_type'] = 'mapping'
        
        keyboard = [["Bỏ qua", "Hủy"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

        await query.message.reply_text( # use message.reply_text because we need a ReplyKeyboard
            f"{EMOJI_FILM_3D} **MAPPING: LIÊN KẾT CHƯƠNG - TẬP PHIM**\n\n"
            f"Nhập số tập 3D muốn đóng góp:\n\n"
            f"Hoặc chọn 'Bỏ qua' nếu không có tập 3D.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        # We need to answer the query but we can't edit it to show a ReplyKeyboard easily with text input needed next?
        # Actually, best practice for mixing callback and replykeyboard:
        # Delete the inline menu message, or just send a new message.
        # Let's delete the inline menu to clean up? Or just leave it.
        # The prompt above uses query.edit_message_text which supports Inline but NOT ReplyKeyboard (ReplyKeyboard is for user input).
        # So we MUST send a new message.
        # Let's clean up the previous menu if possible or just let it be.
        try:
             await query.delete_message()
        except:
             pass

        return MAPPING_EP_3D
    
    elif choice == "contrib_novel":
        context.user_data['contribution_type'] = 'novel_link'
        context.user_data['target_type'] = TARGET_TYPE_NOVEL
        await query.edit_message_text(
            f"{EMOJI_BOOK} **LINK ĐỌC TRUYỆN**\n\n"
            f"Nhập số chương muốn thêm link:\n\n"
            f"Ví dụ: `123`\n\n"
            f"Gửi `/cancel` để hủy.",
            parse_mode='Markdown'
        )
        return LINK_NUMBER
    
    elif choice == "contrib_3d":
        context.user_data['contribution_type'] = '3d_link'
        context.user_data['target_type'] = TARGET_TYPE_EPISODE_3D
        await query.edit_message_text(
            f"{EMOJI_FILM_3D} **LINK XEM PHIM 3D**\n\n"
            f"Nhập số tập 3D muốn thêm link:\n\n"
            f"Ví dụ: `10`\n\n"
            f"Gửi `/cancel` để hủy.",
            parse_mode='Markdown'
        )
        return LINK_NUMBER
    
    elif choice == "contrib_2d":
        context.user_data['contribution_type'] = '2d_link'
        context.user_data['target_type'] = TARGET_TYPE_EPISODE_2D
        await query.edit_message_text(
            f"{EMOJI_FILM_2D} **LINK XEM PHIM 2D**\n\n"
            f"Nhập số tập 2D muốn thêm link:\n\n"
            f"Ví dụ: `5`\n\n"
            f"Gửi `/cancel` để hủy.",
            parse_mode='Markdown'
        )
        return LINK_NUMBER
    
    else:
        await query.edit_message_text(
            f"{EMOJI_CROSS} Lựa chọn không hợp lệ."
        )
        return ConversationHandler.END


# MAPPING FLOW

async def mapping_get_3d(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get 3D episode for mapping (Step 1)"""
    text = update.message.text.strip()
    
    if text.lower() in ["hủy", "huy", "/cancel"]:
        await cancel_contribution(update, context)
        return ConversationHandler.END
    
    if text.lower() == "bỏ qua":
        context.user_data['episode_3d'] = None
    else:
        is_valid, episode_num, error_msg = validate_episode_number(text)
        
        if not is_valid:
            await update.message.reply_text(
                f"{EMOJI_CROSS} {error_msg}\n\nVui lòng nhập lại số tập 3D:"
            )
            return MAPPING_EP_3D
        
        context.user_data['episode_3d'] = episode_num
    
    keyboard = [["Bỏ qua", "Hủy"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"{EMOJI_BOOK} Nhập các chương truyện tương ứng (nếu có):\n\n"
        f"*Cách nhập:*\n"
        f"• Nhiều chương: `121, 122, 123`\n"
        f"• Hoặc range: `121-123`\n\n"
        f"Chọn 'Bỏ qua' nếu không muốn nhập chương.",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
    return MAPPING_CHAPTERS


async def mapping_get_chapters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get novel chapters for mapping (Step 2)"""
    text = update.message.text.strip()
    
    if text.lower() in ["hủy", "huy", "/cancel"]:
        await cancel_contribution(update, context)
        return ConversationHandler.END
    
    if text.lower() == "bỏ qua":
        context.user_data['chapters'] = []
    else:
        # Validate
        is_valid, chapters, error_msg = validate_chapter_list(text)
        
        if not is_valid:
            await update.message.reply_text(
                f"{EMOJI_CROSS} {error_msg}\n\nVui lòng nhập lại chương truyện:"
            )
            return MAPPING_CHAPTERS
        
        context.user_data['chapters'] = chapters
    
    keyboard = [["Bỏ qua", "Hủy"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"{EMOJI_FILM_2D} Nhập số tập 2D tương ứng:\n\n"
        f"Hoặc chọn 'Bỏ qua' nếu không có tập 2D.",
        reply_markup=reply_markup
    )
    
    return MAPPING_EP_2D


async def mapping_get_2d(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get 2D episode for mapping and submit (Step 3)"""
    text = update.message.text.strip()
    
    if text.lower() in ["hủy", "huy", "/cancel"]:
        await cancel_contribution(update, context)
        return ConversationHandler.END
    
    if text.lower() == "bỏ qua":
        context.user_data['episode_2d'] = None
    else:
        is_valid, episode_num, error_msg = validate_episode_number(text)
        
        if not is_valid:
            await update.message.reply_text(
                f"{EMOJI_CROSS} {error_msg}\n\nVui lòng nhập lại số tập 2D:"
            )
            return MAPPING_EP_2D
        
        context.user_data['episode_2d'] = episode_num
    
    # Check if empty (handled by service but good to check here too relevant to user feedback)
    episode_3d = context.user_data.get('episode_3d')
    episode_2d = context.user_data.get('episode_2d')
    chapters = context.user_data.get('chapters', [])

    if not episode_3d and not episode_2d:
         await update.message.reply_text(
            f"{EMOJI_CROSS} Lỗi: Phải có ít nhất một tập phim (3D hoặc 2D).\n"
            f"Vui lòng đóng góp lại.",
            reply_markup=ReplyKeyboardRemove()
        )
         context.user_data.clear()
         return ConversationHandler.END

    # Submit contribution
    user = update.effective_user
    username = f"@{user.username}" if user.username else user.first_name
    
    success, message, contribution = contribution_service.submit_mapping_contribution(
        user_id=user.id,
        username=username,
        novel_chapters=chapters,
        episode_3d=episode_3d,
        episode_2d=episode_2d
    )
    
    await update.message.reply_text(
        f"{EMOJI_CHECK if success else EMOJI_CROSS} {message}",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Notify admin if successful
    if success and contribution:
        await notify_admin_new_contribution(context, contribution)
    
    # Clear user data
    context.user_data.clear()
    
    return ConversationHandler.END


# LINK FLOW

async def link_get_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get chapter/episode number for link contribution"""
    text = update.message.text.strip()
    
    target_type = context.user_data.get('target_type')
    
    # Validate based on target type
    if target_type == TARGET_TYPE_NOVEL:
        is_valid, number, error_msg = validate_chapter_number(text)
    else:
        is_valid, number, error_msg = validate_episode_number(text)
    
    if not is_valid:
        await update.message.reply_text(
            f"{EMOJI_CROSS} {error_msg}\n\nVui lòng nhập lại:"
        )
        return LINK_NUMBER
    
    context.user_data['target_number'] = number
    
    keyboard = [["Hủy"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"{EMOJI_LINK} Nhập tên website:\n\n"
        f"Ví dụ: `TruyenFull`, `YouTube`, `Bilibili`",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return LINK_SOURCE


async def link_get_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get source name for link"""
    text = update.message.text.strip()
    
    if text == "Hủy":
        await update.message.reply_text(
            f"{EMOJI_INFO} Đã hủy đóng góp.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    is_valid, error_msg = validate_source_name(text)
    
    if not is_valid:
        await update.message.reply_text(
            f"{EMOJI_CROSS} {error_msg}\n\nVui lòng nhập lại:"
        )
        return LINK_SOURCE
    
    context.user_data['source_name'] = text
    
    await update.message.reply_text(
        f"{EMOJI_LINK} Nhập URL (link đầy đủ):\n\n"
        f"Ví dụ: `https://truyenfull.vn/...`",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='Markdown'
    )
    
    return LINK_URL


async def link_get_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get URL and submit link contribution"""
    url = update.message.text.strip()
    
    if url.lower() in ["hủy", "huy", "/cancel"]:
        await cancel_contribution(update, context)
        return ConversationHandler.END
    
    is_valid, error_msg = validate_url(url)
    
    if not is_valid:
        await update.message.reply_text(
            f"{EMOJI_CROSS} {error_msg}\n\nVui lòng nhập lại:"
        )
        return LINK_URL
    
    # Submit contribution
    user = update.effective_user
    username = f"@{user.username}" if user.username else user.first_name
    
    success, message, contribution = contribution_service.submit_link_contribution(
        user_id=user.id,
        username=username,
        target_type=context.user_data['target_type'],
        target_number=context.user_data['target_number'],
        source_name=context.user_data['source_name'],
        url=url
    )
    
    await update.message.reply_text(
        f"{EMOJI_CHECK if success else EMOJI_CROSS} {message}"
    )
    
    # Notify admin if successful
    if success and contribution:
        await notify_admin_new_contribution(context, contribution)
    
    # Clear user data
    context.user_data.clear()
    
    return ConversationHandler.END


async def cancel_contribution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel contribution conversation"""
    context.user_data.clear()
    
    await update.message.reply_text(
        f"{EMOJI_INFO} Đã hủy đóng góp.",
        reply_markup=ReplyKeyboardRemove()
    )
    
    return ConversationHandler.END


async def notify_admin_new_contribution(context: ContextTypes.DEFAULT_TYPE, contribution):
    """Notify admin about new contribution"""
    try:
        from utils.formatters import format_contribution_for_admin
        
        message = format_contribution_for_admin(contribution)
        
        await context.bot.send_message(
            chat_id=settings.ADMIN_ID,
            text=message,
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Error notifying admin: {e}")


from telegram.ext import CallbackQueryHandler

# Create conversation handler
contribution_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('contribute', contribute_start),
        CallbackQueryHandler(contribute_start, pattern='^contribute$')
    ],
    states={
        CHOOSE_TYPE: [
            CallbackQueryHandler(choose_contribution_type, pattern='^contrib_')
        ],
        MAPPING_CHAPTERS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, mapping_get_chapters)
        ],
        MAPPING_EP_3D: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, mapping_get_3d)
        ],
        MAPPING_EP_2D: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, mapping_get_2d)
        ],
        LINK_NUMBER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, link_get_number)
        ],
        LINK_SOURCE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, link_get_source)
        ],
        LINK_URL: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, link_get_url)
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel_contribution)],
)
