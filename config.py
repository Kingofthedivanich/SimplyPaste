"""Загрузка и сохранение настроек."""

import json
import os
import sys

def _get_config_path() -> str:
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "config.json")


DEFAULT_CONFIG = {
    "hotkey": "F9",
    "delay_ms": 50,
    "enabled": True,
    "pre_delay_ms": 500,
    "minimize_to_tray": True
}


def load_config() -> dict:
    """Загружает настройки из файла или возвращает умолчания."""
    path = _get_config_path()
    if not os.path.exists(path):
        return DEFAULT_CONFIG.copy()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for key, value in DEFAULT_CONFIG.items():
            data.setdefault(key, value)
        return data
    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    """Сохраняет настройки в config.json."""
    path = _get_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"[SimplyPaste] Ошибка сохранения настроек: {e}")
