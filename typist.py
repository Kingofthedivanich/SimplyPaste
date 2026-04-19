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


def type_text(text: str, delay_ms: int, pre_delay_ms: int,
              on_start=None, on_finish=None, on_cancel=None) -> threading.Thread:
    """
    Запускает посимвольный ввод текста в отдельном потоке.

    :param text:         Текст для ввода
    :param delay_ms:     Задержка между символами (мс)
    :param pre_delay_ms: Пауза перед началом ввода (мс), чтобы успеть переключиться
    :param on_start:     Callback — вызывается при старте ввода
    :param on_finish:    Callback — вызывается по завершении
    :param on_cancel:    Callback — вызывается при отмене (пустой текст)
    :return:             Объект потока (уже запущен)
    """
    thread = threading.Thread(
        target=_type_worker,
        args=(text, delay_ms, pre_delay_ms, on_start, on_finish, on_cancel),
        daemon=True
    )
    thread.start()
    return thread


def _type_worker(text: str, delay_ms: int, pre_delay_ms: int,
                  on_start, on_finish, on_cancel):
    """Рабочая функция в потоке — выполняет ввод символов."""

    if not text:
        if on_cancel:
            on_cancel()
        return

    # Пауза перед вводом — пользователь переключается в нужное окно
    time.sleep(pre_delay_ms / 1000.0)

    if on_start:
        on_start()

    delay_sec = delay_ms / 1000.0

    for char in text:
        _type_char(char)
        if delay_sec > 0:
            time.sleep(delay_sec)

    if on_finish:
        on_finish()


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
