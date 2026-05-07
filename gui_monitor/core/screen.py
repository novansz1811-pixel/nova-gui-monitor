"""
屏幕截图模块 — v2 mss 高性能版

使用 mss 库进行截图，比 pyautogui.screenshot() 快 3-5 倍。
所有坐标均为物理坐标。
"""

import io
import mss
import mss.tools
from PIL import Image

from ..utils.dpi import get_screen_size


def screenshot(
    region: tuple[int, int, int, int] | None = None,
    save_path: str | None = None,
    quality: int = 85,
    format: str = "png",
) -> bytes:
    """截取屏幕并返回图像字节流。
    
    Args:
        region: (x, y, width, height) 物理坐标区域，None 表示主屏全屏
        save_path: 可选，保存到文件路径
        quality: JPEG 压缩质量 (1-100)，仅 format="jpeg" 时有效
        format: 输出格式 "png" | "jpeg"
    
    Returns:
        图像字节流（PNG 或 JPEG）
    """
    with mss.mss() as sct:
        if region:
            x, y, w, h = region
            monitor = {"left": x, "top": y, "width": w, "height": h}
        else:
            # 主屏（monitors[1] 是主显示器，monitors[0] 是虚拟全屏）
            monitor = sct.monitors[1]
        
        raw = sct.grab(monitor)
        pil_img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
    
    # 编码参数
    fmt_upper = "JPEG" if format.lower() == "jpeg" else "PNG"
    save_kwargs = {"quality": quality} if fmt_upper == "JPEG" else {"optimize": True}

    if save_path:
        # 保存到文件，然后读回字节（避免双重编码）
        pil_img.save(save_path, format=fmt_upper, **save_kwargs)
        with open(save_path, "rb") as f:
            return f.read()

    # 仅编码到内存
    buf = io.BytesIO()
    pil_img.save(buf, format=fmt_upper, **save_kwargs)
    return buf.getvalue()


def screenshot_window(
    hwnd: int,
    save_path: str | None = None,
    quality: int = 85,
    format: str = "png",
) -> bytes:
    """截取指定窗口。
    
    Args:
        hwnd: 窗口句柄
        save_path: 可选，保存到文件路径
        quality: JPEG 质量
        format: "png" | "jpeg"
    
    Returns:
        图像字节流
    """
    import ctypes
    import ctypes.wintypes as wintypes
    
    # 获取窗口位置
    rect = wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
    
    region = (
        rect.left,
        rect.top,
        rect.right - rect.left,
        rect.bottom - rect.top,
    )
    return screenshot(region=region, save_path=save_path, quality=quality, format=format)


def get_screen_info() -> dict:
    """获取屏幕信息。
    
    Returns:
        包含屏幕尺寸和所有显示器信息的字典
    """
    w, h = get_screen_size()
    
    monitors = []
    with mss.mss() as sct:
        for i, mon in enumerate(sct.monitors):
            monitors.append({
                "index": i,
                "left": mon["left"],
                "top": mon["top"],
                "width": mon["width"],
                "height": mon["height"],
                "is_primary": i == 1,
                "is_virtual": i == 0,
            })
    
    return {
        "primary_width": w,
        "primary_height": h,
        "monitors": monitors,
    }
