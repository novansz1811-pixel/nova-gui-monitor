"""
DPI 感知工具 — v2 统一版

规则：所有外部接口统一使用物理坐标。
SetProcessDpiAwareness(2) 必须在进程最早期调用。
"""

import ctypes
import ctypes.wintypes as wintypes
import sys

_initialized = False
_dpi_scale = None


def init_dpi():
    """进程启动时调用一次，声明 Per-Monitor DPI Awareness。
    
    必须在任何 GUI / 截图库导入前调用。
    """
    global _initialized
    if _initialized:
        return
    try:
        # Per-Monitor DPI Aware V2 (Windows 10 1703+)
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            # 回退到 System DPI Aware
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass
    _initialized = True


# 别名：兼容 mcp_server.py 等使用旧名称的模块
init_dpi_awareness = init_dpi


def get_dpi_scale(monitor_index: int = 0) -> float:
    """获取 DPI 缩放比（1.0 = 100%, 1.5 = 150%, 1.75 = 175%）。
    
    使用 GetDeviceCaps 获取主屏 DPI。
    """
    global _dpi_scale
    if _dpi_scale is not None:
        return _dpi_scale
    try:
        hdc = ctypes.windll.user32.GetDC(0)
        dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
        ctypes.windll.user32.ReleaseDC(0, hdc)
        _dpi_scale = dpi / 96.0
    except Exception:
        _dpi_scale = 1.0
    return _dpi_scale


def get_screen_size() -> tuple[int, int]:
    """获取主屏物理像素尺寸。
    
    使用 GetSystemMetrics，DPI Aware 模式下返回真实物理像素。
    """
    w = ctypes.windll.user32.GetSystemMetrics(0)   # SM_CXSCREEN
    h = ctypes.windll.user32.GetSystemMetrics(1)   # SM_CYSCREEN
    return w, h


def get_virtual_screen_size() -> tuple[int, int, int, int]:
    """获取虚拟屏幕（多显示器合并）的范围。
    
    Returns:
        (x, y, width, height) — 虚拟屏幕左上角和总尺寸
    """
    x = ctypes.windll.user32.GetSystemMetrics(76)   # SM_XVIRTUALSCREEN
    y = ctypes.windll.user32.GetSystemMetrics(77)   # SM_YVIRTUALSCREEN
    w = ctypes.windll.user32.GetSystemMetrics(78)   # SM_CXVIRTUALSCREEN
    h = ctypes.windll.user32.GetSystemMetrics(79)   # SM_CYVIRTUALSCREEN
    return x, y, w, h


def get_cursor_pos() -> tuple[int, int]:
    """获取当前鼠标位置（物理坐标）。"""
    point = wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y
