import time
from gui_monitor.core.input import hotkey, click, key_press, type_text
from gui_monitor.core.screen import screenshot
import subprocess

def draw_peach():
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
    
    vba_code = """Sub DrawPeach()
    Dim pixels As Variant
    pixels = Array( _
        "00000YYRYY000000", _
        "0000YYYYYY000000", _
        "000YYYYYYYY00000", _
        "00YYYOOOYYY00000", _
        "00YYYOOOOYYY0000", _
        "00YYYOKOOYYY0000", _
        "00YYYOOOOYYY0000", _
        "000YYOOROY000000", _
        "00000PPPP0000000", _
        "0000PPPPPP000000", _
        "000WPPPPPPW00000", _
        "0000PPPPPP000000", _
        "000PPPPPPPP00000", _
        "00PPPPPPPPPP0000", _
        "0PPPPPPPPPPPP000", _
        "0PPPPPPPPPPPP000")
        
    Range(Columns(15), Columns(30)).ColumnWidth = 2
    Range(Rows(1), Rows(16)).RowHeight = 15
    
    Dim r As Integer, c As Integer
    For r = 1 To 16
        For c = 1 To 16
            Dim p As String
            p = Mid(pixels(r - 1), c, 1)
            Dim colIndex As Integer
            colIndex = c + 14 ' 偏移14列，画在马里奥旁边 (15列开始)
            If p = "Y" Then Cells(r, colIndex).Interior.Color = RGB(255, 215, 0)
            If p = "R" Then Cells(r, colIndex).Interior.Color = RGB(255, 0, 0)
            If p = "O" Then Cells(r, colIndex).Interior.Color = RGB(255, 204, 153)
            If p = "K" Then Cells(r, colIndex).Interior.Color = RGB(0, 0, 0)
            If p = "P" Then Cells(r, colIndex).Interior.Color = RGB(255, 105, 180)
            If p = "W" Then Cells(r, colIndex).Interior.Color = RGB(255, 255, 255)
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
    screenshot(save_path='screenshots_debug/peach_done.png')

if __name__ == "__main__":
    draw_peach()
