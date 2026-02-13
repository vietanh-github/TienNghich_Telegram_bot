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
Xin chào {user.mention_markdown_v2()}\! 👋

Chào mừng đến với **Bot Tiên Nghịch** \- nơi tra cứu thông tin về tác phẩm Tiên Nghịch \(Nhĩ Căn\)

{EMOJI_BOOK} **Chức năng chính:**

*Tra cứu thông tin:*
• `/chapter <số>` \- Tra cứu theo chương tiểu thuyết
• `/3d <số>` \- Tra cứu theo tập phim 3D
• `/2d <số>` \- Tra cứu theo tập phim 2D

*Đóng góp thông tin:*
• `/contribute` \- Đóng góp mapping hoặc link

*Khác:*
• `/help` \- Xem hướng dẫn chi tiết

{EMOJI_INFO} **Ví dụ:**
`/chapter 123` \- Tra chương 123
`/3d 10` \- Tra tập 3D số 10
`/2d 5` \- Tra tập 2D số 5

Hãy bắt đầu khám phá\! 🚀
"""
    
    # Create inline keyboard
    keyboard = [
        [
            InlineKeyboardButton("📖 Tra chương", callback_data="mode_chapter"),
            InlineKeyboardButton("🎬 Tra 3D", callback_data="mode_3d")
        ],
        [
            InlineKeyboardButton("📺 Tra 2D", callback_data="mode_2d"),
            InlineKeyboardButton("➕ Đóng góp", callback_data="contribute")
        ],
        [
            InlineKeyboardButton("ℹ️ Hướng dẫn", callback_data="help_main")
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
            f"{EMOJI_BOOK} **TRA CỨU TIỂU THUYẾT**\n\n"
            f"Vui lòng nhập số chương bạn muốn tìm:\n"
            f"Ví dụ: `123`",
            parse_mode='Markdown'
        )
    
    elif data == "mode_3d":
        context.user_data['search_mode'] = '3d'
        await query.edit_message_text(
            f"{EMOJI_FILM_3D} **TRA CỨU PHIM 3D**\n\n"
            f"Vui lòng nhập số tập bạn muốn tìm:\n"
            f"Ví dụ: `10`",
            parse_mode='Markdown'
        )
        
    elif data == "mode_2d":
        context.user_data['search_mode'] = '2d'
        await query.edit_message_text(
            f"{EMOJI_FILM_2D} **TRA CỨU PHIM 2D**\n\n"
            f"Vui lòng nhập số tập bạn muốn tìm:\n"
            f"Ví dụ: `5`",
            parse_mode='Markdown'
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    text = f"""
{EMOJI_INFO} **HƯỚNG DẪN SỬ DỤNG BOT TIÊN NGHỊCH**

Chào mừng bạn đến với Bot Tiên Nghịch! Dưới đây là các chức năng chính:

1️⃣ **Tra cứu:** Tìm kiếm chương truyện, tập phim 3D/2D.
2️⃣ **Đóng góp:** Thêm mapping hoặc link mới.
3️⃣ **Liên hệ:** Hỗ trợ từ admin.

Vui lòng chọn mục bên dưới để xem chi tiết:
"""
    keyboard = [
        [
            InlineKeyboardButton("🔍 Tra cứu", callback_data="help_search"),
            InlineKeyboardButton("➕ Đóng góp", callback_data="help_contribute")
        ],
        [InlineKeyboardButton("📞 Liên hệ", callback_data="help_contact")]
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
{EMOJI_SEARCH} **HƯỚNG DẪN TRA CỨU**

*Tra cứu theo chương tiểu thuyết:*
`/chapter <số chương>`
Ví dụ: `/chapter 123`

*Tra cứu theo tập phim 3D:*
`/3d <số tập>`
Ví dụ: `/3d 10`

*Tra cứu theo tập phim 2D:*
`/2d <số tập>`
Ví dụ: `/2d 5`

Bot sẽ hiển thị thông tin mapping và link nếu có.
"""
    elif data == "help_contribute":
        text = f"""
{EMOJI_CONTRIBUTE} **HƯỚNG DẪN ĐÓNG GÓP**

Sử dụng lệnh `/contribute` hoặc bấm nút **Đóng góp** để bắt đầu.

Bạn có thể đóng góp:
• **Mapping:** Liên kết giữa chương truyện và tập phim.
• **Link:** Thêm link đọc truyện hoặc xem phim.

Tất cả đóng góp sẽ được admin kiểm duyệt và bạn sẽ nhận được **1 EXP** cho mỗi đóng góp được duyệt! 🌟
"""
    elif data == "help_contact":
        text = f"""
{EMOJI_INFO} **LIÊN HỆ & HỖ TRỢ**

Nếu bạn gặp lỗi hoặc có thắc mắc, vui lòng liên hệ admin.

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
