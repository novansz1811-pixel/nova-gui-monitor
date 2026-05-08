"""
诊断 type_text 剪贴板输入问题
"""
import sys, time, os, ctypes, ctypes.wintypes as wt

for _s in (sys.stdout, sys.stderr):
    _r = getattr(_s, "reconfigure", None)
    if _r:
        try: _r(encoding="utf-8", errors="replace")
        except: pass

from gui_monitor.utils.dpi import init_dpi
init_dpi()

from gui_monitor.core import input as gi
from gui_monitor.core import screen as gs
from gui_monitor.core import window as gw
from gui_monitor.utils.clipboard import set_clipboard_text, get_clipboard_text

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots_debug")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def save(name):
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    gs.screenshot(save_path=path)
    print(f"  [screenshot] {name}")

# === 诊断1: 剪贴板读写 ===
print("\n=== Diag 1: Clipboard read/write ===")
test_text = "Hello 你好世界"
ok = set_clipboard_text(test_text)
print(f"  set_clipboard_text({test_text!r}) => {ok}")
readback = get_clipboard_text()
print(f"  get_clipboard_text() => {readback!r}")
print(f"  Match: {readback == test_text}")

# === 诊断2: 剪贴板重试 ===
print("\n=== Diag 2: Clipboard with retry ===")
for i in range(3):
    ok = set_clipboard_text(f"Test {i} 测试")
    rb = get_clipboard_text()
    print(f"  Attempt {i}: set={ok}, read={rb!r}")
    time.sleep(0.1)

# === 诊断3: 在 Telegram 中测试 ===
print("\n=== Diag 3: Telegram type_text test ===")
wins = gw.list_windows()
tg = None
for w in wins:
    if "telegram" in w["title"].lower():
        tg = w
        break

if not tg:
    print("  Telegram not found!")
    sys.exit(1)

hwnd = tg["hwnd"]
if ctypes.windll.user32.IsIconic(hwnd):
    ctypes.windll.user32.ShowWindow(hwnd, 9)
    time.sleep(0.3)
ctypes.windll.user32.SetForegroundWindow(hwnd)
time.sleep(0.5)

rect = wt.RECT()
ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
wx, wy = rect.left, rect.top
ww = rect.right - rect.left
wh = rect.bottom - rect.top
print(f"  Telegram: ({wx},{wy}) {ww}x{wh}")

# 先按 Escape 回到聊天列表
gi.key_press("escape")
time.sleep(0.3)
gi.key_press("escape")
time.sleep(0.5)
save("diag_0_chatlist")

# 点击搜索框
search_x = wx + 200
search_y = wy + 55
print(f"\n  [1] Click search box ({search_x}, {search_y})")
gi.click(search_x, search_y)
time.sleep(0.8)
save("diag_1_clicked_search")

# 检查焦点窗口
fg_hwnd = ctypes.windll.user32.GetForegroundWindow()
print(f"  Foreground HWND: {fg_hwnd} (Telegram={hwnd})")
print(f"  Same window: {fg_hwnd == hwnd}")

# 手动分步执行 type_text 的逻辑
print(f"\n  [2] Manual clipboard paste")
text = "雪雪"

# Step A: 写入剪贴板
print(f"  [2a] Writing to clipboard: {text!r}")
ok = set_clipboard_text(text)
print(f"       set_clipboard_text => {ok}")

# Step B: 读回验证
rb = get_clipboard_text()
print(f"  [2b] Readback: {rb!r}, match={rb==text}")

# Step C: 等待更长时间
time.sleep(0.2)

# Step D: 按 Ctrl+V
print(f"  [2c] Pressing Ctrl+V...")
gi.hotkey("ctrl", "v")
time.sleep(1.0)
save("diag_2_after_paste")

# Step E: 读回剪贴板（看是否被覆盖）
rb2 = get_clipboard_text()
print(f"  [2d] Clipboard after paste: {rb2!r}")

# === 诊断4: 用 type_unicode 试试 ===
print(f"\n  [3] Try type_unicode as fallback")
# 先清空搜索框
gi.hotkey("ctrl", "a")
time.sleep(0.1)
gi.key_press("delete")
time.sleep(0.3)

# 用 unicode 方式
gi.type_unicode("雪雪")
time.sleep(1.0)
save("diag_3_after_unicode")

# === 诊断5: 用 SendInput 逐字符 ===
print(f"\n  [4] Try type_text non-clipboard (ASCII only)")
gi.hotkey("ctrl", "a")
time.sleep(0.1)
gi.key_press("delete")
time.sleep(0.3)

gi.type_text("test123", use_clipboard=False)
time.sleep(1.0)
save("diag_4_after_ascii")

# === 诊断6: 再试一次剪贴板方式，但增加延迟 ===
print(f"\n  [5] Clipboard paste with longer delays")
gi.hotkey("ctrl", "a")
time.sleep(0.1)
gi.key_press("delete")
time.sleep(0.3)

# 手动操作
set_clipboard_text("雪雪测试")
time.sleep(0.3)  # 更长延迟
print(f"  Clipboard content: {get_clipboard_text()!r}")

# 确保 Telegram 有焦点
ctypes.windll.user32.SetForegroundWindow(hwnd)
time.sleep(0.3)

# 重新点击搜索框确保焦点
gi.click(search_x, search_y)
time.sleep(0.5)

gi.hotkey("ctrl", "v")
time.sleep(1.5)
save("diag_5_paste_with_delay")

print("\n=== Diagnosis complete ===")
print(f"Screenshots in: {SCREENSHOT_DIR}")
