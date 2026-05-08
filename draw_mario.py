import time
from gui_monitor.core.input import hotkey, click, key_press, type_text
from gui_monitor.core.screen import screenshot
import subprocess

def draw_mario():
    print("聚焦 Excel 窗口...")
    # 使用 gui_monitor focus 命令聚焦
    subprocess.run(["python", "-m", "gui_monitor", "focus", "Excel"])
    time.sleep(1.0)
    
    print("打开 VBA 编辑器 (Alt+F11)...")
    hotkey('alt', 'f11')
    time.sleep(2.0)
    
    print("插入模块 (Alt+I, 然后 M)...")
    hotkey('alt', 'i')
    time.sleep(0.5)
    key_press('m')
    time.sleep(1.0)
    
    vba_code = """Sub DrawMario()
    Dim pixels As Variant
    pixels = Array( _
        "000RRRRR0000", _
        "00RRRRRRRRR0", _
        "00BBBOOOB000", _
        "0BBOOOOBBB00", _
        "0BBOOOOOOBBB", _
        "00BBOOOOB000", _
        "000OOOOOO000", _
        "00RRURRR0000", _
        "0RRRURRRR000", _
        "RRRRUUUURRR0", _
        "OORRUYUYRROO", _
        "OOORUUUUROOO", _
        "00UUUUUU0000", _
        "00BB00BB0000", _
        "0BBB00BBB000", _
        "000000000000")
        
    Cells.ColumnWidth = 2
    Cells.RowHeight = 15
    
    Dim r As Integer, c As Integer
    For r = 1 To 16
        For c = 1 To 12
            Dim p As String
            p = Mid(pixels(r - 1), c, 1)
            If p = "R" Then Cells(r, c).Interior.Color = RGB(255, 0, 0)
            If p = "B" Then Cells(r, c).Interior.Color = RGB(139, 69, 19)
            If p = "O" Then Cells(r, c).Interior.Color = RGB(255, 204, 153)
            If p = "Y" Then Cells(r, c).Interior.Color = RGB(255, 255, 0)
            If p = "U" Then Cells(r, c).Interior.Color = RGB(0, 0, 255)
        Next c
    Next r
End Sub
"""
    
    print("输入 VBA 代码...")
    type_text(vba_code, use_clipboard=True)
    time.sleep(1.0)
    
    print("运行代码 (F5)...")
    key_press('f5')
    time.sleep(2.0)
    
    print("关闭 VBA 编辑器 (Alt+F4)...")
    hotkey('alt', 'f4')
    time.sleep(1.0)
    
    print("完成！截图保存。")
    screenshot(save_path='screenshots_debug/mario_done.png')

if __name__ == "__main__":
    draw_mario()
