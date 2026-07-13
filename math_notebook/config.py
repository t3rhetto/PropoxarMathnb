import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# 配置目录：固定在应用根目录下，不受CWD影响
_APP_DIR = Path(__file__).resolve().parent.parent
_CONFIG_PATH = _APP_DIR / "config.json"


@dataclass
class Config:
    api_key: str = ""
    api_base: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"
    output_dir: str = "./notes"
    language: str = "zh"
    subject: str = "高等数学"

    def save(self, path: str = None):
        path = path or str(_CONFIG_PATH)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "api_key": self.api_key,
                "api_base": self.api_base,
                "model": self.model,
                "output_dir": self.output_dir,
                "language": self.language,
                "subject": self.subject,
            }, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str = None) -> "Config":
        path = path or str(_CONFIG_PATH)
        if not os.path.exists(path):
            return cls()
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def get_default_config() -> Config:
    cfg = Config.load()
    if not cfg.api_key:
        cfg.api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not cfg.api_key:
        cfg.api_key = os.environ.get("OPENAI_API_KEY", "")
    return cfg
