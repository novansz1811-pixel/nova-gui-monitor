"""
窗口管理模块 — 枚举、查找、聚焦、移动窗口

使用 Win32 API，不依赖 pygetwindow。
"""

import ctypes
import ctypes.wintypes as wintypes
import time
import re
from typing import Optional


# ─── 类型定义 ──────────────────────────────────────────────

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

# ShowWindow 常量
SW_RESTORE = 9
SW_SHOW = 5
SW_MINIMIZE = 6
SW_MAXIMIZE = 3

# GetWindowLong 常量
GWL_STYLE = -16
GWL_EXSTYLE = -20
WS_VISIBLE = 0x10000000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000


# ─── 窗口信息 ──────────────────────────────────────────────

def _get_window_title(hwnd: int) -> str:
    """获取窗口标题。"""
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    if length == 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value


def _get_window_rect(hwnd: int) -> tuple[int, int, int, int]:
    """获取窗口矩形（物理坐标）。"""
    rect = wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top


def _get_class_name(hwnd: int) -> str:
    """获取窗口类名。"""
    buf = ctypes.create_unicode_buffer(256)
    ctypes.windll.user32.GetClassNameW(hwnd, buf, 256)
    return buf.value


def _get_process_id(hwnd: int) -> int:
    """获取窗口对应的进程 ID。"""
    pid = wintypes.DWORD()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def _is_real_window(hwnd: int) -> bool:
    """判断是否为真实的应用窗口（排除工具窗口等）。"""
    if not ctypes.windll.user32.IsWindowVisible(hwnd):
        return False
    
    title = _get_window_title(hwnd)
    if not title:
        return False
    
    # 排除一些系统窗口
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
    ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    
    # 排除工具窗口（除非它有 APPWINDOW 样式）
    if (ex_style & WS_EX_TOOLWINDOW) and not (ex_style & WS_EX_APPWINDOW):
        return False
    
    return True


# ─── 公共 API ──────────────────────────────────────────────

def list_windows(include_all: bool = False) -> list[dict]:
    """枚举所有可见窗口。
    
    Args:
        include_all: True = 包含所有可见窗口，False = 仅真实应用窗口
    
    Returns:
        窗口信息列表 [{"hwnd", "title", "class", "pid", "x", "y", "width", "height"}, ...]
    """
    windows = []
    
    def callback(hwnd, _):
        if include_all:
            if not ctypes.windll.user32.IsWindowVisible(hwnd):
                return True
            title = _get_window_title(hwnd)
            if not title:
                return True
        else:
            if not _is_real_window(hwnd):
                return True
            title = _get_window_title(hwnd)
        
        x, y, w, h = _get_window_rect(hwnd)
        windows.append({
            "hwnd": hwnd,
            "title": title,
            "class": _get_class_name(hwnd),
            "pid": _get_process_id(hwnd),
            "x": x, "y": y,
            "width": w, "height": h,
        })
        return True
    
    ctypes.windll.user32.EnumWindows(WNDENUMPROC(callback), 0)
    return windows


def find_window(title: str, exact: bool = False) -> Optional[int]:
    """按标题查找窗口。
    
    Args:
        title: 窗口标题（支持部分匹配和正则）
        exact: True = 精确匹配，False = 包含匹配
    
    Returns:
        窗口句柄 hwnd，未找到返回 None
    """
    if exact:
        hwnd = ctypes.windll.user32.FindWindowW(None, title)
        return hwnd if hwnd else None
    
    # 模糊匹配 + 正则匹配（只枚举一次）
    title_lower = title.lower()
    all_windows = list_windows(include_all=True)

    for win in all_windows:
        if title_lower in win["title"].lower():
            return win["hwnd"]
    
    # 正则匹配
    try:
        pattern = re.compile(title, re.IGNORECASE)
        for win in all_windows:
            if pattern.search(win["title"]):
                return win["hwnd"]
    except re.error:
        pass
    
    return None


def focus_window(title: str) -> dict:
    """聚焦窗口（前置 + 还原）。
    
    Args:
        title: 窗口标题（支持模糊匹配）
    
    Returns:
        {"success": bool, "hwnd": int, "title": str, ...}
    """
    hwnd = find_window(title)
    if not hwnd:
        return {"success": False, "error": f"未找到窗口: {title!r}"}
    
    # 如果最小化，先还原
    if ctypes.windll.user32.IsIconic(hwnd):
        ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)
        time.sleep(0.1)
    
    # 前置窗口
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    time.sleep(0.1)
    
    actual_title = _get_window_title(hwnd)
    x, y, w, h = _get_window_rect(hwnd)
    
    return {
        "success": True,
        "hwnd": hwnd,
        "title": actual_title,
        "x": x, "y": y,
        "width": w, "height": h,
    }


def get_window_info(title: str) -> dict:
    """获取窗口信息。
    
    Args:
        title: 窗口标题（支持模糊匹配）
    
    Returns:
        窗口信息字典
    """
    hwnd = find_window(title)
    if not hwnd:
        return {"success": False, "error": f"未找到窗口: {title!r}"}
    
    actual_title = _get_window_title(hwnd)
    x, y, w, h = _get_window_rect(hwnd)
    
    return {
        "success": True,
        "hwnd": hwnd,
        "title": actual_title,
        "class": _get_class_name(hwnd),
        "pid": _get_process_id(hwnd),
        "x": x, "y": y,
        "width": w, "height": h,
        "is_minimized": bool(ctypes.windll.user32.IsIconic(hwnd)),
        "is_maximized": bool(ctypes.windll.user32.IsZoomed(hwnd)),
        "is_visible": bool(ctypes.windll.user32.IsWindowVisible(hwnd)),
    }


def move_window(title: str, x: int, y: int, width: int = 0, height: int = 0) -> dict:
    """移动/调整窗口大小。
    
    Args:
        title: 窗口标题
        x, y: 新位置
        width, height: 新尺寸（0 = 保持不变）
    """
    hwnd = find_window(title)
    if not hwnd:
        return {"success": False, "error": f"未找到窗口: {title!r}"}
    
    if width == 0 or height == 0:
        _, _, cur_w, cur_h = _get_window_rect(hwnd)
        if width == 0:
            width = cur_w
        if height == 0:
            height = cur_h
    
    ctypes.windll.user32.MoveWindow(hwnd, x, y, width, height, True)
    
    return {
        "success": True,
        "hwnd": hwnd,
        "x": x, "y": y,
        "width": width, "height": height,
    }


def minimize_window(title: str) -> dict:
    """最小化窗口。"""
    hwnd = find_window(title)
    if not hwnd:
        return {"success": False, "error": f"未找到窗口: {title!r}"}
    ctypes.windll.user32.ShowWindow(hwnd, SW_MINIMIZE)
    return {"success": True, "hwnd": hwnd}


def maximize_window(title: str) -> dict:
    """最大化窗口。"""
    hwnd = find_window(title)
    if not hwnd:
        return {"success": False, "error": f"未找到窗口: {title!r}"}
    ctypes.windll.user32.ShowWindow(hwnd, SW_MAXIMIZE)
    return {"success": True, "hwnd": hwnd}


def get_foreground_window() -> dict:
    """获取当前前台窗口信息。"""
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    if not hwnd:
        return {"success": False, "error": "无前台窗口"}
    
    title = _get_window_title(hwnd)
    x, y, w, h = _get_window_rect(hwnd)
    
    return {
        "success": True,
        "hwnd": hwnd,
        "title": title,
        "class": _get_class_name(hwnd),
        "x": x, "y": y,
        "width": w, "height": h,
    }
