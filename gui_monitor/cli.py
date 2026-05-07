"""
GUI Monitor CLI — 命令行接口

用法:
    python -m gui_monitor <command> [options]
    
命令:
    screenshot  截取屏幕
    click       点击指定坐标
    move        移动鼠标
    drag        拖拽操作
    scroll      滚轮滚动
    type        输入文本（支持中文）
    key         按键操作
    hotkey      组合键
    windows     列出所有窗口
    focus       聚焦窗口
    window-info 获取窗口信息
    foreground  获取当前前台窗口
    info        屏幕信息
    cursor      当前鼠标位置
    serve       启动 HTTP API 服务
"""

import argparse
import json
import sys
import os


def _configure_stdio():
    """Keep Unicode output from crashing on legacy Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if not reconfigure:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            try:
                reconfigure(errors="replace")
            except (OSError, ValueError):
                pass


def _parse_region(s: str) -> tuple[int, int, int, int]:
    """解析区域字符串 "x,y,w,h" 。"""
    parts = s.split(",")
    if len(parts) != 4:
        raise argparse.ArgumentTypeError(f"区域格式错误，应为 x,y,width,height: {s!r}")
    return tuple(int(p.strip()) for p in parts)


def cmd_screenshot(args):
    """截图命令。"""
    from .core.screen import screenshot, screenshot_window, get_screen_info
    from .core.window import find_window
    from pathlib import Path

    # 如果 --save 是裸文件名（无目录），自动放到 screenshots_debug/
    if args.save and os.path.dirname(args.save) == "":
        debug_dir = Path(__file__).parent.parent / "screenshots_debug"
        debug_dir.mkdir(exist_ok=True)
        args.save = str(debug_dir / args.save)

    region = None
    
    if args.region:
        region = _parse_region(args.region)
    elif args.window:
        hwnd = find_window(args.window)
        if not hwnd:
            print(json.dumps({"error": f"未找到窗口: {args.window!r}"}, ensure_ascii=False))
            return 1
        # 截窗口
        data = screenshot_window(hwnd, save_path=args.save, quality=args.quality, format=args.format)
        if args.save:
            result = {"success": True, "path": os.path.abspath(args.save), "size": len(data)}
            print(json.dumps(result, ensure_ascii=False))
        elif args.base64:
            import base64
            print(base64.b64encode(data).decode("ascii"))
        else:
            sys.stdout.buffer.write(data)
        return 0
    
    data = screenshot(region=region, save_path=args.save, quality=args.quality, format=args.format)
    
    if args.save:
        result = {"success": True, "path": os.path.abspath(args.save), "size": len(data)}
        print(json.dumps(result, ensure_ascii=False))
    elif args.base64:
        import base64
        print(base64.b64encode(data).decode("ascii"))
    else:
        # 二进制输出到 stdout
        sys.stdout.buffer.write(data)
    
    return 0



def cmd_click(args):
    """点击命令。"""
    from .core.input import click
    
    button = "right" if args.right else ("middle" if args.middle else "left")
    clicks = 2 if args.double else args.clicks
    
    click(args.x, args.y, button=button, clicks=clicks)
    
    result = {"success": True, "x": args.x, "y": args.y, "button": button, "clicks": clicks}
    print(json.dumps(result))
    return 0


def cmd_move(args):
    """移动鼠标命令。"""
    from .core.input import move
    
    move(args.x, args.y, duration=args.duration)
    
    result = {"success": True, "x": args.x, "y": args.y}
    print(json.dumps(result))
    return 0


def cmd_drag(args):
    """拖拽命令。"""
    from .core.input import drag
    
    drag(args.x1, args.y1, args.x2, args.y2, duration=args.duration)
    
    result = {"success": True, "from": [args.x1, args.y1], "to": [args.x2, args.y2]}
    print(json.dumps(result))
    return 0


def cmd_scroll(args):
    """滚动命令。"""
    from .core.input import scroll
    
    x = args.x if args.x is not None else None
    y = args.y if args.y is not None else None
    scroll(args.amount, x=x, y=y)
    
    result = {"success": True, "amount": args.amount}
    print(json.dumps(result))
    return 0


def cmd_type(args):
    """输入文本命令。"""
    from .core.input import type_text
    
    text = " ".join(args.text)
    type_text(text, use_clipboard=not args.ascii_mode)
    
    result = {"success": True, "text": text, "method": "ascii" if args.ascii_mode else "clipboard"}
    print(json.dumps(result, ensure_ascii=False))
    return 0


def cmd_key(args):
    """按键命令。"""
    from .core.input import key_press
    
    key_press(args.key, presses=args.presses)
    
    result = {"success": True, "key": args.key, "presses": args.presses}
    print(json.dumps(result))
    return 0


def cmd_hotkey(args):
    """组合键命令。"""
    from .core.input import hotkey
    
    hotkey(*args.keys)
    
    result = {"success": True, "keys": args.keys}
    print(json.dumps(result))
    return 0


def cmd_windows(args):
    """列出窗口命令。"""
    from .core.window import list_windows
    
    windows = list_windows(include_all=args.all)
    
    if args.json:
        print(json.dumps(windows, ensure_ascii=False, indent=2))
    else:
        # 表格输出
        print(f"{'HWND':<10} {'PID':<8} {'位置':<20} {'标题'}")
        print("-" * 80)
        for w in windows:
            pos = f"({w['x']},{w['y']}) {w['width']}x{w['height']}"
            print(f"{w['hwnd']:<10} {w['pid']:<8} {pos:<20} {w['title']}")
        print(f"\n共 {len(windows)} 个窗口")
    
    return 0


def cmd_focus(args):
    """聚焦窗口命令。"""
    from .core.window import focus_window
    
    result = focus_window(args.title)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("success") else 1


def cmd_window_info(args):
    """窗口信息命令。"""
    from .core.window import get_window_info
    
    result = get_window_info(args.title)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


def cmd_foreground(args):
    """前台窗口命令。"""
    from .core.window import get_foreground_window
    
    result = get_foreground_window()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_info(args):
    """屏幕信息命令。"""
    from .core.screen import get_screen_info
    from .utils.dpi import get_dpi_scale, get_screen_size
    
    screen = get_screen_info()
    screen["dpi_scale"] = get_dpi_scale()
    
    print(json.dumps(screen, ensure_ascii=False, indent=2))
    return 0


def cmd_cursor(args):
    """鼠标位置命令。"""
    from .utils.dpi import get_cursor_pos
    
    x, y = get_cursor_pos()
    result = {"x": x, "y": y}
    print(json.dumps(result))
    return 0


def cmd_serve(args):
    """启动 HTTP API 服务。"""
    from .server import start_server
    
    start_server(host=args.host, port=args.port)
    return 0


def cmd_chat_agent(args):
    """聊天自动监控与回复。"""
    from .chat_agent import monitor_loop

    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(json.dumps({
            "error": "需要 OpenAI API Key。使用 --api-key 或设置 OPENAI_API_KEY 环境变量"
        }, ensure_ascii=False))
        return 1

    print("=" * 50)
    print("🤖 Chat Agent v2.0 (集成版)")
    print(f"   联系人: {args.contact}")
    print(f"   模式: {args.mode}")
    print(f"   间隔: {args.interval}秒")
    print(f"   发送键: {args.send_key}")
    print("=" * 50)

    monitor_loop(
        contact=args.contact,
        interval=args.interval,
        mode=args.mode,
        api_key=api_key,
        style_path=args.style,
        send_key=args.send_key,
    )
    return 0


def cmd_chat_learn(args):
    """从聊天记录学习风格。"""
    from .chat_agent import learn_style

    result = learn_style(history_dir=args.history, output=args.output)
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result else 1


def cmd_type_pinyin(args):
    """通过拼音输入法输入中文。"""
    from .core.input import type_pinyin

    text = " ".join(args.text)
    type_pinyin(text)

    result = {"success": True, "text": text, "method": "pinyin"}
    print(json.dumps(result, ensure_ascii=False))
    return 0


def cmd_type_unicode(args):
    """通过 Unicode SendInput 输入文本。"""
    from .core.input import type_unicode

    text = " ".join(args.text)
    type_unicode(text)

    result = {"success": True, "text": text, "method": "unicode"}
    print(json.dumps(result, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="gui_monitor",
        description="GUI Monitor — 电脑自动化 CLI 工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__import__('gui_monitor').__version__}",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # ─── screenshot ─────────────────────────────────
    p = subparsers.add_parser("screenshot", aliases=["ss"], help="截取屏幕")
    p.add_argument("--region", "-r", help="区域 x,y,width,height")
    p.add_argument("--window", "-w", help="按窗口标题截图")
    p.add_argument("--save", "-s", help="保存到文件路径")
    p.add_argument("--format", "-f", default="png", choices=["png", "jpeg"], help="图片格式")
    p.add_argument("--quality", "-q", type=int, default=85, help="JPEG 质量 (1-100)")
    p.add_argument("--base64", "-b", action="store_true", help="输出 Base64 编码")
    p.set_defaults(func=cmd_screenshot)
    
    # ─── click ──────────────────────────────────────
    p = subparsers.add_parser("click", help="点击指定坐标")
    p.add_argument("x", type=int, help="X 坐标")
    p.add_argument("y", type=int, help="Y 坐标")
    p.add_argument("--right", action="store_true", help="右键点击")
    p.add_argument("--middle", action="store_true", help="中键点击")
    p.add_argument("--double", action="store_true", help="双击")
    p.add_argument("--clicks", type=int, default=1, help="点击次数")
    p.set_defaults(func=cmd_click)
    
    # ─── move ───────────────────────────────────────
    p = subparsers.add_parser("move", help="移动鼠标")
    p.add_argument("x", type=int, help="X 坐标")
    p.add_argument("y", type=int, help="Y 坐标")
    p.add_argument("--duration", "-d", type=float, default=0, help="移动耗时（秒）")
    p.set_defaults(func=cmd_move)
    
    # ─── drag ───────────────────────────────────────
    p = subparsers.add_parser("drag", help="拖拽操作")
    p.add_argument("x1", type=int, help="起始 X")
    p.add_argument("y1", type=int, help="起始 Y")
    p.add_argument("x2", type=int, help="终点 X")
    p.add_argument("y2", type=int, help="终点 Y")
    p.add_argument("--duration", "-d", type=float, default=0.5, help="拖拽耗时（秒）")
    p.set_defaults(func=cmd_drag)
    
    # ─── scroll ─────────────────────────────────────
    p = subparsers.add_parser("scroll", help="滚轮滚动")
    p.add_argument("amount", type=int, help="滚动量（正=上, 负=下）")
    p.add_argument("--x", type=int, default=None, help="滚动位置 X")
    p.add_argument("--y", type=int, default=None, help="滚动位置 Y")
    p.set_defaults(func=cmd_scroll)
    
    # ─── type ───────────────────────────────────────
    p = subparsers.add_parser("type", help="输入文本（支持中文）")
    p.add_argument("text", nargs="+", help="要输入的文本")
    p.add_argument("--ascii", dest="ascii_mode", action="store_true", help="逐字符模式（仅 ASCII）")
    p.set_defaults(func=cmd_type)
    
    # ─── key ────────────────────────────────────────
    p = subparsers.add_parser("key", help="按键操作")
    p.add_argument("key", help="按键名（enter, tab, f5, a, ...）")
    p.add_argument("--presses", "-n", type=int, default=1, help="按键次数")
    p.set_defaults(func=cmd_key)
    
    # ─── hotkey ─────────────────────────────────────
    p = subparsers.add_parser("hotkey", help="组合键")
    p.add_argument("keys", nargs="+", help="按键序列（如: ctrl c）")
    p.set_defaults(func=cmd_hotkey)
    
    # ─── windows ────────────────────────────────────
    p = subparsers.add_parser("windows", aliases=["wl"], help="列出所有窗口")
    p.add_argument("--all", "-a", action="store_true", help="包含所有窗口")
    p.add_argument("--json", "-j", action="store_true", help="JSON 格式输出")
    p.set_defaults(func=cmd_windows)
    
    # ─── focus ──────────────────────────────────────
    p = subparsers.add_parser("focus", help="聚焦窗口")
    p.add_argument("title", help="窗口标题（支持模糊匹配）")
    p.set_defaults(func=cmd_focus)
    
    # ─── window-info ────────────────────────────────
    p = subparsers.add_parser("window-info", aliases=["wi"], help="获取窗口信息")
    p.add_argument("title", help="窗口标题")
    p.set_defaults(func=cmd_window_info)
    
    # ─── foreground ─────────────────────────────────
    p = subparsers.add_parser("foreground", aliases=["fg"], help="获取前台窗口信息")
    p.set_defaults(func=cmd_foreground)
    
    # ─── info ───────────────────────────────────────
    p = subparsers.add_parser("info", help="屏幕和显示器信息")
    p.set_defaults(func=cmd_info)
    
    # ─── cursor ─────────────────────────────────────
    p = subparsers.add_parser("cursor", aliases=["pos"], help="当前鼠标位置")
    p.set_defaults(func=cmd_cursor)
    
    # ─── serve ──────────────────────────────────────
    p = subparsers.add_parser("serve", help="启动 HTTP API 服务")
    p.add_argument("--host", default="127.0.0.1", help="监听地址")
    p.add_argument("--port", "-p", type=int, default=8765, help="端口号")
    p.set_defaults(func=cmd_serve)

    # ─── chat-agent ─────────────────────────────────
    p = subparsers.add_parser("chat-agent", aliases=["ca"], help="聊天自动监控与回复")
    p.add_argument("--contact", "-c", required=True, help="联系人/群名称")
    p.add_argument("--interval", "-i", type=int, default=10, help="截图间隔（秒）")
    p.add_argument("--mode", "-m", default="review",
                   choices=["auto", "review", "notify"],
                   help="auto(自动回复) / review(审核) / notify(仅通知)")
    p.add_argument("--api-key", help="OpenAI API Key（或 OPENAI_API_KEY 环境变量）")
    p.add_argument("--style", help="风格配置文件路径")
    p.add_argument("--send-key", default="alt s", help="发送快捷键 (默认 'alt s')")
    p.set_defaults(func=cmd_chat_agent)

    # ─── chat-learn ─────────────────────────────────
    p = subparsers.add_parser("chat-learn", aliases=["cl"], help="从聊天记录学习风格")
    p.add_argument("--history", help="聊天记录目录")
    p.add_argument("--output", "-o", help="输出风格配置文件路径")
    p.set_defaults(func=cmd_chat_learn)

    # ─── type-pinyin ────────────────────────────────
    p = subparsers.add_parser("type-pinyin", aliases=["tp"], help="通过拼音输入法输入中文")
    p.add_argument("text", nargs="+", help="要输入的中文")
    p.set_defaults(func=cmd_type_pinyin)

    # ─── type-unicode ───────────────────────────────
    p = subparsers.add_parser("type-unicode", aliases=["tu"], help="通过 Unicode SendInput 输入")
    p.add_argument("text", nargs="+", help="要输入的文本")
    p.set_defaults(func=cmd_type_unicode)

    return parser


def main():
    """CLI 入口。"""
    _configure_stdio()

    parser = build_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        error = {"error": str(e), "type": type(e).__name__}
        print(json.dumps(error, ensure_ascii=False), file=sys.stderr)
        return 1
