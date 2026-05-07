"""
GUI Monitor — python -m gui_monitor 入口

DPI 初始化必须在所有其他导入之前完成。
"""

# 第一步：DPI 初始化（必须最早执行）
from gui_monitor.utils.dpi import init_dpi
init_dpi()


def _cleanup_old_screenshots(max_age_hours: int = 24):
    """静默清理过期调试截图，不影响启动。"""
    import time
    from pathlib import Path

    project_root = Path(__file__).parent.parent
    dirs = [
        project_root / "screenshots_debug",
        project_root / "chat_agent_data" / "screenshots",
    ]

    now = time.time()
    for d in dirs:
        if not d.exists():
            continue
        for f in d.glob("*.png"):
            try:
                if (now - f.stat().st_mtime) > max_age_hours * 3600:
                    f.unlink()
            except Exception:
                pass


# 第二步：自动清理过期调试截图
_cleanup_old_screenshots()

# 第三步：执行 CLI
from gui_monitor.cli import main
import sys

sys.exit(main() or 0)
