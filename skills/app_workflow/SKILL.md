---
name: app_workflow
description: |
  GUI 自动化工具使用经验自动总结。当通过 gui_monitor 成功跑通某个特定 App 的操作流程后，
  自动提取关键步骤、坐标、时序参数和踩过的坑，生成结构化的 Workflow Recipe，
  供后续复用、调试和优化。支持微信、计算器、浏览器等任意 Windows 应用。
---

# App Workflow — 工具使用经验自动总结

## 概述

当 AI 助手通过 GUI 自动化工具（`gui_monitor`）成功完成了对某个 App 的操作后，
应主动触发本 Skill 来总结并保存操作经验。

**核心价值**：避免重复踩坑，积累自动化知识库。

---

## 触发条件

以下情况**必须**触发本 Skill：

1. 成功完成了对某个 App 的完整操作流程（如：微信搜索联系人并发送消息）
2. 经过多次试错后找到了有效方案
3. 发现了某个 App 的特殊行为（如：微信搜索框不接受 Ctrl+V）
4. 用户明确要求"总结一下"

---

## 输出格式

### Workflow Recipe 结构

每个 Recipe 保存到 `<workspace>/chat_agent_data/workflows/` 目录：

```yaml
# workflow_<app>_<action>.yaml
app: "微信"                          # 应用名称
app_class: "WeChatMainWndForPC"     # 窗口类名（可选）
action: "search_contact"             # 操作名称
version: 2                           # Recipe 版本号
created: "2026-05-07"
updated: "2026-05-07"
status: "verified"                   # verified / experimental / deprecated

# 环境要求
prerequisites:
  - "微信已登录并在前台"
  - "系统输入法设置为中文拼音"
  - "pypinyin 已安装"

# 操作步骤
steps:
  - name: "聚焦微信窗口"
    command: "focus '微信'"
    wait_after: 1.0                  # 步骤后等待秒数
    notes: "使用模糊匹配标题"

  - name: "打开搜索框"
    command: "hotkey ctrl f"
    wait_after: 2.0
    notes: "必须等搜索面板完全展开"

  - name: "输入联系人名称"
    command: "type_pinyin '四条龙'"   # 或 type "linda" --ascii
    wait_after: 2.0
    method_selection:
      ascii: "联系人名全为 ASCII 字符时使用 type --ascii"
      pinyin: "联系人名包含中文时使用 type_pinyin"
      clipboard: "❌ 不可用 — 微信搜索框不接受 Ctrl+V"
      unicode: "❌ 不可用 — 微信 Qt 搜索框不响应 KEYEVENTF_UNICODE"

  - name: "选择搜索结果"
    command: "key enter"
    wait_after: 1.0
    notes: "普通联系人自动处于选中状态，不需要按 Down 键。仅当搜索文件传输助手等非优先项时才需要 Down 键。"

  - name: "关闭搜索面板"
    command: "key escape"
    wait_after: 0.5

# 已知陷阱
gotchas:
  - issue: "微信搜索框不接受 Ctrl+V 粘贴"
    root_cause: "微信使用自定义 Qt 输入框，拦截了标准 WM_PASTE"
    solution: "使用系统拼音输入法逐字母键入"
    discovered: "2026-05-07"

  - issue: "KEYEVENTF_UNICODE SendInput 无法在微信搜索框中输入"
    root_cause: "Qt 控件不处理 WM_UNICHAR/IME 之外的 Unicode 注入"
    solution: "改用系统 IME 拼音方案"
    discovered: "2026-05-07"

  - issue: "搜索面板展开后直接键入可能被忽略"
    root_cause: "搜索框动画完成前焦点尚未就绪"
    solution: "Ctrl+F 后等待至少 2 秒"
    discovered: "2026-05-07"

# 时序参数（经验值）
timing:
  focus_delay: 1.0            # 聚焦后等待
  search_open_delay: 2.0      # 搜索框展开后等待
  typing_delay: 0.08           # 拼音字母间隔
  ime_confirm_delay: 0.5       # IME 候选确认延时
  result_select_delay: 1.0     # 选择结果后等待
  send_delay: 0.3              # 发送后等待

# 可靠性评分
reliability:
  success_rate: "90%"          # 预估成功率
  failure_mode: "IME候选未命中目标汉字"
  recovery: "Escape 清空搜索框后重试"
```

---

## AI 助手执行流程

### 操作前：检查已有 Recipe

```
1. 查看 chat_agent_data/workflows/ 目录
2. 是否有匹配当前 App + Action 的 Recipe？
3. 有 → 按 Recipe 执行，跳过探索
4. 无 → 进入探索模式，操作完成后触发本 Skill 总结
```

### 操作后：生成/更新 Recipe

```
1. 回顾整个操作过程中的命令序列
2. 标记每个步骤的等待时间和失败点
3. 记录所有踩过的坑（gotchas）
4. 生成 YAML Recipe 并保存
5. 如果已有旧 Recipe，更新版本号和 updated 日期
```

---

## 快捷指令

| 指令 | 动作 |
|------|------|
| "总结一下刚才的操作" | 生成当前操作的 Workflow Recipe |
| "有没有操作过微信/计算器/浏览器" | 查找并展示已有 Recipe |
| "用之前的经验打开微信搜索" | 按已有 Recipe 执行 |
| "更新这个 Recipe" | 修改已有 Recipe 的参数 |

---

## 数据目录

```
chat_agent_data/
├── workflows/                # Workflow Recipes
│   ├── workflow_wechat_search_contact.yaml
│   ├── workflow_wechat_send_message.yaml
│   ├── workflow_calculator_basic.yaml
│   └── ...
├── history/                  # 聊天记录（风格学习用）
├── style_profile.yaml        # 风格配置
├── logs/                     # 日志
└── screenshots/              # 截图缓存
```

---

## 注意事项

1. **Recipe 是经验沉淀**：每次成功操作都应更新对应的 timing 参数
2. **版本管理**：Recipe 有版本号，方便跟踪演变
3. **失败也是经验**：`gotchas` 部分专门记录踩过的坑
4. **时序是关键**：`timing` 参数是自动化成功率的核心，应根据实际环境微调
5. **环境差异**：不同电脑的微信版本、系统输入法可能导致不同表现
