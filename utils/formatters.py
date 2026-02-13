"""
Message formatting utilities
Formats data for display in Telegram messages
"""
from typing import List, Optional
from database.models import Novel, Episode, Mapping, Link
from utils.constants import *


def format_links(links: List[Link]) -> str:
    """Format links for display"""
    if not links:
        return "  Chưa có link"
    
    result = []
    for link in links:
        result.append(f"  • {link.source_name}: {link.url}")
    
    return "\n".join(result)


def format_novel_info(novel: Novel) -> str:
    """Format novel chapter information"""
    title = f" - {novel.title}" if novel.title else ""
    
    result = [
        f"{EMOJI_BOOK} **Chương {novel.chapter_number}**{title}",
        "",
        f"{EMOJI_LINK} **Link đọc:**"
    ]
    
    if novel.links:
        for link in novel.links:
            result.append(f"  • [{link.source_name}]({link.url})")
    else:
        result.append("  Chưa có link")
    
    return "\n".join(result)


def format_episode_3d_info(episode: Episode) -> str:
    """Format 3D episode information"""
    title = f" - {episode.title}" if episode.title else ""
    
    result = [
        f"{EMOJI_FILM_3D} **Tiên Nghịch 3D - Tập {episode.episode_number}**{title}",
        "",
        f"{EMOJI_LINK} **Link xem:**"
    ]
    
    if episode.links:
        for link in episode.links:
            result.append(f"  • [{link.source_name}]({link.url})")
    else:
        result.append("  Chưa có link")
    
    return "\n".join(result)


def format_episode_2d_info(episode: Episode) -> str:
    """Format 2D episode information"""
    title = f" - {episode.title}" if episode.title else ""
    
    result = [
        f"{EMOJI_FILM_2D} **Tiên Nghịch 2D - Tập {episode.episode_number}**{title}",
        "",
        f"{EMOJI_LINK} **Link xem:**"
    ]
    
    if episode.links:
        for link in episode.links:
            result.append(f"  • [{link.source_name}]({link.url})")
    else:
        result.append("  Chưa có link")
    
    return "\n".join(result)


def format_search_result(
    novels: List[Novel],
    episodes_3d: List[Episode],
    episodes_2d: List[Episode],
    mappings: List[Mapping],
    search_type: str,
    search_value: int
) -> str:
    """
    Format comprehensive search result
    
    Args:
        novels: List of novel chapters
        episodes_3d: List of 3D episodes
        episodes_2d: List of 2D episodes
        mappings: List of mappings
        search_type: Type of search (chapter/3d/2d)
        search_value: Search value (chapter or episode number)
    """
    result = []
    
    # Header
    if search_type == SEARCH_TYPE_CHAPTER:
        result.append(f"{EMOJI_SEARCH} **Kết quả tra cứu: Chương {search_value}**")
    elif search_type == SEARCH_TYPE_3D:
        result.append(f"{EMOJI_SEARCH} **Kết quả tra cứu: Tiên Nghịch 3D - Tập {search_value}**")
    elif search_type == SEARCH_TYPE_2D:
        result.append(f"{EMOJI_SEARCH} **Kết quả tra cứu: Tiên Nghịch 2D - Tập {search_value}**")
    
    result.append("")
    result.append("─" * 30)
    result.append("")
    
    # 3D episodes
    if episodes_3d:
        result.append(f"{EMOJI_FILM_3D} **PHIM 3D**")
        result.append("")
        for episode in episodes_3d:
            title = f" - {episode.title}" if episode.title else ""
            result.append(f"**Tập {episode.episode_number}**{title}")
            if episode.links:
                result.append(f"{EMOJI_LINK} Link xem:")
                for link in episode.links:
                    result.append(f"  • [{link.source_name}]({link.url})")
            else:
                result.append("  • Chưa có link")
            result.append("")
    
    # 2D episodes
    if episodes_2d:
        result.append(f"{EMOJI_FILM_2D} **PHIM 2D**")
        result.append("")
        for episode in episodes_2d:
            title = f" - {episode.title}" if episode.title else ""
            result.append(f"**Tập {episode.episode_number}**{title}")
            if episode.links:
                result.append(f"{EMOJI_LINK} Link xem:")
                for link in episode.links:
                    result.append(f"  • [{link.source_name}]({link.url})")
            else:
                result.append("  • Chưa có link")
            result.append("")

    # Novel chapters
    if novels:
        result.append(f"{EMOJI_BOOK} **TIỂU THUYẾT**")
        result.append("")
        for novel in novels:
            title = f" - {novel.title}" if novel.title else ""
            result.append(f"**Chương {novel.chapter_number}**{title}")
            if novel.links:
                result.append(f"{EMOJI_LINK} Link đọc:")
                for link in novel.links:
                    result.append(f"  • [{link.source_name}]({link.url})")
            else:
                result.append("  • Chưa có link")
            result.append("")
    
    # If no results
    if not novels and not episodes_3d and not episodes_2d:
        result.append(f"{EMOJI_INFO} Không tìm thấy thông tin")
        result.append("")
        result.append("Bạn có thể đóng góp thông tin bằng lệnh /contribute")
    
    return "\n".join(result)


def format_contribution_for_admin(contribution) -> str:
    """Format contribution for admin review"""
    from datetime import datetime
    
    result = [
        f"{EMOJI_CONTRIBUTE} **ĐÓP GÓP MỚI CẦN DUYỆT**",
        "",
        f"**ID:** `{contribution._id}`",
        f"**Người gửi:** {contribution.username} (ID: {contribution.user_id})",
        f"**Loại:** {contribution.contribution_type}",
        f"**Thời gian:** {contribution.submitted_at.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "**Nội dung:**"
    ]
    
    data = contribution.data
    
    if contribution.contribution_type == CONTRIBUTION_TYPE_MAPPING:
        chapters = data.get('novel_chapters', [])
        ep_3d = data.get('episode_3d')
        ep_2d = data.get('episode_2d')
        
        result.append(f"  • Chương: {', '.join(map(str, chapters))}")
        if ep_3d:
            result.append(f"  • Tập 3D: {ep_3d}")
        if ep_2d:
            result.append(f"  • Tập 2D: {ep_2d}")
    
    elif contribution.contribution_type in [
        CONTRIBUTION_TYPE_NOVEL_LINK,
        CONTRIBUTION_TYPE_EPISODE_3D_LINK,
        CONTRIBUTION_TYPE_EPISODE_2D_LINK
    ]:
        target_type = data.get('target_type', '')
        target_number = data.get('target_number', 0)
        link = data.get('link', {})
        
        if target_type == TARGET_TYPE_NOVEL:
            result.append(f"  • Chương: {target_number}")
        elif target_type == TARGET_TYPE_EPISODE_3D:
            result.append(f"  • Tập 3D: {target_number}")
        elif target_type == TARGET_TYPE_EPISODE_2D:
            result.append(f"  • Tập 2D: {target_number}")
        
        result.append(f"  • Website: {link.get('source_name', '')}")
        result.append(f"  • URL: {link.get('url', '')}")
    
    return "\n".join(result)


def format_contribution_list(contributions: list) -> str:
    """Format list of pending contributions"""
    if not contributions:
        return f"{EMOJI_INFO} Không có đóng góp nào đang chờ duyệt"
    
    result = [
        f"{EMOJI_PENDING} **DANH SÁCH ĐÓNG GÓP CHỜ DUYỆT** ({len(contributions)})",
        ""
    ]
    
    for i, contrib in enumerate(contributions, 1):
        contrib_type_display = {
            CONTRIBUTION_TYPE_MAPPING: "Mapping",
            CONTRIBUTION_TYPE_NOVEL_LINK: "Link tiểu thuyết",
            CONTRIBUTION_TYPE_EPISODE_3D_LINK: "Link 3D",
            CONTRIBUTION_TYPE_EPISODE_2D_LINK: "Link 2D"
        }.get(contrib.contribution_type, contrib.contribution_type)
        
        result.append(f"**{i}.** `{contrib._id}`")
        result.append(f"   • Loại: {contrib_type_display}")
        result.append(f"   • Người gửi: {contrib.username}")
        result.append(f"   • Thời gian: {contrib.submitted_at.strftime('%Y-%m-%d %H:%M')}")
        result.append("")
    
    result.append("Sử dụng /review\\_<ID> để xem chi tiết")
    
    return "\n".join(result)
