# GUI Monitor v2 — Claude Code / AI Agent 使用说明

本项目是一个 Windows 电脑自动化 CLI 工具，AI Agent 可通过命令行直接控制屏幕操作。

**无需启动 GUI、无需 HTTP 服务 — 直接命令行调用。**

## 快速开始

```bash
cd "C:/Users/Novansz/OneDrive/产品开发/软件/GUI电脑app自动化"

# 查看帮助
python -m gui_monitor --help

# 查看屏幕信息
python -m gui_monitor info

# 截图
python -m gui_monitor screenshot --save screen.png
```

## 所有命令

### 截图

```bash
# 全屏截图
python -m gui_monitor screenshot --save screen.png

# 区域截图（物理坐标 x,y,width,height）
python -m gui_monitor screenshot --region 100,200,800,600 --save region.png

# 按窗口标题截图
python -m gui_monitor screenshot --window "记事本" --save notepad.png

# 输出 Base64（适合 API 调用）
python -m gui_monitor screenshot --base64
```

### 鼠标操作

```bash
# 左键单击
python -m gui_monitor click 500 300

# 右键
python -m gui_monitor click 500 300 --right

# 双击
python -m gui_monitor click 500 300 --double

# 移动鼠标
python -m gui_monitor move 500 300

# 平滑移动（0.5 秒）
python -m gui_monitor move 500 300 --duration 0.5

# 拖拽（从 100,100 到 300,200）
python -m gui_monitor drag 100 100 300 200

# 滚轮（正=上, 负=下）
python -m gui_monitor scroll -3
python -m gui_monitor scroll 5 --x 500 --y 300
```

### 键盘操作

```bash
# 按键
python -m gui_monitor key enter
python -m gui_monitor key tab
python -m gui_monitor key f5
python -m gui_monitor key a --presses 5

# 组合键
python -m gui_monitor hotkey ctrl c
python -m gui_monitor hotkey ctrl shift s
python -m gui_monitor hotkey alt f4

# 输入文本（支持中文！）
python -m gui_monitor type "Hello World"
python -m gui_monitor type "你好世界"

# ASCII 模式（逐字符按键，不走剪贴板）
python -m gui_monitor type "hello" --ascii
```

### 窗口管理

```bash
# 列出所有窗口
python -m gui_monitor windows

# JSON 格式输出
python -m gui_monitor windows --json

# 聚焦窗口（支持模糊匹配）
python -m gui_monitor focus "记事本"
python -m gui_monitor focus "Chrome"

# 获取窗口信息
python -m gui_monitor window-info "记事本"

# 获取当前前台窗口
python -m gui_monitor foreground
```

### 屏幕信息

```bash
# 屏幕尺寸、DPI、显示器列表
python -m gui_monitor info

# 当前鼠标位置
python -m gui_monitor cursor
```

### HTTP API 服务（可选，兼容 v1）

```bash
# 启动 HTTP API 服务
python -m gui_monitor serve --port 8765
```

### 聊天代理（Chat Agent）

```bash
# 监控微信联系人（审核模式 — 默认）
python -m gui_monitor chat-agent --contact "Linda" --api-key sk-xxx

# 自动回复群聊
python -m gui_monitor chat-agent -c "四条龙" -m auto --interval 15

# 仅通知模式（不回复，只报告新消息）
python -m gui_monitor chat-agent -c "王哥" -m notify -i 10

# 使用自定义风格配置
python -m gui_monitor chat-agent -c "Linda" --style my_style.yaml

# 指定发送快捷键
python -m gui_monitor chat-agent -c "Linda" --send-key "ctrl enter"
```

### 风格学习

```bash
# 从聊天记录学习用户说话风格
python -m gui_monitor chat-learn

# 指定聊天记录目录和输出路径
python -m gui_monitor chat-learn --history ./my_chats --output my_style.yaml
```

### 拼音输入（中文搜索框）

```bash
# 通过拼音输入法输入中文（适合微信搜索框等 Qt 控件）
python -m gui_monitor type-pinyin 四条龙

# 通过 Unicode SendInput 输入（适合标准控件）
python -m gui_monitor type-unicode 你好世界
```

## 常用操作示例

### 打开程序并输入

```bash
# 1. 聚焦窗口
python -m gui_monitor focus "记事本"

# 2. 输入文本
python -m gui_monitor type "自动化测试内容"

# 3. 保存（Ctrl+S）
python -m gui_monitor hotkey ctrl s
```

### 截图 → 分析 → 点击

```bash
# 1. 截图
python -m gui_monitor screenshot --save current.png

# 2. AI 分析截图，确定目标坐标...

# 3. 点击目标
python -m gui_monitor click 1500 800
```

### 窗口操作

```bash
# 1. 列出窗口找目标
python -m gui_monitor windows --json

# 2. 聚焦目标窗口
python -m gui_monitor focus "目标窗口"

# 3. 获取窗口位置进行区域截图
python -m gui_monitor window-info "目标窗口"
python -m gui_monitor screenshot --window "目标窗口" --save target.png
```

### 微信群聊自动化

```bash
# 1. 搜索并打开群聊
python -m gui_monitor focus 微信
python -m gui_monitor hotkey ctrl f          # 打开搜索
sleep 2
python -m gui_monitor type-pinyin 四条龙     # 拼音输入中文
sleep 2
python -m gui_monitor key enter              # 选择结果

# 2. 发送消息
python -m gui_monitor type "你好大家"         # 剪贴板输入（聊天框支持）
python -m gui_monitor hotkey alt s           # 发送

# 3. 或使用集成代理自动监控
python -m gui_monitor chat-agent -c "四条龙" -m review
```

## 输出格式

所有命令输出 **JSON 格式**，方便 AI 解析：

```json
{"success": true, "x": 500, "y": 300, "button": "left", "clicks": 1}
```

错误时输出到 stderr：
```json
{"error": "未找到窗口: '不存在'", "type": "ValueError"}
```

## 坐标系

> **所有坐标均为物理像素坐标**（DPI Aware 模式）。
> 
> 你的屏幕: 3840x2160, DPI 缩放 175%
>
> 坐标范围: (0,0) 到 (3839, 2159)

## 项目结构 (v2)

```
GUI电脑app自动化/
├── gui_monitor/
│   ├── __init__.py          # 包初始化（轻量）
│   ├── __main__.py          # CLI 入口：python -m gui_monitor
│   ├── cli.py               # 命令行解析（18 个子命令）
│   ├── chat_agent.py        # 聊天代理（监控/回复/风格学习）
│   ├── server.py            # HTTP API 服务（可选）
│   ├── core/
│   │   ├── screen.py        # 截图（mss）
│   │   ├── input.py         # 鼠标键盘（Win32 API + 拼音输入）
│   │   └── window.py        # 窗口管理（Win32 API）
│   └── utils/
│       ├── dpi.py           # DPI 工具
│       └── clipboard.py     # 剪贴板（中文输入）
├── chat_agent_data/
│   ├── workflows/           # Workflow Recipes（操作经验）
│   │   ├── workflow_wechat_search_contact.yaml
│   │   └── workflow_wechat_send_message.yaml
│   ├── history/             # 聊天记录（风格学习用）
│   ├── logs/                # 自动回复日志
│   ├── screenshots/         # 截图缓存
│   └── style_profile.yaml   # 风格配置
├── run.py                   # v1 GUI 启动入口（保留）
└── requirements.txt         # 依赖
```

## 依赖

v2 最小依赖：
- `mss` — 高性能截图
- `Pillow` — 图片处理
- `pypinyin` — 中文拼音转换（type-pinyin 命令）
- `pyyaml` — YAML 配置读写

Chat Agent 额外依赖：
- `openai` — GPT-4o 视觉分析

v1 GUI 额外依赖（仅 run.py 需要）：
- `PyQt6` / `pyautogui` / `opencv-python` / `numpy`

## 输入法策略

| 场景 | 方法 | 命令 |
|------|------|------|
| 标准输入框 + 中文 | 剪贴板粘贴 | `type "中文"` |
| 微信搜索框 + 中文 | 拼音输入法 | `type-pinyin 中文` |
| 标准控件 + Unicode | SendInput Unicode | `type-unicode 文本` |
| 任何地方 + ASCII | 逐字符按键 | `type "hello" --ascii` |

