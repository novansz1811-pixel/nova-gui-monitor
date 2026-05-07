"""
Chat Agent — 聊天自动监控与智能回复模块

集成在 gui_monitor 内部，直接调用 core API，无需 subprocess。

用法:
    python -m gui_monitor chat-agent --contact "Linda" --mode review
    python -m gui_monitor chat-agent --contact "四条龙" --mode notify --interval 15

依赖:
    - openai (pip install openai)
    - pypinyin (pip install pypinyin)  # 中文联系人搜索时需要
    - pyyaml (pip install pyyaml)
"""

import base64
import hashlib
import json
import os
import re
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

# ─── 路径配置 ──────────────────────────────────────────────

# 数据目录放在项目根目录下
_MODULE_DIR = Path(__file__).parent        # gui_monitor/
_PROJECT_ROOT = _MODULE_DIR.parent         # GUI电脑app自动化/
DATA_DIR = _PROJECT_ROOT / "chat_agent_data"
LOG_DIR = DATA_DIR / "logs"
SCREENSHOT_DIR = DATA_DIR / "screenshots"
HISTORY_DIR = DATA_DIR / "history"
STYLE_FILE = DATA_DIR / "style_profile.yaml"

# 微信发送快捷键
WECHAT_SEND_KEYS = ["alt", "s"]


# ─── 工具函数 ──────────────────────────────────────────────

def _ensure_dirs():
    """确保数据目录存在。"""
    for d in [DATA_DIR, LOG_DIR, SCREENSHOT_DIR, HISTORY_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def _is_ascii(text: str) -> bool:
    """判断文本是否全为 ASCII 字符。"""
    return all(ord(c) < 128 for c in text)


def image_to_base64(path: str) -> str:
    """图片转 Base64。"""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def image_hash(path: str) -> str:
    """计算图片文件的 SHA256 哈希（用于快速比对画面变化）。"""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def log_message(contact: str, direction: str, content: str):
    """记录消息日志。"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"{datetime.now():%Y-%m-%d}.log"
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] [{contact}] [{direction}] {content}\n"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)

    print(f"  📝 {line.strip()}")


def load_style_profile(style_path: Path | None = None) -> dict:
    """加载风格配置。"""
    path = style_path or STYLE_FILE
    if not path.exists():
        return {}
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("style_profile", data) if data else {}
    except ImportError:
        # 没有 pyyaml，尝试 JSON 格式
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    except Exception:
        return {}


# ─── 微信导航 ──────────────────────────────────────────────

def navigate_to_contact(contact: str):
    """在微信中搜索并打开指定联系人/群聊。
    
    自动判断联系人名称是否包含中文：
    - ASCII → 直接逐字符输入（如 "Linda"）
    - 中文 → 使用系统拼音输入法键入（如 "四条龙"）
    """
    from .core.window import focus_window
    from .core.input import hotkey, key_press, type_text, type_pinyin

    # 1. 聚焦微信
    print(f"  🔍 正在搜索联系人: {contact}")
    result = focus_window("微信")
    if not result.get("success"):
        print(f"  ❌ 无法聚焦微信窗口", file=sys.stderr)
        return False
    time.sleep(1)

    # 2. Ctrl+F 打开搜索
    hotkey("ctrl", "f")
    time.sleep(2)

    # 3. 输入联系人名称
    if _is_ascii(contact):
        # ASCII 联系人直接逐字符键入
        type_text(contact, use_clipboard=False)
    else:
        # 中文联系人通过拼音输入法
        type_pinyin(contact)

    time.sleep(2)

    # 4. 按 Enter 选择第一个结果
    key_press("enter")
    time.sleep(1)

    # 5. Escape 关掉搜索面板
    key_press("escape")
    time.sleep(0.5)

    print(f"  ✅ 已打开联系人: {contact}")
    return True


# ─── 截图 ──────────────────────────────────────────────────

def screenshot_chat(save_path: str) -> bool:
    """截图微信聊天窗口。"""
    from .core.screen import screenshot
    from .core.window import focus_window

    result = focus_window("微信")
    if not result.get("success"):
        return False

    try:
        region = (result["x"], result["y"], result["width"], result["height"])
        data = screenshot(region=region, save_path=save_path)
        return bool(data)
    except Exception as e:
        print(f"  ❌ 截图失败: {e}", file=sys.stderr)
        return False


# ─── AI 视觉分析 ───────────────────────────────────────────

def analyze_screenshot(
    image_path: str,
    style_profile: dict,
    contact: str,
    api_key: str,
) -> dict:
    """用 AI 视觉 API 分析聊天截图。
    
    返回:
        {
            "has_new_message": bool,
            "last_message_from": "contact" | "me",
            "last_message_text": str,
            "suggested_reply": str | None,
            "confidence": float
        }
    """
    try:
        from openai import OpenAI
    except ImportError:
        print("  ❌ 需要 openai 库: pip install openai", file=sys.stderr)
        return {"has_new_message": False, "confidence": 0}

    client = OpenAI(api_key=api_key)
    b64_image = image_to_base64(image_path)

    # 构建风格提示
    style_prompt = ""
    if style_profile:
        style_prompt = f"""
你需要模仿用户的聊天风格来回复。用户的风格特征：
- 语气：{style_profile.get('tone', '随意')}
- 句子长度：{style_profile.get('sentence_length', '短')}
- 口头禅：{', '.join(style_profile.get('filler_words', []))}
- 标点习惯：{style_profile.get('punctuation_style', '正常')}
- Emoji 使用：{style_profile.get('emoji_usage', '适中')}
- 标志性用语：{', '.join(style_profile.get('signature_phrases', []))}

示例对话：
"""
        for ex in style_profile.get("example_exchanges", [])[:5]:
            style_prompt += f"  对方：{ex.get('received', '')}\n"
            style_prompt += f"  用户回复：{ex.get('replied', '')}\n"

    messages = [
        {
            "role": "system",
            "content": f"""你是一个聊天截图分析助手。分析微信聊天截图并返回 JSON。

任务：
1. 识别截图中的聊天内容
2. 判断最新一条消息是对方发的还是用户发的
3. 如果最新消息来自对方（联系人：{contact}），生成一条合适的回复

{style_prompt}

严格返回以下 JSON 格式（不要加 markdown 标记）：
{{
    "has_new_message": true/false,
    "last_message_from": "contact" 或 "me",
    "last_message_text": "最新消息的内容",
    "suggested_reply": "建议的回复内容（仅当需要回复时）",
    "confidence": 0.0-1.0
}}

如果无法识别内容，设 confidence 为 0 且 has_new_message 为 false。
不要回复涉及金钱、密码、隐私的消息，此时 suggested_reply 设为 null。"""
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"分析这张微信聊天截图。联系人是 {contact}。"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{b64_image}",
                        "detail": "high",
                    },
                },
            ],
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=500,
        temperature=0.7,
    )

    reply_text = response.choices[0].message.content.strip()

    # 清理可能的 markdown 包裹
    if reply_text.startswith("```"):
        reply_text = reply_text.split("\n", 1)[1]
        reply_text = reply_text.rsplit("```", 1)[0]

    try:
        return json.loads(reply_text)
    except json.JSONDecodeError:
        print(f"  ⚠️ AI 返回解析失败: {reply_text[:200]}", file=sys.stderr)
        return {"has_new_message": False, "confidence": 0}


# ─── 发送消息 ──────────────────────────────────────────────

def send_reply(text: str) -> bool:
    """通过 GUI 自动化在当前聊天窗口发送回复。"""
    from .core.window import focus_window
    from .core.input import type_text, hotkey

    # 确保微信在前台
    focus_window("微信")
    time.sleep(0.5)

    # 输入文本（通过剪贴板，支持中文）
    type_text(text, use_clipboard=True)
    time.sleep(0.3)

    # 发送
    hotkey(*WECHAT_SEND_KEYS)
    time.sleep(0.3)

    return True


# ─── 主监控循环 ────────────────────────────────────────────

def monitor_loop(
    contact: str,
    interval: int = 10,
    mode: str = "review",
    api_key: str = "",
    style_path: str | None = None,
    send_key: str = "alt s",
):
    """主监控循环。
    
    Args:
        contact: 联系人名称
        interval: 截图间隔（秒）
        mode: "auto" | "review" | "notify"
        api_key: OpenAI API Key
        style_path: 风格配置文件路径
        send_key: 发送快捷键（如 "alt s" 或 "ctrl enter"）
    """
    global WECHAT_SEND_KEYS
    WECHAT_SEND_KEYS = send_key.split()

    _ensure_dirs()

    # 加载风格
    sp = Path(style_path) if style_path else None
    style_profile = load_style_profile(sp)
    if style_profile:
        print(f"  ✅ 已加载风格配置")
    else:
        print(f"  ⚠️ 未找到风格配置，将使用默认风格")

    # 导航到联系人
    if not navigate_to_contact(contact):
        print("  ❌ 无法打开联系人，退出", file=sys.stderr)
        return

    print(f"\n🤖 开始监控 [{contact}]")
    print(f"   模式: {mode} | 间隔: {interval}秒")
    print(f"   按 Ctrl+C 停止\n")

    last_hash = ""
    reply_count = 0
    minute_start = time.time()

    try:
        while True:
            # 频率限制重置
            if time.time() - minute_start > 60:
                reply_count = 0
                minute_start = time.time()

            # 截图
            ss_path = str(SCREENSHOT_DIR / "current.png")
            from .core.window import focus_window
            focus_window("微信")
            time.sleep(0.5)

            if not screenshot_chat(ss_path):
                print("  ❌ 截图失败，跳过")
                time.sleep(interval)
                continue

            # 快速判断画面是否变化
            current_hash = image_hash(ss_path)
            if current_hash == last_hash:
                time.sleep(interval)
                continue

            last_hash = current_hash
            print(f"  📸 [{datetime.now():%H:%M:%S}] 画面变化，分析中...")

            # AI 分析
            analysis = analyze_screenshot(ss_path, style_profile, contact, api_key)

            has_new = analysis.get("has_new_message", False)
            from_who = analysis.get("last_message_from", "")
            last_msg = analysis.get("last_message_text", "")
            reply = analysis.get("suggested_reply")
            confidence = analysis.get("confidence", 0)

            print(f"  📨 新消息: {has_new} | 来自: {from_who} | 置信度: {confidence}")
            if last_msg:
                print(f"  💬 最新: {last_msg}")

            if not has_new or from_who != "contact" or not reply:
                time.sleep(interval)
                continue

            if confidence < 0.6:
                print(f"  ⚠️ 置信度过低 ({confidence})，跳过")
                time.sleep(interval)
                continue

            if reply_count >= 3:
                print("  ⚠️ 达到每分钟回复上限 (3条)，跳过")
                time.sleep(interval)
                continue

            log_message(contact, "收到", last_msg)

            # 根据模式处理
            if mode == "notify":
                print(f"  🔔 [通知] 建议回复: {reply}")
                log_message(contact, "建议", reply)

            elif mode == "review":
                print(f"\n  ✏️ 建议回复: {reply}")
                try:
                    confirm = input("  发送？(y/n/自定义内容): ").strip()
                except EOFError:
                    confirm = "n"

                if confirm.lower() == "y":
                    send_reply(reply)
                    reply_count += 1
                    log_message(contact, "发送", reply)
                elif confirm.lower() == "n":
                    print("  ⏭️ 已跳过")
                elif confirm:
                    send_reply(confirm)
                    reply_count += 1
                    log_message(contact, "发送", confirm)

            elif mode == "auto":
                print(f"  🚀 自动回复: {reply}")
                send_reply(reply)
                reply_count += 1
                log_message(contact, "自动发送", reply)

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\n🛑 监控已停止")
        print(f"📋 日志: {LOG_DIR}")


# ─── 风格学习 ──────────────────────────────────────────────

def learn_style(history_dir: str | None = None, output: str | None = None):
    """从聊天记录中分析并生成风格配置。
    
    Args:
        history_dir: 聊天记录目录
        output: 输出文件路径
    """
    _ensure_dirs()
    hdir = Path(history_dir) if history_dir else HISTORY_DIR
    outpath = Path(output) if output else STYLE_FILE

    # 收集所有文本文件
    texts = []
    if hdir.exists():
        for f in hdir.iterdir():
            if f.suffix in (".txt", ".log", ".md", ".html"):
                try:
                    texts.append(f.read_text(encoding="utf-8"))
                except Exception:
                    pass

    if not texts:
        print(f"  ❌ 未找到聊天记录。请将文件放到: {hdir}")
        print(f"     支持格式: .txt, .log, .md, .html")
        return None

    combined = "\n---\n".join(texts)
    print(f"  📖 已读取 {len(texts)} 个聊天记录文件")
    print(f"  📏 总长度: {len(combined)} 字符")
    print(f"  💾 输出到: {outpath}")

    return {
        "texts": combined,
        "output_path": str(outpath),
        "file_count": len(texts),
    }
