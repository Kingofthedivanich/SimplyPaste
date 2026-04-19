"""
gui/tray.py — иконка в системном трее для SimplyPaste.
Использует pystray для показа иконки и контекстного меню.
"""

import threading

import pystray                   # pip install pystray
from PIL import Image, ImageDraw # pip install Pillow


def _create_default_icon(size: int = 64, enabled: bool = True) -> Image.Image:
    """
    Создаёт простую программную иконку (если файл icon.png недоступен).
    Зелёный круг = включено, серый = выключено.
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = "#4CAF50" if enabled else "#9E9E9E"
    # Фон — скруглённый прямоугольник
    draw.rectangle([4, 4, size - 4, size - 4], fill="#1E1E2E")
    # Индикатор — цветной кружок
    draw.ellipse([14, 14, size - 14, size - 14], fill=color)
    return img


def _load_icon_image(icon_path: str, enabled: bool = True) -> Image.Image:
    """Загружает иконку из файла или создаёт программную."""
    try:
        return Image.open(icon_path).resize((64, 64)).convert("RGBA")
    except Exception:
        return _create_default_icon(enabled=enabled)


class TrayIcon:
    """
    Иконка в системном трее с контекстным меню.

    Меню содержит:
      - Показать / скрыть главное окно
      - Включить / выключить SimplyPaste
      - Выход
    """

    def __init__(self, icon_path: str, on_show, on_toggle, on_quit):
        """
        :param icon_path: Путь к файлу иконки
        :param on_show:   Callback — показать главное окно
        :param on_toggle: Callback(enabled: bool) — переключить состояние
        :param on_quit:   Callback — завершить приложение
        """
        self._icon_path = icon_path
        self._on_show = on_show
        self._on_toggle = on_toggle
        self._on_quit = on_quit
        self._enabled = True
        self._tray: pystray.Icon | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Запускает иконку трея в отдельном потоке."""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        """Основной цикл иконки трея."""
        image = _load_icon_image(self._icon_path, self._enabled)
        self._tray = pystray.Icon(
            name="SimplyPaste",
            icon=image,
            title="SimplyPaste",
            menu=self._build_menu()
        )
        self._tray.run()

    def _build_menu(self) -> pystray.Menu:
        """Создаёт контекстное меню трея."""
        return pystray.Menu(
            pystray.MenuItem("SimplyPaste", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Показать окно", self._handle_show, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Включено",
                self._handle_toggle,
                checked=lambda item: self._enabled
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Выход", self._handle_quit),
        )

    # ── Обработчики меню ──────────────────────────────────────────────────────

    def _handle_show(self, icon, item) -> None:
        self._on_show()

    def _handle_toggle(self, icon, item) -> None:
        self._enabled = not self._enabled
        self._on_toggle(self._enabled)
        self._update_icon()

    def _handle_quit(self, icon, item) -> None:
        self._tray.stop()
        self._on_quit()

    # ── Публичные методы ──────────────────────────────────────────────────────

    def set_enabled(self, enabled: bool) -> None:
        """Обновляет состояние иконки при изменении из главного окна."""
        self._enabled = enabled
        self._update_icon()

    def _update_icon(self) -> None:
        """Перерисовывает иконку в зависимости от состояния включения."""
        if self._tray:
            self._tray.icon = _load_icon_image(self._icon_path, self._enabled)

    def stop(self) -> None:
        """Останавливает иконку трея."""
        if self._tray:
            try:
                self._tray.stop()
            except Exception:
                pass
