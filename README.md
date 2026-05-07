# Nova GUI Monitor

> Windows 电脑 GUI 自动化 CLI 工具 — 纯 Win32 API，零 GUI 依赖

通过命令行控制 Windows 桌面：截图、鼠标点击、键盘输入、窗口管理。专为 AI Agent 设计，所有输出均为 JSON 格式。

## ✨ 特性

- **纯 CLI** — 无需启动 GUI，直接命令行调用
- **纯 Win32 API** — 不依赖 pyautogui、PyQt 等第三方 GUI 库
- **DPI 感知** — 自动处理高分屏缩放，坐标精确
- **中文输入** — 支持剪贴板、拼音输入法、Unicode SendInput 三种方式
- **HTTP API** — 可选的 REST API 服务，支持远程控制
- **Chat Agent** — 集成 GPT-4o Vision 的聊天自动监控与回复（实验性）

## 📦 安装

```bash
# 克隆仓库
git clone https://github.com/Novansz/gui-monitor.git
cd gui-monitor

# 安装（推荐虚拟环境）
pip install .

# 带 Chat Agent 支持
pip install ".[chat]"
```

## 🚀 快速开始

```bash
# 查看帮助
python -m gui_monitor --help

# 屏幕信息
python -m gui_monitor info

# 截图保存
python -m gui_monitor screenshot --save screen.png

# 点击坐标 (500, 300)
python -m gui_monitor click 500 300

# 输入中文
python -m gui_monitor type "你好世界"

# 聚焦窗口
python -m gui_monitor focus "记事本"
```

## 📖 命令参考

| 命令 | 别名 | 功能 |
|------|------|------|
| `screenshot` | `ss` | 截取屏幕（支持全屏/区域/窗口） |
| `click` | | 点击指定坐标 |
| `move` | | 移动鼠标 |
| `drag` | | 拖拽操作 |
| `scroll` | | 滚轮滚动 |
| `type` | | 输入文本（支持中文） |
| `type-pinyin` | `tp` | 通过拼音输入法输入中文 |
| `type-unicode` | `tu` | 通过 Unicode SendInput 输入 |
| `key` | | 按键操作 |
| `hotkey` | | 组合键 |
| `windows` | `wl` | 列出所有窗口 |
| `focus` | | 聚焦窗口（支持模糊匹配） |
| `window-info` | `wi` | 获取窗口详细信息 |
| `foreground` | `fg` | 获取当前前台窗口 |
| `info` | | 屏幕和显示器信息 |
| `cursor` | `pos` | 当前鼠标位置 |
| `serve` | | 启动 HTTP API 服务 |
| `chat-agent` | `ca` | 聊天自动监控与回复 |
| `chat-learn` | `cl` | 从聊天记录学习风格 |

### 截图示例

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
# 右键点击
python -m gui_monitor click 500 300 --right

# 双击
python -m gui_monitor click 500 300 --double

# 平滑移动（0.5 秒缓动）
python -m gui_monitor move 800 600 --duration 0.5

# 拖拽
python -m gui_monitor drag 100 100 500 500 --duration 1.0

# 滚动（正=上，负=下）
python -m gui_monitor scroll -3 --x 500 --y 400
```

### 键盘操作

```bash
# 按 Enter
python -m gui_monitor key enter

# 组合键 Ctrl+C
python -m gui_monitor hotkey ctrl c

# 输入中文（通过剪贴板粘贴）
python -m gui_monitor type "你好世界"

# 通过拼音输入法
python -m gui_monitor type-pinyin "你好"

# 通过 Unicode SendInput
python -m gui_monitor type-unicode "你好世界🎉"
```

### 窗口管理

```bash
# 列出所有窗口
python -m gui_monitor windows

# JSON 格式输出
python -m gui_monitor windows --json

# 聚焦窗口（模糊匹配标题）
python -m gui_monitor focus "微信"

# 获取窗口信息
python -m gui_monitor window-info "Chrome"
```

## 🌐 HTTP API

```bash
# 启动 API 服务
python -m gui_monitor serve --port 8765
```

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/info` | 屏幕信息 |
| GET | `/screenshot` | 全屏截图 (JPEG) |
| GET | `/cursor` | 鼠标位置 |
| GET | `/windows` | 窗口列表 |
| POST | `/click` | 点击 `{x, y, button, clicks}` |
| POST | `/type` | 输入文本 `{text}` |
| POST | `/hotkey` | 组合键 `{keys: [...]}` |
| POST | `/focus` | 聚焦窗口 `{title}` |

## 🤖 Chat Agent（实验性）

集成 GPT-4o Vision 的聊天自动监控与回复系统：

```bash
# 设置 API Key
set OPENAI_API_KEY=sk-xxx

# 审核模式（推荐）— 每条回复需确认
python -m gui_monitor chat-agent --contact "Linda" --mode review

# 通知模式 — 仅提醒，不回复
python -m gui_monitor chat-agent --contact "群聊" --mode notify

# 自动模式 — 完全自动回复（谨慎使用）
python -m gui_monitor chat-agent --contact "Linda" --mode auto
```

## ⚙️ 系统要求

- **操作系统**: Windows 10 1703+ / Windows 11
- **Python**: 3.10+
- **DPI**: 自动适配（支持 100%~250% 缩放）

## 📄 License

[MIT](LICENSE)
