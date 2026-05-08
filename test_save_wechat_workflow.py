import json
from gui_monitor.mcp_server import gui_save_workflow

steps = [
    {"name": "Focus WeChat", "command": "focus_window", "args": {"title": "微信"}, "wait_after": 0.5},
    {"name": "Open Search", "command": "hotkey", "args": {"keys": ["ctrl", "f"]}, "wait_after": 1.5},
    {"name": "Type Contact (Smart)", "command": "type_smart", "args": {"text": "{{contact_name}}"}, "wait_after": 1.0, "notes": "对于英文联系人，使用 type_text 然后按 Enter。对于中文联系人，使用 type_pinyin 并且等待输入法确认。"},
    {"name": "Enter Chat", "command": "key_press", "args": {"key": "enter"}, "wait_after": 1.0, "notes": "搜索普通联系人时，第一个搜索结果会自动选中，直接按 Enter 即可进入。如果是功能号(如文件传输助手)，需要按 Down 6次跳过网络搜索。"},
    {"name": "Type Message", "command": "type_text", "args": {"text": "{{message_content}}", "use_clipboard": True}, "wait_after": 1.0},
    {"name": "Send", "command": "key_press", "args": {"key": "enter"}, "wait_after": 1.0}
]

gotchas = [
    {"issue": "WeChat search does not accept Ctrl+V via keyboard shortcuts reliably", "solution": "Use pywin32 clipboard injection directly via use_clipboard=True in type_text, or type_pinyin for Chinese input."},
    {"issue": "WeChat network results push local results down", "solution": "Normal contacts are auto-selected on top. Functions require pressing down 6 times. For standard user chat, direct Enter is safe."}
]

params = {
    "search_delay": 1.5,
    "chat_open_delay": 1.0
}

result = gui_save_workflow(
    app_name="wechat",
    action="send_message_stable",
    steps=steps,
    gotchas=gotchas,
    params=params
)
print("Result:", json.loads(result))
