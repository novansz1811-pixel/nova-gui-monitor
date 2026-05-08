import os
import yaml
from datetime import datetime
from pathlib import Path

class RecipeManager:
    """管理 GUI 操作的学习与复用 (Workflows)"""

    def __init__(self, storage_dir=None):
        if storage_dir is None:
            # 默认存放在工作区下的 chat_agent_data/workflows
            self.storage_dir = Path(os.getcwd()) / "chat_agent_data" / "workflows"
        else:
            self.storage_dir = Path(storage_dir)
        
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, app_name: str, action: str) -> Path:
        filename = f"workflow_{app_name.lower()}_{action.lower()}.yaml"
        return self.storage_dir / filename

    def load_recipe(self, app_name: str, action: str) -> dict:
        """加载已存在的操作配方"""
        path = self._get_path(app_name, action)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def save_recipe(self, app_name: str, action: str, steps: list, gotchas: list = None, params: dict = None):
        """保存操作步骤和最佳实践"""
        path = self._get_path(app_name, action)
        
        # 检查是否已存在
        existing = self.load_recipe(app_name, action)
        version = 1
        created = datetime.now().strftime("%Y-%m-%d")
        if existing:
            version = existing.get("version", 1) + 1
            created = existing.get("created", created)
            
        recipe = {
            "app": app_name,
            "action": action,
            "version": version,
            "created": created,
            "updated": datetime.now().strftime("%Y-%m-%d"),
            "status": "verified",
            "parameters": params or {},
            "steps": steps,
            "gotchas": gotchas or []
        }

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(recipe, f, allow_unicode=True, sort_keys=False)
            
        print(f"[Learning] 已将最佳实践记录到: {path}")
        return str(path)

    def list_recipes(self):
        """列出所有学习过的配方"""
        recipes = []
        for file in self.storage_dir.glob("workflow_*.yaml"):
            with open(file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                recipes.append({
                    "app": data.get("app"),
                    "action": data.get("action"),
                    "version": data.get("version"),
                    "updated": data.get("updated")
                })
        return recipes
