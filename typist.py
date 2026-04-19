"""Посимвольный ввод текста через pynput."""

import time
import threading

from pynput.keyboard import Controller, Key


_keyboard = Controller()


def get_clipboard_text() -> str:
    """Читает текст из буфера обмена."""
    try:
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        return clipboard.text()
    except Exception:
        return ""





def _type_char(char: str):
    """Вводит один символ."""
    try:
        if char == "\n":
            _keyboard.press(Key.enter)
            _keyboard.release(Key.enter)
        elif char == "\t":
            _keyboard.press(Key.tab)
            _keyboard.release(Key.tab)
        else:
            _keyboard.type(char)
    except Exception as e:
        print(f"[SimplyPaste] Не удалось ввести символ {repr(char)}: {e}")
