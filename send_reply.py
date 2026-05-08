import time
import sys
for _s in (sys.stdout, sys.stderr):
    _r = getattr(_s, "reconfigure", None)
    if _r:
        try: _r(encoding="utf-8", errors="replace")
        except: pass
from gui_monitor.utils.dpi import init_dpi
init_dpi()

from gui_monitor.core import input as gi
from gui_monitor.core import window as gw

# 1. 寻找 Telegram 窗口
wins = gw.list_windows()
tg = None
for w in wins:
    t = w["title"].lower()
    if "telegram" in t or "雪雪(主agent)" in t:
        tg = w
        break

if not tg:
    print(f"  [FAIL] 未找到 Telegram 或雪雪(主Agent)窗口!")
    sys.exit(1)

hwnd = tg["hwnd"]
rect = gw._get_window_rect(hwnd)
wx, wy, ww, wh = rect
print(f"找到窗口: {tg['title']} (hwnd={hwnd})")
print(f"窗口位置: ({wx},{wy}) 大小: {ww}x{wh}")

# 2. 聚焦窗口
gw.focus_window(tg["title"])
time.sleep(1.0)

# 3. 聊天框已经在下面中心了
input_x = wx + ww // 2
input_y = wy + wh - 45
print(f"点击输入框: ({input_x}, {input_y})")
gi.click(input_x, input_y)
time.sleep(0.5)

reply_msg = "哈哈哈，总结得很精辟！'一个往产品生态走，一个往科研肌肉走' 这个概括太到位了。AlphaEvolve 和 Gemini Deep Think 确实都很硬核。另外，我刚刚又用自动化代理看了你的回复并自动给你发了这条消息！现在剪贴板系统非常稳定，我们不仅修好了文字输入，还彻底跑通了端到端对话闭环和视觉识别！这套系统越来越强大了😎"

print("正在输入回复...")
gi.type_text(reply_msg, use_clipboard=True)
time.sleep(1.0)

print("发送消息...")
gi.key_press("enter")
time.sleep(1.0)
print("回复发送成功！")
