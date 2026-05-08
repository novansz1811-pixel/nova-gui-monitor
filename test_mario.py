import time
import os
from gui_monitor.core.input import hotkey, click, key_press, type_text
from gui_monitor.core.screen import screenshot

def create_mario():
    # 1. 最小化所有窗口，回到桌面
    print("Showing desktop...")
    hotkey('win', 'd')
    time.sleep(1.0)
    
    # 2. 在桌面空白处右键 (假设 1920, 1080 附近为空白)
    # 为了防止选中图标，先点一下旁边，再右键
    print("Right clicking on desktop...")
    click(2500, 1000, button="left")
    time.sleep(0.5)
    
    # 使用 Shift+F10 打开桌面右键菜单 (因为焦点在桌面)
    # 但是如果没选中任何东西，Shift+F10 确实会打开桌面菜单吗？
    # 更安全的方法：右键点击
    click(2500, 1000, button="right")
    time.sleep(1.0)
    
    # 截图看看右键菜单
    screenshot(save_path='screenshots_debug/mario_1_rc.png')
    
    # 在 Win11 中，如果弹出了新版菜单，"显示更多选项"快捷键是 Shift+F10，或者我们要按多次箭头。
    # 试试直接发送 Shift+F10 把新菜单转换为老菜单
    hotkey('shift', 'f10')
    time.sleep(1.0)
    screenshot(save_path='screenshots_debug/mario_2_classic_rc.png')
    
if __name__ == "__main__":
    create_mario()
