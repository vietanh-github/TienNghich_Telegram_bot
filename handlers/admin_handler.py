"""
Admin handler
Handles admin commands for reviewing contributions
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, filters, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler
from services import ContributionService, AdminService, UserService
from utils.formatters import format_contribution_for_admin, format_contribution_list
from utils.constants import *
from config.settings import settings


contribution_service = ContributionService()
admin_service = AdminService()
user_service = UserService()

# Conversation states
BROADCAST_ASK_CONTENT = 0
BROADCAST_CONFIRM = 1


async def admin_dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command - Show admin dashboard"""
    if not await admin_check(update, context):
        return

    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJI_ADMIN} Sổ Nam Tào", callback_data="admin_stats"),
            InlineKeyboardButton(f"{EMOJI_PENDING} Thẩm định", callback_data="admin_pending")
        ],
        [
            InlineKeyboardButton("📢 Truyền âm toàn server", callback_data="admin_broadcast_users")
        ],
        [
            InlineKeyboardButton("❌ Đóng", callback_data="admin_close")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"{EMOJI_ADMIN} **CHƯỞNG MÔN ĐẠI ĐIỆN**\n\nChọn chức năng:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_service.is_admin(user_id)


async def admin_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Check if user is admin and reply if not
    Returns True if admin, False otherwise
    """
    if not update.effective_user:
        return False
        
    if not is_admin(update.effective_user.id):
        # Silent ignore or reply? Silent is better for security
        return False
        
    return True


async def add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Add a new admin
    Usage: /add_admin <user_id>
    Restricted to Super Admin (settings.ADMIN_ID)
    """
    user_id = update.effective_user.id
    if user_id != settings.ADMIN_ID:
        await update.message.reply_text(f"{EMOJI_CROSS} Chỉ Super Admin mới có quyền thực hiện lệnh này.")
        return

    if not context.args or len(context.args) == 0:
        await update.message.reply_text(f"{EMOJI_INFO} Vui lòng cung cấp ID người dùng. Ví dụ: `/add_admin 123456789`", parse_mode='Markdown')
        return
    
    try:
        new_admin_id = int(context.args[0])
        
        # Verify user exists (optional, but good)
        user = user_service.user_repo.get_by_id(new_admin_id)
        if not user:
             await update.message.reply_text(f"{EMOJI_WARNING} User ID {new_admin_id} chưa từng tương tác với bot. Họ cần start bot trước.")
             return

        if user_service.set_admin_status(new_admin_id, True):
             await update.message.reply_text(f"{EMOJI_CHECK} Đã thêm user `{new_admin_id}` ({user.username}) làm Admin.", parse_mode='Markdown')
        else:
             await update.message.reply_text(f"{EMOJI_CROSS} Tâm ma quấy nhiễu khi thêm hộ pháp.")
             
    except ValueError:
        await update.message.reply_text(f"{EMOJI_CROSS} ID không hợp lệ.")


async def remove_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Remove an admin
    Usage: /remove_admin <user_id>
    Restricted to Super Admin
    """
    user_id = update.effective_user.id
    if user_id != settings.ADMIN_ID:
        await update.message.reply_text(f"{EMOJI_CROSS} Chỉ Super Admin mới có quyền thực hiện lệnh này.")
        return

    if not context.args or len(context.args) == 0:
        await update.message.reply_text(f"{EMOJI_INFO} Vui lòng cung cấp ID người dùng. Ví dụ: `/remove_admin 123456789`", parse_mode='Markdown')
        return
    
    try:
        target_id = int(context.args[0])
        
        if target_id == settings.ADMIN_ID:
            await update.message.reply_text(f"{EMOJI_CROSS} Không thể xóa Super Admin.")
            return
            
        if user_service.set_admin_status(target_id, False):
             await update.message.reply_text(f"{EMOJI_CHECK} Đã xóa quyền Admin của user `{target_id}`.", parse_mode='Markdown')
        else:
             await update.message.reply_text(f"{EMOJI_CROSS} Tâm ma quấy nhiễu khi xóa hộ pháp.")
             
    except ValueError:
        await update.message.reply_text(f"{EMOJI_CROSS} ID không hợp lệ.")






async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - Show database statistics"""
    if not await admin_check(update, context):
        return
    
    try:
        stats = admin_service.get_statistics()
        
        top_users = stats.get('top_contributors', [])
        leaderboard_text = ""
        if top_users:
            leaderboard_text = "\n🏆 **TOP ĐÓNG GÓP:**\n"
            for i, user in enumerate(top_users, 1):
                # Retrieve user exp
                user_obj = admin_service.user_repo.get_by_id(user.get('_id'))
                exp = user_obj.exp if user_obj else 0
                leaderboard_text += f"{i}. {user.get('username', 'Unknown')} - {user.get('count', 0)} lần ({exp} EXP)\n"
        
        message = f"""
{EMOJI_ADMIN} **THỐNG KÊ HỆ THỐNG**

📊 **Dữ liệu:**
{EMOJI_BOOK} **Tiểu thuyết:** {stats.get('total_novels', 0)} chương
{EMOJI_FILM_3D} **Phim 3D:** {stats.get('total_episodes_3d', 0)} tập
{EMOJI_FILM_2D} **Phim 2D:** {stats.get('total_episodes_2d', 0)} tập
{EMOJI_LINK} **Mappings:** {stats.get('total_mappings', 0)} liên kết
{EMOJI_PENDING} **Đóng góp chờ duyệt:** {stats.get('pending_contributions', 0)}

👥 **Người dùng:**
• Tổng số: {stats.get('total_users', 0)}
• Hôm nay: {stats.get('active_today', 0)}
• 7 ngày qua: {stats.get('active_week', 0)}
• 30 ngày qua: {stats.get('active_month', 0)}
{leaderboard_text}
"""
        
        await update.message.reply_text(
            message,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        print(f"Error in admin_stats_command: {e}")
        await update.message.reply_text(
            f"{EMOJI_CROSS} Tâm ma quấy nhiễu khi xem Sổ Nam Tào."
        )


async def admin_pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pending command - List pending contributions"""
    if not await admin_check(update, context):
        return
    
    try:
        contributions = contribution_service.get_pending_contributions()
        
        message = format_contribution_list(contributions)
        
        # Create buttons for list
        keyboard = []
        if contributions:
            # Chunk or limits? Let's show all for now, assuming logic handles formatting
            for i, contrib in enumerate(contributions, 1):
                row = [
                    InlineKeyboardButton(f"✅ #{i}", callback_data=f"approvelist_{contrib._id}"),
                    InlineKeyboardButton(f"❌ #{i}", callback_data=f"rejectlist_{contrib._id}")
                ]
                keyboard.append(row)
        
        # Add refresh/close buttons
        keyboard.append([
            InlineKeyboardButton("🔄 Làm mới", callback_data="admin_pending"),
            InlineKeyboardButton("❌ Đóng", callback_data="admin_close")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        print(f"Error in admin_pending_command: {e}")
        await update.message.reply_text(
            f"{EMOJI_CROSS} Tâm ma quấy nhiễu khi lấy danh sách cống hiến."
        )


async def admin_review_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /review_<id> command - Review a specific contribution"""
    if not await admin_check(update, context):
        return
    
    try:
        if not context.args or len(context.args) == 0:
            await update.message.reply_text(
                f"{EMOJI_INFO} Vui lòng cung cấp ID đóng góp.\n\n"
                f"Ví dụ: `/review_<ID>`",
                parse_mode='Markdown'
            )
            return
        
        contribution_id = context.args[0]
        contribution = contribution_service.get_contribution_by_id(contribution_id)
        
        if not contribution:
            await update.message.reply_text(
                f"{EMOJI_CROSS} Không tìm thấy đóng góp với ID: `{contribution_id}`",
                parse_mode='Markdown'
            )
            return
        
        message = format_contribution_for_admin(contribution)
        
        message = format_contribution_for_admin(contribution)
        
        # Create buttons
        keyboard = [
            [
                InlineKeyboardButton("✅ Duyệt", callback_data=f"approve_{contribution_id}"),
                InlineKeyboardButton("❌ Từ chối", callback_data=f"reject_{contribution_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        print(f"Error in admin_review_command: {e}")
        await update.message.reply_text(
            f"{EMOJI_CROSS} Tâm ma quấy nhiễu khi xem chi tiết."
        )


async def admin_approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /approve_<id> command - Approve a contribution"""
    if not await admin_check(update, context):
        return
    
    try:
        if not context.args or len(context.args) == 0:
            await update.message.reply_text(
                f"{EMOJI_INFO} Vui lòng cung cấp ID đóng góp.\n\n"
                f"Ví dụ: `/approve_<ID>`",
                parse_mode='Markdown'
            )
            return
        
        contribution_id = context.args[0]
        
        # Get contribution details first
        contribution = contribution_service.get_contribution_by_id(contribution_id)
        if not contribution:
            await update.message.reply_text(
                f"{EMOJI_CROSS} Không tìm thấy đóng góp với ID: `{contribution_id}`",
                parse_mode='Markdown'
            )
            return
        
        # Approve
        success, message = contribution_service.approve_contribution(
            contribution_id=contribution_id,
            admin_id=update.effective_user.id
        )
        
        await update.message.reply_text(
            f"{EMOJI_CHECK if success else EMOJI_CROSS} {message}"
        )
        
        # Notify the contributor
        if success:
            try:
                await context.bot.send_message(
                    chat_id=contribution.user_id,
                    text=f"{EMOJI_CHECK} Cống hiến của đạo hữu đã được chưởng môn phê duyệt!\n\n"
                         f"Đa tạ đạo hữu đã cống hiến cho tông môn! 🎉"
                )
            except Exception as e:
                print(f"Error notifying contributor: {e}")
        
    except Exception as e:
        print(f"Error in admin_approve_command: {e}")
        await update.message.reply_text(
            f"{EMOJI_CROSS} Tâm ma quấy nhiễu khi thẩm định."
        )


async def admin_reject_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reject_<id> command - Reject a contribution"""
    if not await admin_check(update, context):
        return
    
    try:
        if not context.args or len(context.args) == 0:
            await update.message.reply_text(
                f"{EMOJI_INFO} Vui lòng cung cấp ID đóng góp.\n\n"
                f"Ví dụ: `/reject_<ID>`",
                parse_mode='Markdown'
            )
            return
        
        contribution_id = context.args[0]
        
        # Get contribution details first
        contribution = contribution_service.get_contribution_by_id(contribution_id)
        if not contribution:
            await update.message.reply_text(
                f"{EMOJI_CROSS} Không tìm thấy đóng góp với ID: `{contribution_id}`",
                parse_mode='Markdown'
            )
            return
        
        # Reject
        success, message = contribution_service.reject_contribution(
            contribution_id=contribution_id,
            admin_id=update.effective_user.id
        )
        
        await update.message.reply_text(
            f"{EMOJI_CHECK if success else EMOJI_CROSS} {message}"
        )
        
        # Notify the contributor
        if success:
            try:
                await context.bot.send_message(
                    chat_id=contribution.user_id,
                    text=f"{EMOJI_CROSS} Cống hiến của đạo hữu đã bị từ chối.\n\n"
                         f"Xin đạo hữu kiểm tra lại manh mối và cống hiến lại nếu cần."
                )
            except Exception as e:
                print(f"Error notifying contributor: {e}")
        
    except Exception as e:
        print(f"Error in admin_reject_command: {e}")
        await update.message.reply_text(
            f"{EMOJI_CROSS} Tâm ma quấy nhiễu khi từ chối."
        )


async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin callback queries (approve/reject)"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.id):
        await query.edit_message_text(f"{EMOJI_CROSS} Đạo hữu không có quyền thực hiện hành động này.")
        return

    data = query.data
    
    # Handle dashboard callbacks
    if data == "admin_close":
        await query.message.delete()
        return
        
    if data == "admin_stats":
        stats = admin_service.get_statistics()
        top_users = stats.get('top_contributors', [])
        leaderboard_text = ""
        if top_users:
            leaderboard_text = "\n🏆 **TOP ĐÓNG GÓP:**\n"
            for i, user in enumerate(top_users, 1):
                # Retrieve user exp
                user_obj = admin_service.user_repo.get_by_id(user.get('_id'))
                exp = user_obj.exp if user_obj else 0
                leaderboard_text += f"{i}. {user.get('username', 'Unknown')} - {user.get('count', 0)} lần ({exp} EXP)\n"
                
        message = f"""
{EMOJI_ADMIN} **THỐNG KÊ HỆ THỐNG**

📊 **Dữ liệu:**
{EMOJI_BOOK} **Tiểu thuyết:** {stats.get('total_novels', 0)} chương
{EMOJI_FILM_3D} **Phim 3D:** {stats.get('total_episodes_3d', 0)} tập
{EMOJI_FILM_2D} **Phim 2D:** {stats.get('total_episodes_2d', 0)} tập
{EMOJI_LINK} **Mappings:** {stats.get('total_mappings', 0)} liên kết
{EMOJI_PENDING} **Đóng góp chờ duyệt:** {stats.get('pending_contributions', 0)}

👥 **Người dùng:**
• Tổng số: {stats.get('total_users', 0)}
• Hôm nay: {stats.get('active_today', 0)}
• 7 ngày qua: {stats.get('active_week', 0)}
• 30 ngày qua: {stats.get('active_month', 0)}
{leaderboard_text}
"""
        await query.edit_message_text(message, parse_mode='Markdown')
        return

    if data == "admin_pending":
        contributions = contribution_service.get_pending_contributions()
        message = format_contribution_list(contributions)
        
        # Create buttons for list
        keyboard = []
        if contributions:
            for i, contrib in enumerate(contributions, 1):
                row = [
                    InlineKeyboardButton(f"✅ #{i}", callback_data=f"approvelist_{contrib._id}"),
                    InlineKeyboardButton(f"❌ #{i}", callback_data=f"rejectlist_{contrib._id}")
                ]
                keyboard.append(row)
        
        # Add refresh/close buttons
        keyboard.append([
            InlineKeyboardButton("🔄 Làm mới", callback_data="admin_pending"),
            InlineKeyboardButton("❌ Đóng", callback_data="admin_close")
        ])
        
        await query.edit_message_text(
            message, 
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    
    if data == "admin_broadcast_users":
        await query.message.reply_text(
            f"{EMOJI_ADMIN} **TRUYỀN ÂM TOÀN SERVER**\n\n"
            f"Vui lòng nhập nội dung truyền âm (hoặc gửi /cancel để hủy):",
            parse_mode='Markdown'
        )
        return BROADCAST_ASK_CONTENT

    parts = data.split('_')
    action = parts[0]
    
    if action in ["approve", "reject", "approvelist", "rejectlist"]:
        contribution_id = parts[1]
    
    try:
        # Get contribution first to notify user
        contribution = contribution_service.get_contribution_by_id(contribution_id)
        
        if not contribution:
            if "list" in action:
                # If list action, just refresh list
                contributions = contribution_service.get_pending_contributions()
                message = format_contribution_list(contributions)
                
                # Rebuild keyboard
                keyboard = []
                for i, contrib in enumerate(contributions, 1):
                    row = [
                        InlineKeyboardButton(f"✅ #{i}", callback_data=f"approvelist_{contrib._id}"),
                        InlineKeyboardButton(f"❌ #{i}", callback_data=f"rejectlist_{contrib._id}")
                    ]
                    keyboard.append(row)
                keyboard.append([
                    InlineKeyboardButton("🔄 Làm mới", callback_data="admin_pending"),
                    InlineKeyboardButton("❌ Đóng", callback_data="admin_close")
                ])
                
                await query.edit_message_text(
                    f"{EMOJI_CROSS} Không tìm thấy đóng góp này (có thể đã được xử lý).\n\n{message}",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                await query.edit_message_text(f"{EMOJI_CROSS} Không tìm thấy đóng góp này.")
            return

        if action.startswith("approve"):
            success, message = contribution_service.approve_contribution(
                contribution_id=contribution_id,
                admin_id=update.effective_user.id
            )
            emoji = EMOJI_CHECK
            result_text = "✅ ĐÃ DUYỆT"
        else: # reject
            success, message = contribution_service.reject_contribution(
                contribution_id=contribution_id,
                admin_id=update.effective_user.id
            )
            emoji = EMOJI_CROSS
            result_text = "❌ ĐÃ TỪ CHỐI"
            
        if success:
            # Handle list update vs single view update
            if "list" in action:
                 # Refresh list
                contributions = contribution_service.get_pending_contributions()
                new_list_text = format_contribution_list(contributions)
                
                 # Rebuild keyboard
                keyboard = []
                for i, contrib in enumerate(contributions, 1):
                    row = [
                        InlineKeyboardButton(f"✅ #{i}", callback_data=f"approvelist_{contrib._id}"),
                        InlineKeyboardButton(f"❌ #{i}", callback_data=f"rejectlist_{contrib._id}")
                    ]
                    keyboard.append(row)
                keyboard.append([
                    InlineKeyboardButton("🔄 Làm mới", callback_data="admin_pending"),
                    InlineKeyboardButton("❌ Đóng", callback_data="admin_close")
                ])
                
                await query.edit_message_text(
                    text=f"{emoji} {result_text} đóng góp của {contribution.username}.\n\n{new_list_text}",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                # Single view update (existing logic)
                original_text = query.message.text_markdown
                new_text = f"{original_text}\n\n**TRẠNG THÁI:** {result_text}"
                await query.edit_message_text(
                    text=new_text,
                    parse_mode='Markdown'
                )
            
            # Notify user
            if action.startswith("approve"):
                notify_text = (f"{EMOJI_CHECK} Cống hiến của đạo hữu đã được chưởng môn phê duyệt!\n\n"
                               f"Đa tạ đạo hữu đã cống hiến cho tông môn! 🎉")
            else:
                notify_text = (f"{EMOJI_CROSS} Cống hiến của đạo hữu đã bị từ chối.\n\n"
                               f"Xin đạo hữu kiểm tra lại manh mối.")
                               
            try:
                await context.bot.send_message(
                    chat_id=contribution.user_id,
                    text=notify_text
                )
            except Exception as e:
                print(f"Error notifying contributor: {e}")
                
        else:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=f"{EMOJI_CROSS} {message}"
            )

    except Exception as e:
        print(f"Error in handle_admin_callback: {e}")
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"{EMOJI_CROSS} Tâm ma quấy nhiễu: {e}"
        )


async def admin_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /adminhelp command - Show admin help"""
    if not await admin_check(update, context):
        return
    
    help_message = f"""
{EMOJI_ADMIN} **HƯỚNG DẪN ADMIN**

**Xem thống kê:**
`/stats` - Xem thống kê tổng quan

**Quản lý đóng góp:**
`/pending` - Danh sách đóng góp chờ duyệt
`/review_<ID>` - Xem chi tiết đóng góp
`/approve_<ID>` - Duyệt đóng góp
`/reject_<ID>` - Từ chối đóng góp

**Lưu ý:**
• Thay `<ID>` bằng ID thực tế của đóng góp
• Khi có đóng góp mới, bot sẽ tự động thông báo
• Đạo hữu cống hiến sẽ nhận thông báo khi được duyệt/từ chối
"""
    
    await update.message.reply_text(
        help_message,
        parse_mode='Markdown'
    )


async def broadcast_ask_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask for broadcast content"""
    text = update.message.text
    context.user_data['broadcast_content'] = text
    
    # Get user count
    user_count = user_service.count_users()
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Gửi ngay", callback_data="broadcast_confirm"),
            InlineKeyboardButton("❌ Hủy bỏ", callback_data="broadcast_cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"📣 **XÁC NHẬN GỬI THÔNG BÁO**\n\n"
        f"**Số lượng người nhận:** {user_count} users\n\n"
        f"**Nội dung:**\n{text}\n\n"
        f"Bạn có chắc chắn muốn gửi không?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return BROADCAST_CONFIRM


async def broadcast_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute broadcast"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    
    if action == "broadcast_cancel":
        await query.edit_message_text(f"{EMOJI_CROSS} Đã hủy gửi thông báo.")
        context.user_data.clear()
        return ConversationHandler.END
        
    content = context.user_data.get('broadcast_content')
    if not content:
        await query.edit_message_text(f"{EMOJI_CROSS} Thất bại: Không tìm thấy nội dung.")
        return ConversationHandler.END
        
    # Start broadcasting
    await query.edit_message_text(f"⏳ Đang gửi thông báo... Vui lòng đợi.")
    
    users = user_service.get_all_users()
    success_count = 0
    fail_count = 0
    
    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user.user_id,
                text=f"{EMOJI_ADMIN} **TRUYỀN ÂM TỪ CHƯỞNG MÔN**\n\n{content}",
                parse_mode='Markdown'
            )
            success_count += 1
        except Exception as e:
            fail_count += 1
            print(f"Failed to send to {user.user_id}: {e}")
            
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"{EMOJI_CHECK} **KẾT QUẢ GỬI THÔNG BÁO**\n\n"
             f"✅ Thành công: {success_count}\n"
             f"❌ Thất bại: {fail_count}",
        parse_mode='Markdown'
    )
    
    context.user_data.clear()
    return ConversationHandler.END


async def broadcast_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel broadcast conversation"""
    await update.message.reply_text(f"{EMOJI_CROSS} Đã hủy thao tác.")
    context.user_data.clear()
    return ConversationHandler.END


# Broadcast Conversation Handler
broadcast_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(handle_admin_callback, pattern='^admin_broadcast_users$')],
    states={
        BROADCAST_ASK_CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_ask_content)],
        BROADCAST_CONFIRM: [CallbackQueryHandler(broadcast_confirm, pattern='^broadcast_(confirm|cancel)$')]
    },
    fallbacks=[CommandHandler("cancel", broadcast_cancel)]
)
