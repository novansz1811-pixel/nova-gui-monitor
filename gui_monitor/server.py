"""
HTTP API 服务 — v2 版

保持与 v1 API 路径兼容，但内部使用 v2 核心模块。
使用 ThreadingHTTPServer 支持并发请求。
"""

import json
import time
import base64
import sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

from .core import screen, input as inp, window
from .utils.dpi import get_screen_size, get_cursor_pos, get_dpi_scale


class APIHandler(BaseHTTPRequestHandler):
    """HTTP API 请求处理器。"""
    
    def log_message(self, format, *args):
        """简化日志。"""
        print(f"[API] {self.command} {self.path}", file=sys.stderr)
    
    def _send_json(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    
    def _read_body(self) -> dict:
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0:
            return {}
        body = self.rfile.read(content_len)
        return json.loads(body) if body else {}
    
    def do_OPTIONS(self):
        """CORS 预检。"""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self):
        try:
            self._handle_get()
        except Exception as e:
            self._send_json({"error": str(e), "type": type(e).__name__}, 500)
    
    def do_POST(self):
        try:
            self._handle_post()
        except Exception as e:
            self._send_json({"error": str(e), "type": type(e).__name__}, 500)
    
    def _handle_get(self):
        path = self.path.split("?")[0]  # 去掉查询参数
        
        if path == "/info":
            w, h = get_screen_size()
            self._send_json({
                "screen_width": w,
                "screen_height": h,
                "dpi_scale": get_dpi_scale(),
            })
        
        elif path == "/screenshot":
            img_bytes = screen.screenshot(format="jpeg", quality=85)
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(img_bytes)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(img_bytes)
        
        elif path == "/cursor":
            x, y = get_cursor_pos()
            self._send_json({"x": x, "y": y})
        
        elif path == "/windows":
            windows = window.list_windows()
            self._send_json({"windows": windows, "count": len(windows)})
        
        elif path == "/foreground":
            self._send_json(window.get_foreground_window())
        
        # v1 兼容
        elif path == "/region":
            w, h = get_screen_size()
            self._send_json({
                "x": 0, "y": 0, "width": w, "height": h,
                "mode": "fullscreen", "timestamp": time.time()
            })
        
        elif path == "/state":
            x, y = get_cursor_pos()
            self._send_json({
                "mouse_x": x, "mouse_y": y,
                "is_clicking": False, "overlay_visible": True,
                "timestamp": time.time()
            })
        
        else:
            self._send_json({"error": "Not found", "path": path}, 404)
    
    def _handle_post(self):
        path = self.path.split("?")[0]
        data = self._read_body()
        
        if path == "/click":
            x = data.get("x", 0)
            y = data.get("y", 0)
            button = data.get("button", "left")
            clicks = data.get("clicks", 1)
            delay = data.get("delay", 0)
            
            if delay > 0:
                time.sleep(delay)
            
            inp.click(x, y, button=button, clicks=clicks)
            self._send_json({"success": True, "x": x, "y": y, "button": button})
        
        elif path == "/move":
            x = data.get("x", 0)
            y = data.get("y", 0)
            duration = data.get("duration", 0)
            
            inp.move(x, y, duration=duration)
            self._send_json({"success": True, "x": x, "y": y})
        
        elif path == "/drag":
            inp.drag(
                data.get("start_x", 0), data.get("start_y", 0),
                data.get("end_x", 0), data.get("end_y", 0),
                duration=data.get("duration", 0.5),
            )
            self._send_json({"success": True})
        
        elif path == "/scroll":
            amount = data.get("amount", -3)
            x = data.get("x")
            y = data.get("y")
            inp.scroll(amount, x=x, y=y)
            self._send_json({"success": True, "amount": amount})
        
        elif path == "/key":
            key = data.get("key", "")
            presses = data.get("presses", 1)
            inp.key_press(key, presses=presses)
            self._send_json({"success": True, "key": key})
        
        elif path == "/type" or path == "/typewrite":
            text = data.get("text", "")
            use_clipboard = data.get("use_clipboard", True)
            inp.type_text(text, use_clipboard=use_clipboard)
            self._send_json({"success": True, "text": text})
        
        elif path == "/hotkey":
            keys = data.get("keys", [])
            inp.hotkey(*keys)
            self._send_json({"success": True, "keys": keys})
        
        elif path == "/focus":
            title = data.get("title", "")
            result = window.focus_window(title)
            self._send_json(result)
        
        elif path == "/screenshot":
            region = data.get("region")  # [x, y, w, h]
            fmt = data.get("format", "jpeg")
            quality = data.get("quality", 85)
            save_path = data.get("save_path")
            
            r = tuple(region) if region else None
            img_bytes = screen.screenshot(region=r, save_path=save_path, quality=quality, format=fmt)
            
            if data.get("base64"):
                self._send_json({
                    "success": True,
                    "image": base64.b64encode(img_bytes).decode("ascii"),
                    "format": fmt,
                    "size": len(img_bytes),
                })
            else:
                content_type = "image/jpeg" if fmt == "jpeg" else "image/png"
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(img_bytes)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(img_bytes)
        
        elif path == "/window-info":
            title = data.get("title", "")
            result = window.get_window_info(title)
            self._send_json(result)
        
        else:
            self._send_json({"error": "Not found", "path": path}, 404)


def start_server(host: str = "127.0.0.1", port: int = 8765):
    """启动 HTTP API 服务。"""
    server = ThreadingHTTPServer((host, port), APIHandler)
    
    w, h = get_screen_size()
    print("=" * 50)
    print("GUI Monitor v2 — HTTP API Server")
    print(f"监听地址: http://{host}:{port}")
    print(f"屏幕尺寸: {w}x{h} (DPI {get_dpi_scale():.0%})")
    print("=" * 50)
    print("API 路径:")
    print("  GET  /info         → 屏幕信息")
    print("  GET  /screenshot   → 全屏截图 (JPEG)")
    print("  GET  /cursor       → 鼠标位置")
    print("  GET  /windows      → 窗口列表")
    print("  GET  /foreground   → 前台窗口")
    print("  POST /click        → 点击")
    print("  POST /move         → 移动")
    print("  POST /drag         → 拖拽")
    print("  POST /scroll       → 滚动")
    print("  POST /key          → 按键")
    print("  POST /type         → 输入文本")
    print("  POST /hotkey       → 组合键")
    print("  POST /focus        → 聚焦窗口")
    print("  POST /screenshot   → 区域截图")
    print("=" * 50)
    print("按 Ctrl+C 停止服务")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        server.shutdown()
