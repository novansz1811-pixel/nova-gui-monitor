"""
Nova GUI Monitor — MCP Server

将 GUI 自动化核心 API 暴露为 MCP (Model Context Protocol) 工具，
供 AI Agent（Claude Code / Cursor / Hermes 等）原生调用。

启动方式：
    python -m gui_monitor mcp           # stdio 模式（标准 MCP 传输）
    python -m gui_monitor mcp --sse     # SSE 模式（HTTP 传输）

配置到 Agent：
    {
        "gui-monitor": {
            "command": "python",
            "args": ["-m", "gui_monitor", "mcp"]
        }
    }
"""

import base64
import json
import ctypes

from mcp.server.fastmcp import FastMCP

from .core import input as gui_input
from .core import screen as gui_screen
from .core import window as gui_window
from .utils.dpi import get_screen_size, get_cursor_pos

# ─── 初始化 MCP Server ──────────────────────────────────────

mcp = FastMCP("Nova GUI Monitor — Windows 桌面 GUI 自动化")


# ═══════════════════════════════════════════════════════════════
#  截图工具
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
def gui_screenshot(
    region: str | None = None,
    quality: int = 85,
) -> str:
    """截取屏幕截图，返回 base64 编码的 PNG 图像。

    Args:
        region: 截图区域 "x,y,width,height"（物理坐标），省略则全屏
        quality: JPEG 质量 1-100（仅 JPEG 格式有效）

    Returns:
        base64 编码的 PNG 图像数据（可直接用于 AI 视觉分析）
    """
    parsed_region = None
    if region:
        parts = region.split(",")
        if len(parts) == 4:
            parsed_region = tuple(int(p.strip()) for p in parts)

    img_bytes = gui_screen.screenshot(region=parsed_region, quality=quality)
    b64 = base64.b64encode(img_bytes).decode("ascii")
    return f"data:image/png;base64,{b64}"


# ═══════════════════════════════════════════════════════════════
#  鼠标工具
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
def gui_click(
    x: int,
    y: int,
    button: str = "left",
    clicks: int = 1,
) -> str:
    """点击屏幕指定坐标。

    Args:
        x: X 坐标（物理像素）
        y: Y 坐标（物理像素）
        button: 鼠标按键 "left" | "right" | "middle"
        clicks: 点击次数（2 = 双击）

    Returns:
        操作结果 JSON
    """
    gui_input.click(x, y, button=button, clicks=clicks)
    return json.dumps({"success": True, "x": x, "y": y, "button": button, "clicks": clicks})


@mcp.tool()
def gui_move(x: int, y: int, duration: float = 0) -> str:
    """移动鼠标到指定坐标。

    Args:
        x: 目标 X 坐标（物理像素）
        y: 目标 Y 坐标（物理像素）
        duration: 移动耗时（秒），0 = 瞬移

    Returns:
        操作结果 JSON
    """
    gui_input.move(x, y, duration=duration)
    return json.dumps({"success": True, "x": x, "y": y})


@mcp.tool()
def gui_drag(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration: float = 0.5,
    button: str = "left",
) -> str:
    """拖拽操作：从起点拖到终点。

    Args:
        start_x: 起始 X 坐标
        start_y: 起始 Y 坐标
        end_x: 终点 X 坐标
        end_y: 终点 Y 坐标
        duration: 拖拽耗时（秒）
        button: 鼠标按键 "left" | "right"

    Returns:
        操作结果 JSON
    """
    gui_input.drag(start_x, start_y, end_x, end_y, duration=duration, button=button)
    return json.dumps({"success": True, "from": [start_x, start_y], "to": [end_x, end_y]})


@mcp.tool()
def gui_scroll(amount: int, x: int | None = None, y: int | None = None) -> str:
    """鼠标滚轮滚动。

    Args:
        amount: 滚动量，正数向上，负数向下（1 = 一个滚轮缺口）
        x: 可选，先移到此 X 坐标再滚动
        y: 可选，先移到此 Y 坐标再滚动

    Returns:
        操作结果 JSON
    """
    gui_input.scroll(amount, x=x, y=y)
    return json.dumps({"success": True, "amount": amount})


@mcp.tool()
def gui_cursor() -> str:
    """获取当前鼠标光标位置。

    Returns:
        JSON: {"x": int, "y": int}
    """
    x, y = get_cursor_pos()
    return json.dumps({"x": x, "y": y})


# ═══════════════════════════════════════════════════════════════
#  键盘工具
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
def gui_type(text: str, use_clipboard: bool = True) -> str:
    """输入文本（支持中文）。

    Args:
        text: 要输入的文本内容
        use_clipboard: True = 通过剪贴板粘贴（推荐，支持中文）；False = 逐字符输入

    Returns:
        操作结果 JSON
    """
    gui_input.type_text(text, use_clipboard=use_clipboard)
    return json.dumps({"success": True, "text": text, "method": "clipboard" if use_clipboard else "keystroke"})


@mcp.tool()
def gui_key(key: str, presses: int = 1) -> str:
    """按下并释放按键。

    Args:
        key: 按键名（如 "enter", "tab", "escape", "a", "f5", "delete"）
        presses: 按键次数

    Returns:
        操作结果 JSON
    """
    gui_input.key_press(key, presses=presses)
    return json.dumps({"success": True, "key": key, "presses": presses})


@mcp.tool()
def gui_hotkey(keys: str) -> str:
    """按下组合键。

    Args:
        keys: 按键组合，用 "+" 分隔（如 "ctrl+c", "ctrl+shift+s", "alt+f4"）

    Returns:
        操作结果 JSON
    """
    key_list = [k.strip() for k in keys.split("+")]
    gui_input.hotkey(*key_list)
    return json.dumps({"success": True, "keys": key_list})


# ═══════════════════════════════════════════════════════════════
#  窗口管理工具
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
def gui_windows(include_all: bool = False) -> str:
    """列出当前所有可见窗口。

    Args:
        include_all: True = 包含隐藏/系统窗口，False = 仅可见窗口

    Returns:
        窗口列表 JSON
    """
    windows = gui_window.list_windows(include_all=include_all)
    return json.dumps(windows, ensure_ascii=False)


@mcp.tool()
def gui_focus(title: str) -> str:
    """聚焦（前置）指定窗口。

    Args:
        title: 窗口标题（支持模糊匹配和正则表达式）

    Returns:
        操作结果 JSON，包含窗口位置和大小
    """
    result = gui_window.focus_window(title)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def gui_window_info(title: str) -> str:
    """获取指定窗口的详细信息。

    Args:
        title: 窗口标题（支持模糊匹配）

    Returns:
        窗口信息 JSON（位置、大小、状态等）
    """
    result = gui_window.get_window_info(title)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def gui_move_window(
    title: str,
    x: int,
    y: int,
    width: int = 0,
    height: int = 0,
) -> str:
    """移动或调整窗口大小。

    Args:
        title: 窗口标题（支持模糊匹配）
        x: 新的 X 位置
        y: 新的 Y 位置
        width: 新宽度（0 = 保持不变）
        height: 新高度（0 = 保持不变）

    Returns:
        操作结果 JSON
    """
    result = gui_window.move_window(title, x, y, width, height)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def gui_foreground() -> str:
    """获取当前前台（活动）窗口信息。

    Returns:
        前台窗口信息 JSON
    """
    result = gui_window.get_foreground_window()
    return json.dumps(result, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════
#  系统信息工具
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
def gui_screen_info() -> str:
    """获取屏幕和显示器信息。

    Returns:
        JSON: 包含分辨率、DPI 缩放比例、所有显示器列表
    """
    info = gui_screen.get_screen_info()
    return json.dumps(info, ensure_ascii=False)


# ─── 入口 ─────────────────────────────────────────────────────

def run_mcp(transport: str = "stdio"):
    """启动 MCP Server。

    Args:
        transport: "stdio" 或 "sse"
    """
    # 确保 DPI 感知已初始化
    from .utils.dpi import init_dpi_awareness
    init_dpi_awareness()

    mcp.run(transport=transport)
