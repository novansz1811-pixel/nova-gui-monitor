"""
鼠标键盘输入模块 — v2 Win32 API 版

直接使用 Win32 SendInput / SetCursorPos / keybd_event，
不依赖 pyautogui，精度更高。
"""

import ctypes
import ctypes.wintypes as wintypes
import time

from ..utils.clipboard import set_clipboard_text

# ─── Win32 常量 ───────────────────────────────────────────

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

# mouse_event flags
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000

# keybd_event flags
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

# Virtual Key Codes（常用）
VK_MAP = {
    # 修饰键
    "ctrl": 0x11, "control": 0x11,
    "alt": 0x12, "menu": 0x12,
    "shift": 0x10,
    "win": 0x5B, "lwin": 0x5B, "rwin": 0x5C,
    # 功能键
    "enter": 0x0D, "return": 0x0D,
    "tab": 0x09,
    "escape": 0x1B, "esc": 0x1B,
    "space": 0x20,
    "backspace": 0x08, "bs": 0x08,
    "delete": 0x2E, "del": 0x2E,
    "insert": 0x2D, "ins": 0x2D,
    "home": 0x24,
    "end": 0x23,
    "pageup": 0x21, "pgup": 0x21,
    "pagedown": 0x22, "pgdn": 0x22,
    # 方向键
    "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
    # F 键
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
    "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
    "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
    # 其他
    "capslock": 0x14, "numlock": 0x90, "scrolllock": 0x91,
    "printscreen": 0x2C, "prtsc": 0x2C,
    "apps": 0x5D,  # 菜单键
}


# ─── SendInput 结构体（type_unicode 使用） ──────────────────

class _KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

class _INPUT_UNION(ctypes.Union):
    _fields_ = [("ki", _KEYBDINPUT)]

class _INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("_input", _INPUT_UNION),
    ]

def _get_vk(key: str) -> int:
    """将按键名转换为 Virtual Key Code。"""
    key_lower = key.lower().strip()
    
    # 查表
    if key_lower in VK_MAP:
        return VK_MAP[key_lower]
    
    # 单字符 → VkKeyScan
    if len(key) == 1:
        vk = ctypes.windll.user32.VkKeyScanW(ord(key))
        if vk != -1:
            return vk & 0xFF
    
    raise ValueError(f"未知按键: {key!r}")


# ─── 鼠标操作 ──────────────────────────────────────────────

def click(x: int, y: int, button: str = "left", clicks: int = 1, interval: float = 0.05):
    """点击指定位置（物理坐标）。
    
    Args:
        x, y: 物理屏幕坐标
        button: "left" | "right" | "middle"
        clicks: 点击次数（2 = 双击）
        interval: 多次点击间隔（秒）
    """
    # 先移动光标
    ctypes.windll.user32.SetCursorPos(x, y)
    time.sleep(0.02)  # 等待光标到位
    
    # 按钮事件映射
    if button == "right":
        down, up = MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP
    elif button == "middle":
        down, up = MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP
    else:
        down, up = MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP
    
    for i in range(clicks):
        ctypes.windll.user32.mouse_event(down, 0, 0, 0, 0)
        time.sleep(0.01)
        ctypes.windll.user32.mouse_event(up, 0, 0, 0, 0)
        if i < clicks - 1:
            time.sleep(interval)


def move(x: int, y: int, duration: float = 0):
    """移动鼠标到指定位置。
    
    Args:
        x, y: 目标物理坐标
        duration: 移动耗时（秒），0 = 瞬移
    """
    if duration <= 0:
        ctypes.windll.user32.SetCursorPos(x, y)
        return
    
    # 平滑移动
    from ..utils.dpi import get_cursor_pos
    start_x, start_y = get_cursor_pos()
    
    steps = max(int(duration * 60), 5)  # 60 FPS
    for i in range(1, steps + 1):
        t = i / steps
        # 缓动函数（ease-out）
        t = 1 - (1 - t) ** 2
        cur_x = int(start_x + (x - start_x) * t)
        cur_y = int(start_y + (y - start_y) * t)
        ctypes.windll.user32.SetCursorPos(cur_x, cur_y)
        time.sleep(duration / steps)


def drag(
    start_x: int, start_y: int,
    end_x: int, end_y: int,
    duration: float = 0.5,
    button: str = "left",
):
    """拖拽操作。
    
    Args:
        start_x, start_y: 起始物理坐标
        end_x, end_y: 终点物理坐标
        duration: 拖拽耗时（秒）
        button: "left" | "right" | "middle"
    """
    if button == "right":
        down, up = MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP
    elif button == "middle":
        down, up = MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP
    else:
        down, up = MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP
    
    # 移到起点
    ctypes.windll.user32.SetCursorPos(start_x, start_y)
    time.sleep(0.05)
    
    # 按下
    ctypes.windll.user32.mouse_event(down, 0, 0, 0, 0)
    time.sleep(0.05)
    
    # 平滑移动到终点
    steps = max(int(duration * 60), 10)
    for i in range(1, steps + 1):
        t = i / steps
        cur_x = int(start_x + (end_x - start_x) * t)
        cur_y = int(start_y + (end_y - start_y) * t)
        ctypes.windll.user32.SetCursorPos(cur_x, cur_y)
        time.sleep(duration / steps)
    
    time.sleep(0.05)
    # 松开
    ctypes.windll.user32.mouse_event(up, 0, 0, 0, 0)


def scroll(amount: int, x: int | None = None, y: int | None = None):
    """滚轮滚动。
    
    Args:
        amount: 正数向上，负数向下（每次 120 单位 = 一个缺口）
        x, y: 可选，先移动到此位置再滚动
    """
    if x is not None and y is not None:
        ctypes.windll.user32.SetCursorPos(x, y)
        time.sleep(0.02)
    
    # WHEEL_DELTA = 120
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, amount * 120, 0)


# ─── 键盘操作 ──────────────────────────────────────────────

def key_press(key: str, presses: int = 1, interval: float = 0.05):
    """按下并释放按键。
    
    Args:
        key: 按键名（如 "enter", "tab", "a", "f5"）
        presses: 按键次数
        interval: 多次按键间隔
    """
    vk = _get_vk(key)
    for i in range(presses):
        ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.01)
        ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        if i < presses - 1:
            time.sleep(interval)


def hotkey(*keys: str):
    """组合键（如 hotkey("ctrl", "c")）。
    
    Args:
        keys: 按键名序列，前面的先按下，后面的后按下，释放顺序反转
    """
    vks = [_get_vk(k) for k in keys]
    
    # 按下（正序）
    for vk in vks:
        ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.02)
    
    time.sleep(0.05)
    
    # 释放（逆序）
    for vk in reversed(vks):
        ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)


def type_text(text: str, use_clipboard: bool = True, interval: float = 0):
    """输入文本。
    
    Args:
        text: 要输入的文本（支持中文）
        use_clipboard: True = 通过剪贴板粘贴（支持中文），False = 逐字符按键（仅 ASCII）
        interval: 逐字符模式的按键间隔
    """
    if use_clipboard:
        # 剪贴板方式：支持任意字符（中文、emoji 等）
        set_clipboard_text(text)
        time.sleep(0.05)
        hotkey("ctrl", "v")
        time.sleep(0.05)
    else:
        # 逐字符方式：仅支持 ASCII
        for ch in text:
            try:
                vk_result = ctypes.windll.user32.VkKeyScanW(ord(ch))
                if vk_result == -1:
                    continue
                vk = vk_result & 0xFF
                shift = bool(vk_result & 0x100)
                
                if shift:
                    ctypes.windll.user32.keybd_event(0x10, 0, 0, 0)  # SHIFT down
                
                ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
                time.sleep(0.01)
                ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
                
                if shift:
                    ctypes.windll.user32.keybd_event(0x10, 0, KEYEVENTF_KEYUP, 0)
                
                if interval > 0:
                    time.sleep(interval)
            except Exception:
                continue


def type_unicode(text: str, interval: float = 0.05):
    """通过 SendInput + KEYEVENTF_UNICODE 直接注入 Unicode 字符。
    
    适用于支持 WM_CHAR 的标准控件。对于 Qt 控件（如微信）可能无效，
    此时应使用 type_pinyin 或 type_text (clipboard)。
    
    Args:
        text: 要输入的文本（支持任意 Unicode）
        interval: 字符间隔（秒）
    """
    for ch in text:
        inputs = (_INPUT * 2)()
        # Key down
        inputs[0].type = INPUT_KEYBOARD
        inputs[0]._input.ki.wScan = ord(ch)
        inputs[0]._input.ki.dwFlags = KEYEVENTF_UNICODE
        # Key up
        inputs[1].type = INPUT_KEYBOARD
        inputs[1]._input.ki.wScan = ord(ch)
        inputs[1]._input.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP

        ctypes.windll.user32.SendInput(2, ctypes.byref(inputs), ctypes.sizeof(_INPUT))
        if interval > 0:
            time.sleep(interval)


def type_pinyin(text: str, char_interval: float = 0.08, confirm_delay: float = 0.5):
    """通过系统拼音输入法输入中文。
    
    将中文文本转换为拼音，逐字母键入触发系统 IME，然后按空格确认候选字。
    这是微信搜索框等 Qt 控件中输入中文的最可靠方式。
    
    需要系统输入法处于中文拼音模式。
    
    Args:
        text: 中文文本
        char_interval: 拼音字母间隔（秒）
        confirm_delay: 输入完成后等待 IME 候选的时间（秒）
    """
    try:
        from pypinyin import pinyin, Style
    except ImportError:
        raise ImportError(
            "type_pinyin 需要 pypinyin 库。请运行: pip install pypinyin"
        )

    # 将中文转为拼音（不带音调）
    py_list = pinyin(text, style=Style.NORMAL)
    full_pinyin = "".join(p[0] for p in py_list)

    # 逐字母按键
    for ch in full_pinyin:
        vk = ctypes.windll.user32.VkKeyScanW(ord(ch)) & 0xFF
        ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.02)
        ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(char_interval)

    # 等候选出现
    time.sleep(confirm_delay)

    # 按空格确认第一个候选
    ctypes.windll.user32.keybd_event(0x20, 0, 0, 0)
    time.sleep(0.02)
    ctypes.windll.user32.keybd_event(0x20, 0, KEYEVENTF_KEYUP, 0)
