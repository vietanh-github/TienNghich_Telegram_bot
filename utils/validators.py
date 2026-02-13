"""
Input validation utilities
"""
import validators
from typing import Tuple, Optional


def validate_chapter_number(chapter_str: str) -> Tuple[bool, Optional[int], str]:
    """
    Validate chapter number input
    
    Returns:
        (is_valid, chapter_number, error_message)
    """
    try:
        chapter_num = int(chapter_str.strip())
        if chapter_num <= 0:
            return False, None, "Số chương phải lớn hơn 0"
        if chapter_num > 10000:
            return False, None, "Số chương không hợp lệ (quá lớn)"
        return True, chapter_num, ""
    except ValueError:
        return False, None, "Vui lòng nhập số chương hợp lệ"


def validate_episode_number(episode_str: str) -> Tuple[bool, Optional[int], str]:
    """
    Validate episode number input
    
    Returns:
        (is_valid, episode_number, error_message)
    """
    try:
        episode_num = int(episode_str.strip())
        if episode_num <= 0:
            return False, None, "Số tập phải lớn hơn 0"
        if episode_num > 10000:
            return False, None, "Số tập không hợp lệ (quá lớn)"
        return True, episode_num, ""
    except ValueError:
        return False, None, "Vui lòng nhập số tập hợp lệ"


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate URL format
    
    Returns:
        (is_valid, error_message)
    """
    url = url.strip()
    
    if not url:
        return False, "URL không được để trống"
    
    if not validators.url(url):
        return False, "URL không hợp lệ. Vui lòng nhập URL đầy đủ (bắt đầu bằng http:// hoặc https://)"
    
    return True, ""


def validate_source_name(source_name: str) -> Tuple[bool, str]:
    """
    Validate source name (website name)
    
    Returns:
        (is_valid, error_message)
    """
    source_name = source_name.strip()
    
    if not source_name:
        return False, "Tên website không được để trống"
    
    if len(source_name) < 2:
        return False, "Tên website phải có ít nhất 2 ký tự"
    
    if len(source_name) > 50:
        return False, "Tên website không được vượt quá 50 ký tự"
    
    return True, ""


def validate_chapter_list(chapters_str: str) -> Tuple[bool, Optional[list], str]:
    """
    Validate list of chapter numbers (comma-separated)
    Example: "121, 122, 123" or "121-123"
    
    Returns:
        (is_valid, chapter_list, error_message)
    """
    try:
        chapters_str = chapters_str.strip()
        
        # Check if it's a range (e.g., "121-123")
        if '-' in chapters_str:
            parts = chapters_str.split('-')
            if len(parts) != 2:
                return False, None, "Định dạng range không hợp lệ. Sử dụng: 121-123"
            
            start = int(parts[0].strip())
            end = int(parts[1].strip())
            
            if start > end:
                return False, None, "Số chương bắt đầu phải nhỏ hơn số chương kết thúc"
            
            if end - start > 100:
                return False, None, "Không được nhập quá 100 chương cùng lúc"
            
            chapters = list(range(start, end + 1))
        else:
            # Parse comma-separated list
            chapter_strs = chapters_str.split(',')
            chapters = []
            
            for ch_str in chapter_strs:
                ch_str = ch_str.strip()
                if not ch_str:
                    continue
                    
                is_valid, ch_num, error = validate_chapter_number(ch_str)
                if not is_valid:
                    return False, None, f"Chương '{ch_str}': {error}"
                
                if ch_num in chapters:
                    return False, None, f"Chương {ch_num} bị trùng lặp"
                
                chapters.append(ch_num)
        
        if not chapters:
            return False, None, "Danh sách chương không được để trống"
        
        if len(chapters) > 100:
            return False, None, "Không được nhập quá 100 chương cùng lúc"
        
        # Sort chapters
        chapters.sort()
        
        return True, chapters, ""
        
    except ValueError:
        return False, None, "Định dạng không hợp lệ. Sử dụng: '121, 122, 123' hoặc '121-123'"


def validate_title(title: str) -> Tuple[bool, str]:
    """
    Validate title
    
    Returns:
        (is_valid, error_message)
    """
    title = title.strip()
    
    if len(title) > 200:
        return False, "Tiêu đề không được vượt quá 200 ký tự"
    
    return True, ""
