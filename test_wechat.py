import sys
import time
for _s in (sys.stdout, sys.stderr):
    _r = getattr(_s, "reconfigure", None)
    if _r:
        try: _r(encoding="utf-8", errors="replace")
        except: pass

from gui_monitor.utils.dpi import init_dpi
init_dpi()

from gui_monitor.core import input as gi
from gui_monitor.core import window as gw
from gui_monitor.core import screen as gs
import os

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots_debug")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def step(msg):
    print(f"\n---> {msg}")

# 1. 寻找并聚焦微信
step("寻找并聚焦 微信 窗口")
wins = gw.list_windows()
wechat_hwnd = None
wechat_title = None
for w in wins:
    if w["title"] == "微信":
        wechat_hwnd = w["hwnd"]
        wechat_title = w["title"]
        break

if not wechat_hwnd:
    print("未找到微信主窗口！")
    sys.exit(1)

gw.focus_window(wechat_title)
time.sleep(1.0)
gs.screenshot(save_path=os.path.join(SCREENSHOT_DIR, "wx_1_focus.png"))

# 2. 快捷键打开搜索 (微信全局/内部搜索都是 Ctrl+F)
step("按 Ctrl+F 打开搜索")
gi.hotkey("ctrl", "f")
time.sleep(1.5)
gs.screenshot(save_path=os.path.join(SCREENSHOT_DIR, "wx_2_search_open.png"))

# 3. 输入 文件传输助手 (使用拼音输入法)
# 因为微信搜索框不支持 Ctrl+V，且检测到用户当前是中文输入法状态，所以直接用拼音打汉字
step("输入拼音 '文件传输助手'")
gi.type_pinyin("文件传输助手", char_interval=0.08, confirm_delay=1.0)
time.sleep(1.0)
gs.screenshot(save_path=os.path.join(SCREENSHOT_DIR, "wx_3_typed.png"))

# 4. 选择并进入联系人
step("按 Down 6次 跳过网络搜索，选择 '功能' 下的联系人，按 Enter 进入聊天")
for _ in range(6):
    gi.key_press("down")
    time.sleep(0.1)

time.sleep(0.5)
gs.screenshot(save_path=os.path.join(SCREENSHOT_DIR, "wx_3_selected.png"))

gi.key_press("enter")
time.sleep(1.0)
gs.screenshot(save_path=os.path.join(SCREENSHOT_DIR, "wx_4_entered.png"))

# 5. 聊天界面自动聚焦在输入框，直接通过剪贴板输入长消息
step("输入测试消息 (使用剪贴板)")
msg = "测试消息：这是通过 Python 脚本自动发送的"
gi.type_text(msg, use_clipboard=True)
time.sleep(1.0)
gs.screenshot(save_path=os.path.join(SCREENSHOT_DIR, "wx_5_msg_typed.png"))

# 6. 按回车发送
step("按 Enter 发送")
gi.key_press("enter")
time.sleep(1.0)
gs.screenshot(save_path=os.path.join(SCREENSHOT_DIR, "wx_6_sent.png"))
print("Done")

