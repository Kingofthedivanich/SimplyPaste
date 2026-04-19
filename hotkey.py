"""Глобальный перехват горячих клавиш."""

import threading
import time
import keyboard


class HotkeyListener:
    """Менеджер глобальной горячей клавиши."""

    def __init__(self):
        self._current_hotkey: str = ""
        self._callback = None
        self._active: bool = False
        self._lock = threading.Lock()

    def set_hotkey(self, hotkey: str, callback) -> None:
        """Устанавливает новую горячую клавишу."""
        with self._lock:
            if self._current_hotkey:
                try:
                    keyboard.remove_hotkey(self._current_hotkey)
                except Exception:
                    pass

            self._current_hotkey = hotkey
            self._callback = callback

            if self._active and hotkey:
                self._register()

    def enable(self) -> None:
        """Включает перехват горячей клавиши."""
        with self._lock:
            self._active = True
            if self._current_hotkey:
                self._register()

    def disable(self) -> None:
        """Отключает перехват горячей клавиши."""
        with self._lock:
            self._active = False
            if self._current_hotkey:
                try:
                    keyboard.remove_hotkey(self._current_hotkey)
                except Exception:
                    pass

    def _register(self) -> None:
        """Регистрирует обработчик."""
        try:
            keyboard.add_hotkey(
                self._current_hotkey,
                self._callback,
                suppress=False
            )
        except Exception as e:
            print(f"[SimplyPaste] Ошибка регистрации горячей клавиши '{self._current_hotkey}': {e}")

    def stop(self) -> None:
        """Полная остановка — снимаем все обработчики."""
        with self._lock:
            self._active = False
            keyboard.unhook_all()


class HotkeyRecorder:
    """Ожидание и запись первой нажатой клавиши."""

    def __init__(self):
        self._recording: bool = False
        self._hook = None
        self._lock = threading.Lock()

    def start(self, on_recorded) -> None:
        """Начинает ожидание нажатия клавиши."""
        with self._lock:
            if self._recording:
                return
            self._recording = True

        def _delayed_register():
            time.sleep(0.4)
            if not self._recording:
                return

            def _on_key(event: keyboard.KeyboardEvent):
                modifiers = {
                    "shift", "ctrl", "alt", "windows",
                    "left shift", "right shift",
                    "left ctrl",  "right ctrl",
                    "left alt",   "right alt",
                }
                if event.name and event.name.lower() in modifiers:
                    return

                parts = []
                if keyboard.is_pressed("ctrl"):
                    parts.append("ctrl")
                if keyboard.is_pressed("alt"):
                    parts.append("alt")
                if keyboard.is_pressed("shift"):
                    parts.append("shift")
                if keyboard.is_pressed("windows"):
                    parts.append("windows")

                key_name = event.name or "unknown"
                parts.append(key_name)
                hotkey_str = "+".join(parts)

                def _safe_finish():
                    self._stop_hook()
                    on_recorded(hotkey_str)

                threading.Thread(target=_safe_finish, daemon=True).start()

            with self._lock:
                self._hook = keyboard.on_press(_on_key, suppress=False)

        threading.Thread(target=_delayed_register, daemon=True).start()

    def _stop_hook(self) -> None:
        """Снимает активный хук и сбрасывает флаг записи."""
        with self._lock:
            if self._hook is not None:
                try:
                    keyboard.unhook(self._hook)
                except Exception:
                    pass
                self._hook = None
            self._recording = False

    def cancel(self) -> None:
        """Отменяет запись и снимает хук."""
        self._stop_hook()

    @property
    def is_recording(self) -> bool:
        return self._recording
