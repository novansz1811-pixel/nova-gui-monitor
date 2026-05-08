"""
Telegram 发送消息 — 完整流程（稳健版）
"""
import sys, time, os

from gui_monitor.utils.dpi import init_dpi
init_dpi()

from gui_monitor.core import input as gi
from gui_monitor.core import screen as gs
from gui_monitor.core import window as gw

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots_debug")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def save(name):
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    gs.screenshot(save_path=path)
    print(f"  [shot] {name}")

# === 1. 找到并聚焦 Telegram ===
print("[1] Finding Telegram...")
wins = gw.list_windows()
tg = None
for w in wins:
    t = w["title"]
    if "telegram" in t.lower() or "雪" in t:
        tg = w
        break
if not tg:
    print("  ERROR: Telegram not found")
    for w in wins:
        print(f"    {w['title'][:60]}")
    sys.exit(1)

import ctypes
if ctypes.windll.user32.IsIconic(tg["hwnd"]):
    ctypes.windll.user32.ShowWindow(tg["hwnd"], 9)
    time.sleep(0.3)
ctypes.windll.user32.SetForegroundWindow(tg["hwnd"])
time.sleep(0.5)

# 重新获取窗口位置（可能因重启位置变了）
import ctypes.wintypes as wt
rect = wt.RECT()
ctypes.windll.user32.GetWindowRect(tg["hwnd"], ctypes.byref(rect))
wx, wy = rect.left, rect.top
ww = rect.right - rect.left
wh = rect.bottom - rect.top
print(f"  OK: '{tg['title']}' at ({wx},{wy}) {ww}x{wh}")
save("01_focused")

# === 2. 回到主聊天列表 ===
print("[2] Returning to chat list...")
gi.key_press("escape")
time.sleep(0.2)
gi.key_press("escape")
time.sleep(0.5)
save("02_chatlist")

# === 3. 用搜索功能精确找到雪雪(主Agent) ===
print("[3] Searching for 雪雪(主Agent)...")
# 点击搜索框
search_x = wx + 200
search_y = wy + 55
print(f"  Click search ({search_x}, {search_y})")
gi.click(search_x, search_y)
time.sleep(0.5)

# 输入搜索词
gi.type_text("雪雪 主Agent", use_clipboard=True)
time.sleep(1.5)
save("03_searched")
