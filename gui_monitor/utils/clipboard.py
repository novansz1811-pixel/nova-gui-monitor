"""
剪贴板工具 — 支持中文文本输入

通过 Win32 API 操作剪贴板，配合 Ctrl+V 粘贴实现中文输入。
"""

import ctypes
import ctypes.wintypes as wintypes
import time

# Win32 剪贴板常量
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002


def set_clipboard_text(text: str) -> bool:
    """将文本写入系统剪贴板。
    
    Args:
        text: 要写入的文本（支持中文）
    
    Returns:
        True 成功，False 失败
    """
    if not text:
        return False
    
    try:
        # 打开剪贴板
        if not ctypes.windll.user32.OpenClipboard(0):
            return False
        
        try:
            # 清空剪贴板
            ctypes.windll.user32.EmptyClipboard()
            
            # 编码为 UTF-16LE（Windows 内部编码）
            data = text.encode("utf-16-le") + b"\x00\x00"
            
            # 分配全局内存
            h_mem = ctypes.windll.kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
            if not h_mem:
                return False
            
            # 锁定内存并复制数据
            p_mem = ctypes.windll.kernel32.GlobalLock(h_mem)
            if not p_mem:
                ctypes.windll.kernel32.GlobalFree(h_mem)
                return False
            
            ctypes.memmove(p_mem, data, len(data))
            ctypes.windll.kernel32.GlobalUnlock(h_mem)
            
            # 设置剪贴板数据
            ctypes.windll.user32.SetClipboardData(CF_UNICODETEXT, h_mem)
            return True
        finally:
            ctypes.windll.user32.CloseClipboard()
    except Exception:
        return False


def get_clipboard_text() -> str:
    """从系统剪贴板读取文本。
    
    Returns:
        剪贴板文本，失败返回空字符串
    """
    try:
        if not ctypes.windll.user32.OpenClipboard(0):
            return ""
        
        try:
            h_data = ctypes.windll.user32.GetClipboardData(CF_UNICODETEXT)
            if not h_data:
                return ""
            
            p_data = ctypes.windll.kernel32.GlobalLock(h_data)
            if not p_data:
                return ""
            
            try:
                text = ctypes.wstring_at(p_data)
                return text
            finally:
                ctypes.windll.kernel32.GlobalUnlock(h_data)
        finally:
            ctypes.windll.user32.CloseClipboard()
    except Exception:
        return ""
