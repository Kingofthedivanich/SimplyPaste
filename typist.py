"""
typist.py — логика посимвольного ввода текста из буфера обмена.
Использует pynput для эмуляции нажатий клавиш с поддержкой Unicode.
"""

import time
import threading

from pynput.keyboard import Controller, Key

# Единственный экземпляр контроллера клавиатуры
_keyboard = Controller()


def get_clipboard_text() -> str:
    """
    Читает текст из буфера обмена через PyQt5 QApplication.
    Возвращает пустую строку, если буфер пуст или содержит не текст.
    ВАЖНО: должна вызываться из основного потока (там, где живёт QApplication).
    """
    try:
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        return clipboard.text()
    except Exception:
        return ""





def _type_char(char: str):
    """
    Вводит один символ с поддержкой Unicode (кириллица, спецсимволы).
    pynput умеет вводить любой Unicode-символ через press/release.
    """
    try:
        if char == "\n":
            _keyboard.press(Key.enter)
            _keyboard.release(Key.enter)
        elif char == "\t":
            _keyboard.press(Key.tab)
            _keyboard.release(Key.tab)
        else:
            # Для любого Unicode-символа используем type() — самый надёжный способ
            _keyboard.type(char)
    except Exception as e:
        # Пропускаем символ, если не удалось ввести (напр. нулевой байт)
        print(f"[SimplyPaste] Не удалось ввести символ {repr(char)}: {e}")
