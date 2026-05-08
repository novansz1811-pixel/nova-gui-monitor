"""
Telegram 文字输入完整测试 — 发消息给雪雪(主Agent)

流程:
  1. 找到 Telegram 窗口并聚焦
  2. 搜索 "雪雪(主Agent)"
  3. 点击进入聊天
  4. 在输入框输入测试消息
  5. 发送消息
  6. 每步截图留证
"""
import sys, time, os, json, ctypes, ctypes.wintypes as wt

# === 修复终端编码 ===
for _s in (sys.stdout, sys.stderr):
    _r = getattr(_s, "reconfigure", None)
    if _r:
        try: _r(encoding="utf-8", errors="replace")
        except: pass

# === DPI 初始化（必须最先） ===
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
    print(f"  [screenshot] {name}")
    return path

def step(n, msg):
    print(f"\n{'='*50}")
    print(f"[Step {n}] {msg}")
    print(f"{'='*50}")


# ─── Step 1: 找到 Telegram ───
step(1, "寻找并聚焦 Telegram 窗口")

wins = gw.list_windows()
tg = None
for w in wins:
    t = w["title"].lower()
    if "telegram" in t:
        tg = w
        break

if not tg:
    print(f"  [FAIL] Wei zhao dao Telegram chuang kou! Dang qian ke jian chuang kou:")
    for w in wins:
        print(f"    - {w['title'][:80]}")
    sys.exit(1)

print(f"  [OK] Found: '{tg['title']}' (hwnd={tg['hwnd']})")

# 恢复 & 聚焦
hwnd = tg["hwnd"]
if ctypes.windll.user32.IsIconic(hwnd):
    ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    time.sleep(0.3)
ctypes.windll.user32.SetForegroundWindow(hwnd)
time.sleep(0.5)

# 获取窗口位置
rect = wt.RECT()
ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
wx, wy = rect.left, rect.top
ww = rect.right - rect.left
wh = rect.bottom - rect.top
print(f"  窗口位置: ({wx},{wy}) 大小: {ww}x{wh}")
save("step1_focused")


# ─── Step 2: 回到主聊天列表 ───
step(2, "按 Escape 回到聊天列表")
gi.key_press("escape")
time.sleep(0.3)
gi.key_press("escape")
time.sleep(0.5)
save("step2_chatlist")


# ─── Step 3: 搜索雪雪(主Agent) ───
step(3, "搜索 雪雪(主Agent)")

# Telegram 搜索框位置（侧边栏顶部）
search_x = wx + 200
search_y = wy + 55
print(f"  点击搜索框 ({search_x}, {search_y})")
gi.click(search_x, search_y)
time.sleep(0.5)

# 输入搜索词
search_term = "雪雪"
print(f"  输入搜索词: '{search_term}'")
gi.type_text(search_term, use_clipboard=True)
time.sleep(1.5)
save("step3_searched")


# ─── Step 4: 点击搜索结果 ───
step(4, "点击搜索结果进入聊天")

# 搜索结果通常在搜索框下方 ~80px 处
result_x = wx + 200
result_y = wy + 140
print(f"  点击搜索结果 ({result_x}, {result_y})")
gi.click(result_x, result_y)
time.sleep(1.0)
save("step4_chat_opened")


# ─── Step 5: 在输入框输入消息 ───
step(5, "在聊天输入框输入测试消息")

# Telegram 输入框在窗口底部中央
input_x = wx + ww // 2
input_y = wy + wh - 45
print(f"  点击输入框 ({input_x}, {input_y})")
gi.click(input_x, input_y)
time.sleep(0.3)

# 输入测试消息（中英文混合，测试剪贴板中文输入）
test_msg = "GUI Monitor test -- Hello! \u4f60\u597d\u4e16\u754c 123 abc"
print(f"  typing message: {test_msg!r}")
gi.type_text(test_msg, use_clipboard=True)
time.sleep(0.5)
save("step5_typed")


# ─── Step 6: 发送消息 ───
step(6, "按 Enter 发送消息")
gi.key_press("enter")
time.sleep(1.0)
save("step6_sent")


# ─── 完成 ───
print(f"\n{'='*50}")
print(f"[DONE] Test complete! Screenshots saved to: {SCREENSHOT_DIR}")
print(f"{'='*50}")
