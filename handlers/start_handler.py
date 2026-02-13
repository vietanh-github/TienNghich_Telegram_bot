"""
Start handler
Handles /start command and welcome message
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from services import UserService
from utils.constants import *

user_service = UserService()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Track user
    if user:
        user_service.track_user(user)
    
    welcome_message = rf"""
Kính chào đạo hữu {user.mention_markdown_v2()}\! 👋

Chào mừng đạo hữu đến với **Tàng Kinh Các Tiên Nghịch** \- nơi lưu trữ ngọc giản và lưu ảnh về thế giới Tiên Nghịch

{EMOJI_BOOK} **Các pháp môn chính:**

*Dò xét thông tin:*
• `/chapter <số>` \- Tìm kiếm theo chương tiểu thuyết
• `/3d <số>` \- Tìm kiếm theo tập phim 3D
• `/2d <số>` \- Tìm kiếm theo tập phim 2D

*Cống hiến tông môn:*
• `/contribute` \- Đóng góp manh mối hoặc ngọc giản

*Pháp bảo khác:*
• `/help` \- Xem bí kíp hướng dẫn

{EMOJI_INFO} **Ví dụ:**
`/chapter 123` \- Tìm chương 123
`/3d 10` \- Tìm tập 3D số 10
`/2d 5` \- Tìm tập 2D số 5

Hãy bắt đầu con đường tu luyện\! 🚀
"""
    
    # Create inline keyboard
    keyboard = [
        [
            InlineKeyboardButton("📖 Tìm chương", callback_data="mode_chapter"),
            InlineKeyboardButton("🎬 Tìm 3D", callback_data="mode_3d")
        ],
        [
            InlineKeyboardButton("📺 Tìm 2D", callback_data="mode_2d"),
            InlineKeyboardButton("➕ Cống hiến", callback_data="contribute")
        ],
        [
            InlineKeyboardButton("ℹ️ Bí kíp", callback_data="help_main")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='MarkdownV2',
        reply_markup=reply_markup
    )


async def handle_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start menu callbacks (search modes)"""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "mode_chapter":
        context.user_data['search_mode'] = 'chapter'
        await query.edit_message_text(
            f"{EMOJI_BOOK} **DÒ XÉT TIỂU THUYẾT**\n\n"
            f"Vui lòng nhập số chương đạo hữu muốn tìm:\n"
            f"Ví dụ: `123`",
            parse_mode='Markdown'
        )
    
    elif data == "mode_3d":
        context.user_data['search_mode'] = '3d'
        await query.edit_message_text(
            f"{EMOJI_FILM_3D} **DÒ XÉT PHIM 3D**\n\n"
            f"Vui lòng nhập số tập đạo hữu muốn tìm:\n"
            f"Ví dụ: `10`",
            parse_mode='Markdown'
        )
        
    elif data == "mode_2d":
        context.user_data['search_mode'] = '2d'
        await query.edit_message_text(
            f"{EMOJI_FILM_2D} **DÒ XÉT PHIM 2D**\n\n"
            f"Vui lòng nhập số tập đạo hữu muốn tìm:\n"
            f"Ví dụ: `5`",
            parse_mode='Markdown'
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    text = f"""
{EMOJI_INFO} **BÍ KÍP SỬ DỤNG TÀNG KINH CÁC**

Chào mừng đạo hữu đến với Tàng Kinh Các Tiên Nghịch! Dưới đây là các pháp môn chính:

1️⃣ **Dò xét:** Tìm kiếm chương truyện, tập phim 3D/2D.
2️⃣ **Cống hiến:** Thêm manh mối hoặc ngọc giản mới.
3️⃣ **Truyền âm:** Liên hệ chưởng môn (admin).

Vui lòng chọn mục bên dưới để xem chi tiết:
"""
    keyboard = [
        [
            InlineKeyboardButton("🔍 Dò xét", callback_data="help_search"),
            InlineKeyboardButton("➕ Cống hiến", callback_data="help_contribute")
        ],
        [InlineKeyboardButton("📞 Truyền âm", callback_data="help_contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )


async def handle_help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help menu callbacks"""
    query = update.callback_query
    data = query.data
    
    if data == "help_main":
        await help_command(update, context)
        return

    back_button = [InlineKeyboardButton("🔙 Quay lại", callback_data="help_main")]
    
    if data == "help_search":
        text = f"""
{EMOJI_SEARCH} **BÍ KÍP DÒ XÉT**

*Dò xét theo chương tiểu thuyết:*
`/chapter <số chương>`
Ví dụ: `/chapter 123`

*Dò xét theo tập phim 3D:*
`/3d <số tập>`
Ví dụ: `/3d 10`

*Dò xét theo tập phim 2D:*
`/2d <số tập>`
Ví dụ: `/2d 5`

Bot sẽ hiển thị manh mối và ngọc giản nếu có.
"""
    elif data == "help_contribute":
        text = f"""
{EMOJI_CONTRIBUTE} **BÍ KÍP CỐNG HIẾN**

Sử dụng lệnh `/contribute` hoặc bấm nút **Cống hiến** để bắt đầu.

Đạo hữu có thể cống hiến:
• **Mối liên kết:** Liên kết giữa chương truyện và tập phim.
• **Ngọc giản/Lưu ảnh:** Thêm link đọc truyện hoặc xem phim.

Tất cả cống hiến sẽ được chưởng môn kiểm duyệt và đạo hữu sẽ nhận được **1 điểm công đức (EXP)** cho mỗi cống hiến được duyệt! 🌟
"""
    elif data == "help_contact":
        text = f"""
{EMOJI_INFO} **TRUYỀN ÂM & HỖ TRỢ**

Nếu đạo hữu gặp tẩu hỏa nhập ma (lỗi) hoặc có thắc mắc, vui lòng truyền âm cho chưởng môn.

• Bot version: 1.0.0
• Developed by: Antigravity
"""
    else:
        text = "Nội dung không tồn tại."

    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([back_button])
    )
