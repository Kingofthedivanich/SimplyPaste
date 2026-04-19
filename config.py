"""
config.py — загрузка и сохранение настроек приложения SimplyPaste.
Настройки хранятся в файле config.json рядом с исполняемым файлом.
"""

import json
import os
import sys

# Путь к config.json — рядом с запускаемым файлом
def _get_config_path() -> str:
    if getattr(sys, "frozen", False):
        # Режим EXE (PyInstaller)
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "config.json")


# Значения по умолчанию
DEFAULT_CONFIG = {
    "hotkey": "F9",          # Горячая клавиша по умолчанию
    "delay_ms": 50,          # Задержка между символами (мс)
    "enabled": True,         # Утилита включена
    "pre_delay_ms": 500,     # Пауза перед началом ввода (мс)
    "minimize_to_tray": True # Сворачивать в трей при закрытии
}


def load_config() -> dict:
    """Загружает настройки из config.json. Если файл отсутствует — возвращает дефолтные."""
    path = _get_config_path()
    if not os.path.exists(path):
        return DEFAULT_CONFIG.copy()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Дополняем отсутствующие ключи дефолтными значениями
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
