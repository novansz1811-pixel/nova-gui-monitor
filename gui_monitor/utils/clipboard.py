"""
剪贴板工具 — 支持中文文本输入

通过 Win32 API 操作剪贴板，配合 Ctrl+V 粘贴实现中文输入。

v2: 修复 64 位 Python 上 ctypes 类型声明问题。
    所有 Win32 函数显式声明 argtypes/restype，
    防止指针/HANDLE 被截断为 32 位。
"""

import ctypes
import ctypes.wintypes as wintypes
import time
import logging

logger = logging.getLogger(__name__)

# Win32 剪贴板常量
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002

# ─── Win32 函数签名声明（64 位安全） ────────────────────────

_user32 = ctypes.windll.user32
_kernel32 = ctypes.windll.kernel32

# OpenClipboard(HWND) -> BOOL
_user32.OpenClipboard.argtypes = [wintypes.HWND]
_user32.OpenClipboard.restype = wintypes.BOOL

# CloseClipboard() -> BOOL
_user32.CloseClipboard.argtypes = []
_user32.CloseClipboard.restype = wintypes.BOOL

# EmptyClipboard() -> BOOL
_user32.EmptyClipboard.argtypes = []
_user32.EmptyClipboard.restype = wintypes.BOOL

# SetClipboardData(UINT, HANDLE) -> HANDLE
_user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
_user32.SetClipboardData.restype = wintypes.HANDLE

# GetClipboardData(UINT) -> HANDLE
_user32.GetClipboardData.argtypes = [wintypes.UINT]
_user32.GetClipboardData.restype = wintypes.HANDLE

# GlobalAlloc(UINT, SIZE_T) -> HGLOBAL
_kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
_kernel32.GlobalAlloc.restype = wintypes.HANDLE

# GlobalLock(HGLOBAL) -> LPVOID
_kernel32.GlobalLock.argtypes = [wintypes.HANDLE]
_kernel32.GlobalLock.restype = ctypes.c_void_p

# GlobalUnlock(HGLOBAL) -> BOOL
_kernel32.GlobalUnlock.argtypes = [wintypes.HANDLE]
_kernel32.GlobalUnlock.restype = wintypes.BOOL

# GlobalFree(HGLOBAL) -> HGLOBAL
_kernel32.GlobalFree.argtypes = [wintypes.HANDLE]
_kernel32.GlobalFree.restype = wintypes.HANDLE

# GetLastError
_kernel32.GetLastError.argtypes = []
_kernel32.GetLastError.restype = wintypes.DWORD


# ─── 剪贴板打开重试 ─────────────────────────────────────────

def _open_clipboard(max_retries: int = 5, retry_delay: float = 0.05) -> bool:
    """尝试打开剪贴板，带重试机制。
    
    其他程序可能短暂占用剪贴板（如剪贴板管理器、密码管理器），
    重试几次通常就能成功。
    """
    for attempt in range(max_retries):
        if _user32.OpenClipboard(None):
            return True
        err = _kernel32.GetLastError()
        logger.debug(f"OpenClipboard attempt {attempt+1}/{max_retries} failed (error={err})")
        time.sleep(retry_delay)
    
    err = _kernel32.GetLastError()
    logger.warning(f"OpenClipboard failed after {max_retries} attempts (last error={err})")
    return False


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
        if not _open_clipboard():
            logger.error("Failed to open clipboard for writing")
            return False
        
        try:
            # 清空剪贴板
            if not _user32.EmptyClipboard():
                logger.error(f"EmptyClipboard failed (error={_kernel32.GetLastError()})")
                return False
            
            # 编码为 UTF-16LE（Windows 内部编码）+ null terminator
            data = text.encode("utf-16-le") + b"\x00\x00"
            
            # 分配全局内存
            h_mem = _kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
            if not h_mem:
                logger.error(f"GlobalAlloc failed for {len(data)} bytes (error={_kernel32.GetLastError()})")
                return False
            
            # 锁定内存并复制数据
            p_mem = _kernel32.GlobalLock(h_mem)
            if not p_mem:
                logger.error(f"GlobalLock failed (error={_kernel32.GetLastError()})")
                _kernel32.GlobalFree(h_mem)
                return False
            
            ctypes.memmove(p_mem, data, len(data))
            _kernel32.GlobalUnlock(h_mem)
            
            # 设置剪贴板数据（系统接管 h_mem，不要手动 Free）
            result = _user32.SetClipboardData(CF_UNICODETEXT, h_mem)
            if not result:
                logger.error(f"SetClipboardData failed (error={_kernel32.GetLastError()})")
                _kernel32.GlobalFree(h_mem)
                return False
            
            return True
        finally:
            _user32.CloseClipboard()
    except Exception as e:
        logger.error(f"set_clipboard_text exception: {e}")
        return False


def get_clipboard_text() -> str:
    """从系统剪贴板读取文本。
    
    Returns:
        剪贴板文本，失败返回空字符串
    """
    try:
        if not _open_clipboard():
            logger.error("Failed to open clipboard for reading")
            return ""
        
        try:
            h_data = _user32.GetClipboardData(CF_UNICODETEXT)
            if not h_data:
                return ""
            
            p_data = _kernel32.GlobalLock(h_data)
            if not p_data:
                return ""
            
            try:
                text = ctypes.wstring_at(p_data)
                return text
            finally:
                _kernel32.GlobalUnlock(h_data)
        finally:
            _user32.CloseClipboard()
    except Exception as e:
        logger.error(f"get_clipboard_text exception: {e}")
        return ""
