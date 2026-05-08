import json
from gui_monitor.mcp_server import gui_save_workflow

steps = [
    {"name": "Focus Telegram", "command": "focus_window", "args": {"title": "Telegram"}},
    {"name": "Clear search", "command": "hotkey", "args": {"keys": ["ctrl", "a"]}},
    {"name": "Delete search", "command": "key_press", "args": {"key": "delete"}},
    {"name": "Search contact", "command": "type_text", "args": {"text": "雪雪(主Agent)"}, "wait_after": 2.0},
    {"name": "Open chat", "command": "key_press", "args": {"key": "enter"}, "wait_after": 1.0},
    {"name": "Focus input", "command": "click", "args": {"relative_x": 0.5, "relative_y": -45}},
    {"name": "Type message", "command": "type_text", "args": {"use_clipboard": True}},
    {"name": "Send", "command": "key_press", "args": {"key": "enter"}, "wait_after": 1.0}
]

gotchas = [
    {"issue": "Clicking arbitrary coordinates for search results is unreliable", "solution": "Use 'Enter' key to select the first search result"}
]

params = {
    "search_delay": 2.0,
    "chat_open_delay": 1.0
}

result = gui_save_workflow(
    app_name="telegram",
    action="send_message",
    steps=steps,
    gotchas=gotchas,
    params=params
)
print("Result:", json.loads(result))
