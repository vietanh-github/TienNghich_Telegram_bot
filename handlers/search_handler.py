"""
Search handler
Handles search commands (/chapter, /3d, /2d)
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services import SearchService
from utils.formatters import format_search_result
from utils.validators import validate_chapter_number, validate_episode_number
from utils.constants import *


search_service = SearchService()


async def handle_search_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search navigation callbacks"""
    query = update.callback_query
    # await query.answer() # Answer later or let perform_search handle it? Better here.
    
    data = query.data
    parts = data.split('_')
    
    if len(parts) < 3:
        await query.answer()
        return
        
    search_type = parts[1] # chapter, 3d, 2d
    search_value_str = parts[2]
    
    try:
        search_value = int(search_value_str)
        
        # Update user mode to match navigation
        context.user_data['search_mode'] = search_type
        
        # determine function
        if search_type == 'chapter':
             await perform_search_chapter(update, context, search_value, is_callback=True)
        elif search_type == '3d':
             await perform_search_3d(update, context, search_value, is_callback=True)
        elif search_type == '2d':
             await perform_search_2d(update, context, search_value, is_callback=True)
             
    except ValueError:
        await query.answer("Tâm ma quấy nhiễu (Lỗi dữ liệu)")


# REFACTORED COMMANDS TO USE SHARED LOGIC

async def search_chapter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /chapter command"""
    if not context.args or len(context.args) == 0:
        await update.message.reply_text(f"{EMOJI_INFO} Xin đạo hữu cho biết số chương. Ví dụ: `/chapter 123`", parse_mode='Markdown')
        return
    
    chapter_str = context.args[0]
    is_valid, chapter_num, error_msg = validate_chapter_number(chapter_str)
    
    if not is_valid:
        await update.message.reply_text(f"{EMOJI_CROSS} {error_msg}", parse_mode='Markdown')
        return

    await perform_search_chapter(update, context, chapter_num, is_callback=False)


async def search_3d_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /3d command"""
    if not context.args or len(context.args) == 0:
        await update.message.reply_text(f"{EMOJI_INFO} Xin đạo hữu cho biết số tập. Ví dụ: `/3d 10`", parse_mode='Markdown')
        return
    
    episode_str = context.args[0]
    is_valid, episode_num, error_msg = validate_episode_number(episode_str)
    
    if not is_valid:
        await update.message.reply_text(f"{EMOJI_CROSS} {error_msg}", parse_mode='Markdown')
        return

    await perform_search_3d(update, context, episode_num, is_callback=False)


async def search_2d_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /2d command"""
    if not context.args or len(context.args) == 0:
        await update.message.reply_text(f"{EMOJI_INFO} Xin đạo hữu cho biết số tập. Ví dụ: `/2d 5`", parse_mode='Markdown')
        return
    
    episode_str = context.args[0]
    is_valid, episode_num, error_msg = validate_episode_number(episode_str)
    
    if not is_valid:
        await update.message.reply_text(f"{EMOJI_CROSS} {error_msg}", parse_mode='Markdown')
        return

    await perform_search_2d(update, context, episode_num, is_callback=False)



async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /list command"""
    await show_list_page(update, context, page=0)


async def handle_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle list pagination"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    try:
        page = int(data.split('_')[-1])
        await show_list_page(update, context, page=page, is_callback=True)
    except Exception as e:
        print(f"Error in list callback: {e}")


async def show_list_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0, is_callback: bool = False):
    """Show list page"""
    ITEMS_PER_PAGE = 10
    offset = page * ITEMS_PER_PAGE
    
    items = search_service.get_full_list(limit=ITEMS_PER_PAGE, offset=offset)
    
    if not items and page > 0:
        if is_callback:
            await update.callback_query.answer("Đã hết ngọc giản")
        return
        
    if not items and page == 0:
         msg = f"{EMOJI_INFO} Tàng Kinh Các hiện còn trống, chưa có ngọc giản nào."
         if is_callback:
             await update.callback_query.edit_message_text(msg)
         else:
             await update.message.reply_text(msg)
         return

    # Format list
    text = f"{EMOJI_BOOK} **DANH MỤC TÀNG KINH CÁC**\n"
    text += f"(Trang {page + 1})\n\n"
    
    for item in items:
        mapping = item["mapping"]
        ep_3d = item["episode_3d"]
        ep_2d = item["episode_2d"]
        novel = item["novel"]
        
        # Format 3D
        txt_3d = "--"
        if mapping.episode_3d:
            if ep_3d and ep_3d.links:
                # Use first link
                link = ep_3d.links[0]
                txt_3d = f"[{mapping.episode_3d}]({link.url})"
            else:
                txt_3d = f"{mapping.episode_3d}"
                
        # Format 2D
        txt_2d = "--"
        if mapping.episode_2d:
             if ep_2d and ep_2d.links:
                 link = ep_2d.links[0]
                 txt_2d = f"[{mapping.episode_2d}]({link.url})"
             else:
                 txt_2d = f"{mapping.episode_2d}"
        
        # Format Chapter
        txt_chap = "--"
        if mapping.novel_chapters:
            start = mapping.novel_chapters[0]
            end = mapping.novel_chapters[-1]
            chap_range = f"{start}" if start == end else f"{start}-{end}"
            
            if novel and novel.links:
                link = novel.links[0]
                txt_chap = f"[{chap_range}]({link.url})"
            else:
                txt_chap = f"{chap_range}"
        
        text += f"🎬 3D: {txt_3d} | 📺 2D: {txt_2d} | 📖: {txt_chap}\n"
        
    text += f"\n_Chọn ngọc giản để xem/đọc_"
    
    # Pagination
    keyboard = []
    nav_row = []
    
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Trước", callback_data=f"list_page_{page-1}"))
    
    # Check if there might be more (simple check: if we got full limit, likely more)
    # Better: items count == limit
    if len(items) == ITEMS_PER_PAGE:
        nav_row.append(InlineKeyboardButton("Sau ➡️", callback_data=f"list_page_{page+1}"))
        
    if nav_row:
        keyboard.append(nav_row)
        
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    if is_callback:
        try:
             await update.callback_query.edit_message_text(
                text,
                parse_mode='Markdown',
                disable_web_page_preview=True,
                reply_markup=reply_markup
             )
        except Exception: pass
    else:
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )


# CORE SEARCH LOGIC

async def perform_search_chapter(update: Update, context: ContextTypes.DEFAULT_TYPE, chapter_num: int, is_callback: bool):
    try:
        if not is_callback:
            await update.message.chat.send_action(action="typing")
        
        result = search_service.search_by_chapter(chapter_num)
        text = format_search_result(result["novels"], result["episodes_3d"], result["episodes_2d"], result["mappings"], result["search_type"], result["search_value"])
        
        keyboard = []
        row1 = []
        if result["episodes_3d"]:
            ep_num = result["episodes_3d"][0].episode_number
            row1.append(InlineKeyboardButton(f"🎬 Xem 3D tập {ep_num}", callback_data=f"nav_3d_{ep_num}"))
        if result["episodes_2d"]:
            ep_num = result["episodes_2d"][0].episode_number
            row1.append(InlineKeyboardButton(f"📺 Xem 2D tập {ep_num}", callback_data=f"nav_2d_{ep_num}"))
        if row1: keyboard.append(row1)
        
        row2 = []
        if chapter_num > 1:
            row2.append(InlineKeyboardButton("⬅️ Trước", callback_data=f"nav_chapter_{chapter_num - 1}"))
        row2.append(InlineKeyboardButton("Sau ➡️", callback_data=f"nav_chapter_{chapter_num + 1}"))
        keyboard.append(row2)
        
        if not result["novels"] and not result["episodes_3d"] and not result["episodes_2d"]:
            keyboard.append([InlineKeyboardButton("➕ Cống hiến ngay", callback_data="contribute")])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if is_callback:
            await update.callback_query.answer()
            # Only edit if content changed to avoid errors, but usually it changes
            try:
                await update.callback_query.edit_message_text(text, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=reply_markup)
            except Exception:
                pass # Message not modified
        else:
            await update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=reply_markup)
            
    except Exception as e:
        print(f"Error search chapter: {e}")
        if is_callback: await update.callback_query.answer("Tẩu hỏa nhập ma (Lỗi tra cứu)")


async def perform_search_3d(update: Update, context: ContextTypes.DEFAULT_TYPE, episode_num: int, is_callback: bool):
    try:
        if not is_callback:
            await update.message.chat.send_action(action="typing")
            
        result = search_service.search_by_episode_3d(episode_num)
        text = format_search_result(result["novels"], result["episodes_3d"], result["episodes_2d"], result["mappings"], result["search_type"], result["search_value"])
        
        keyboard = []
        row1 = []
        if result["episodes_2d"]:
            ep_num = result["episodes_2d"][0].episode_number
            row1.append(InlineKeyboardButton(f"📺 Xem 2D tập {ep_num}", callback_data=f"nav_2d_{ep_num}"))
        if result["novels"]:
             chap_num = result["novels"][0].chapter_number
             row1.append(InlineKeyboardButton(f"📖 Đọc chương {chap_num}", callback_data=f"nav_chapter_{chap_num}"))
        if row1: keyboard.append(row1)
        
        row2 = []
        if episode_num > 1:
            row2.append(InlineKeyboardButton("⬅️ Trước", callback_data=f"nav_3d_{episode_num - 1}"))
        row2.append(InlineKeyboardButton("Sau ➡️", callback_data=f"nav_3d_{episode_num + 1}"))
        keyboard.append(row2)
        
        if not result["novels"] and not result["episodes_3d"] and not result["episodes_2d"]:
            keyboard.append([InlineKeyboardButton("➕ Cống hiến ngay", callback_data="contribute")])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if is_callback:
            await update.callback_query.answer()
            try:
                await update.callback_query.edit_message_text(text, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=reply_markup)
            except Exception: pass
        else:
            await update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=reply_markup)
            
    except Exception as e:
        print(f"Error search 3d: {e}")
        if is_callback: await update.callback_query.answer("Tẩu hỏa nhập ma (Lỗi tra cứu)")


async def perform_search_2d(update: Update, context: ContextTypes.DEFAULT_TYPE, episode_num: int, is_callback: bool):
    try:
        if not is_callback:
            await update.message.chat.send_action(action="typing")
            
        result = search_service.search_by_episode_2d(episode_num)
        text = format_search_result(result["novels"], result["episodes_3d"], result["episodes_2d"], result["mappings"], result["search_type"], result["search_value"])
        
        keyboard = []
        row1 = []
        if result["episodes_3d"]:
            ep_num = result["episodes_3d"][0].episode_number
            row1.append(InlineKeyboardButton(f"🎬 Xem 3D tập {ep_num}", callback_data=f"nav_3d_{ep_num}"))
        if result["novels"]:
             chap_num = result["novels"][0].chapter_number
             row1.append(InlineKeyboardButton(f"📖 Đọc chương {chap_num}", callback_data=f"nav_chapter_{chap_num}"))
        if row1: keyboard.append(row1)
        
        row2 = []
        if episode_num > 1:
            row2.append(InlineKeyboardButton("⬅️ Trước", callback_data=f"nav_2d_{episode_num - 1}"))
        row2.append(InlineKeyboardButton("Sau ➡️", callback_data=f"nav_2d_{episode_num + 1}"))
        keyboard.append(row2)
        
        if not result["novels"] and not result["episodes_3d"] and not result["episodes_2d"]:
            keyboard.append([InlineKeyboardButton("➕ Cống hiến ngay", callback_data="contribute")])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if is_callback:
            await update.callback_query.answer()
            try:
                await update.callback_query.edit_message_text(text, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=reply_markup)
            except Exception: pass
        else:
            await update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=reply_markup)
            
    except Exception as e:
        print(f"Error search 2d: {e}")
        if is_callback: await update.callback_query.answer("Tẩu hỏa nhập ma (Lỗi tra cứu)")
