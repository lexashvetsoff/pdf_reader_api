import json
from pathlib import Path
from functools import lru_cache
from typing import Dict, Any


@lru_cache()
def get_raw_settings() -> Dict[str, Any]:
    settings_path = Path(__file__).parent.parent / "data" / "settings.json"
    with open(settings_path, "r", encoding="utf-8") as f:
        return json.load(f)
