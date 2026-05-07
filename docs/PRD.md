# GUI Monitor - 产品需求文档 (PRD)

## 1. 产品概述

### 1.1 产品名称
GUI Monitor（GUI 电脑 App 自动化监控工具）

### 1.2 产品定位
一个 Windows 桌面工具，用于定义屏幕监控区域，并提供 HTTP API 供 Claude Code 或其他自动化脚本控制鼠标键盘操作。

### 1.3 目标用户
- 开发者：需要自动化测试 GUI 应用
- Claude Code 用户：需要让 AI 操作电脑屏幕
- RPA 开发者：需要快速定义操作区域

### 1.4 核心价值
- **区域选择**：可视化拖拽定义监控/操作区域
- **API 控制**：通过 HTTP API 远程控制鼠标键盘
- **DPI 兼容**：支持高分辨率屏幕（4K + 150%/175% 缩放）

---

## 2. 功能需求

### 2.1 区域选择窗口

| 功能 | 描述 | 状态 |
|------|------|------|
| 透明边框 | 窗口透明，只显示蓝色边框，底层内容可见 | ✅ 已实现 |
| 拖拽移动 | 拖拽窗口内部移动位置 | ✅ 已实现 |
| 拖拽调整大小 | 拖拽 8 个角落/边缘调整窗口大小 | ✅ 已实现 |
| 坐标显示 | 实时显示物理坐标和窗口尺寸 | ✅ 已实现 |
| 最小尺寸限制 | 窗口最小 100×80 像素 | ✅ 已实现 |

### 2.2 悬浮工具栏

| 功能 | 描述 | 状态 |
|------|------|------|
| 全屏按钮 | 切换到全屏监控模式 | ✅ 已实现 |
| 区域按钮 | 切换到区域选择模式 | ✅ 已实现 |
| 穿透/操作切换 | 切换鼠标穿透模式 | ✅ 已实现 |
| 坐标显示 | 实时显示鼠标坐标 | ✅ 已实现 |
| 关闭按钮 | 退出程序 | ✅ 已实现 |

### 2.3 HTTP API

| 接口 | 方法 | 描述 | 状态 |
|------|------|------|------|
| `/region` | GET | 获取当前监控区域坐标 | ✅ 已实现 |
| `/state` | GET | 获取鼠标状态 | ✅ 已实现 |
| `/screenshot` | GET | 获取当前截图 (PNG) | ✅ 已实现 |
| `/info` | GET | 获取屏幕尺寸和区域信息 | ✅ 已实现 |
| `/click` | POST | 点击指定坐标 | ✅ 已实现 |
| `/move` | POST | 移动鼠标 | ✅ 已实现 |
| `/drag` | POST | 拖拽操作 | ✅ 已实现 |
| `/scroll` | POST | 滚轮滚动 | ✅ 已实现 |
| `/key` | POST | 按键操作 | ✅ 已实现 |
| `/typewrite` | POST | 输入文本 | ✅ 已实现 |
| `/hotkey` | POST | 组合键 | ✅ 已实现 |

### 2.4 IPC 文件

| 文件 | 描述 | 状态 |
|------|------|------|
| `region.json` | 当前监控区域坐标 | ✅ 已实现 |
| `state.json` | 鼠标实时状态 | ✅ 已实现 |
| `screenshot.png` | 当前截图 | ✅ 已实现 |

---

## 3. 技术架构

### 3.1 技术栈
- **语言**: Python 3.12
- **GUI 框架**: PyQt6
- **截图**: QScreen.grabWindow() / mss
- **自动化**: pyautogui
- **HTTP 服务**: Python 内置 http.server

### 3.2 项目结构
```
GUI电脑app自动化/
├── run.py                   # 启动入口
├── requirements.txt         # 依赖
├── CLAUDE.md               # Claude Code 使用说明
├── PRD.md                  # 产品需求文档（本文件）
├── config.py               # 配置（已废弃，移至 gui_monitor/）
└── gui_monitor/
    ├── __init__.py
    ├── config.py           # 配置文件
    ├── main.py             # 主程序入口
    ├── region_selector.py  # 区域选择窗口
    ├── overlay_window.py   # 全屏覆盖层
    ├── control_bar.py      # 悬浮工具栏
    ├── api_server.py       # HTTP API 服务
    ├── ipc.py              # JSON 文件 IPC
    ├── screen_capture.py   # 屏幕截图
    └── dpi.py              # DPI 转换工具
```

### 3.3 关键技术点

#### 3.3.1 DPI 感知
- Windows 高分屏使用 150%/175% 缩放
- Qt geometry() 返回逻辑坐标
- pyautogui/mss 使用物理坐标
- 解决方案：`SetProcessDpiAwareness(2)` + 坐标转换

#### 3.3.2 透明窗口
- `WA_TranslucentBackground` 实现窗口透明
- 底层内容自然透过，无需截图循环
- 避免闪烁问题

---

## 4. 接口规范

### 4.1 HTTP API 详细说明

#### GET /region
返回当前监控区域坐标。
```json
{
  "x": 1520,
  "y": 780,
  "width": 800,
  "height": 600,
  "mode": "region",
  "timestamp": 1648123456.789
}
```

#### POST /click
点击指定坐标。
```json
// 请求
{
  "x": 500,
  "y": 300,
  "button": "left",    // left | right | middle
  "clicks": 1,          // 1 = 单击, 2 = 双击
  "delay": 0            // 延迟秒数
}
// 响应
{
  "success": true,
  "clicked": [500, 300]
}
```

#### POST /drag
拖拽操作。
```json
// 请求
{
  "start_x": 100,
  "start_y": 100,
  "end_x": 300,
  "end_y": 200,
  "duration": 0.5
}
```

#### POST /hotkey
组合键。
```json
// 请求
{
  "keys": ["ctrl", "c"]
}
```

#### POST /typewrite
输入文本。
```json
// 请求
{
  "text": "Hello World",
  "interval": 0.1
}
```

---

## 5. 使用场景

### 5.1 场景一：自动化测试
1. 启动 GUI Monitor
2. 拖拽选择要测试的区域
3. 通过 API 获取区域截图
4. 使用 pyautogui 进行自动化操作

### 5.2 场景二：Claude Code 操作
1. 启动 GUI Monitor
2. Claude Code 通过 `/region` 获取当前区域
3. Claude Code 通过 `/screenshot` 获取截图分析
4. Claude Code 通过 `/click`、`/typewrite` 等操作屏幕

### 5.3 场景三：RPA 脚本
1. 启动 GUI Monitor
2. 读取 `region.json` 获取监控区域
3. 使用 pyautogui 在区域内操作

---

## 6. 后续规划

### 6.1 短期优化
- [ ] 添加系统托盘图标
- [ ] 支持多显示器
- [ ] 添加快捷键支持

### 6.2 中期功能
- [ ] OCR 文字识别
- [ ] 图像匹配点击
- [ ] 录制/回放操作

### 6.3 长期规划
- [ ] 跨平台支持（macOS/Linux）
- [ ] 云端 API 服务
- [ ] AI 自动化助手

---

## 7. 更新日志

### v0.1.0 (2025-03-25)
- 初始版本
- 实现区域选择窗口
- 实现 HTTP API
- 实现透明边框方案（解决 DPI 和闪烁问题）
