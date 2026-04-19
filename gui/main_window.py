"""
gui/main_window.py — главное окно приложения SimplyPaste.
Построено на PyQt5 с современным тёмным дизайном для Windows 11.
"""

import os
import sys

from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QObject
)
from PyQt5.QtGui import (
    QFont, QIcon, QColor, QCursor
)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QSpinBox, QFrame,
    QSystemTrayIcon, QMenu, QAction, QGraphicsDropShadowEffect
)

from config import load_config, save_config
from hotkey import HotkeyListener, HotkeyRecorder
from typist import get_clipboard_text, _type_char


# ══════════════════════════════════════════════════════════════════════════════
#  Цветовая палитра (тёмная тема в стиле Windows 11)
# ══════════════════════════════════════════════════════════════════════════════

COLORS = {
    "bg_dark":      "#1C1B1F",   # Основной фон (Surface)
    "bg_card":      "#2B2930",   # Карточки (Surface Variant / Container)
    "bg_widget":    "#322F35",   # Виджеты внутри карточек (Surface Container High)
    "accent":       "#D0BCFF",   # Primary (светлый фиолетовый)
    "accent_light": "#EADDFF",   # Primary Container (светлее)
    "accent_glow":  "#4F378B",   # Primary (тёмный, для теней или hover)
    "success":      "#A8EFCD",   # Аналог Primary для успеха (зеленоватый пастельный)
    "warning":      "#FFB4AB",   # Запись клавиши (error container или tertiary)
    "danger":       "#FFB4AB",   # Отключено (красный пастельный error)
    "text_primary": "#E6E1E5",   # On-Surface (основной текст)
    "text_secondary": "#CAC4D0", # On-Surface Variant (вторичный текст)
    "border":       "#49454F",   # Outline (границы)
    "on_accent":    "#381E72",   # On-Primary (текст на кнопках)
}

STYLESHEET = f"""
/* ── Основное окно ── */
QMainWindow, QWidget#centralWidget {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI Variable Display', 'Segoe UI', sans-serif;
}}

/* ── Карточки ── */
QFrame#card {{
    background-color: {COLORS['bg_card']};
    border: none;
    border-radius: 24px;
    padding: 8px;
}}

/* ── Метки ── */
QLabel {{
    color: {COLORS['text_primary']};
    background: transparent;
}}
QLabel#sectionTitle {{
    color: {COLORS['accent']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
}}
QLabel#hotkeyDisplay {{
    background-color: {COLORS['bg_widget']};
    border: none;
    border-radius: 12px;
    color: {COLORS['accent']};
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 8px 18px;
    qproperty-alignment: AlignCenter;
}}
QLabel#statusLabel {{
    font-size: 13px;
    font-weight: 500;
    padding: 6px 12px;
    border-radius: 8px;
}}

/* ── Кнопки ── */
QPushButton {{
    background-color: {COLORS['accent']};
    color: {COLORS['on_accent']};
    border: none;
    border-radius: 18px; /* Material pill shape for small buttons */
    font-size: 13px;
    font-weight: 600;
    padding: 8px 20px;
    outline: none;
}}
QPushButton:hover {{
    background-color: {COLORS['accent_light']};
}}
QPushButton:pressed {{
    background-color: {COLORS['accent_glow']};
    color: {COLORS['text_primary']};
}}

/* Кнопка «Записать клавишу» */
QPushButton#recordBtn {{
    background-color: {COLORS['bg_widget']};
    color: {COLORS['text_primary']};
    border-radius: 16px;
    font-weight: 500;
}}
QPushButton#recordBtn:hover {{
    background-color: {COLORS['border']};
}}
QPushButton#recordBtn[recording="true"] {{
    background-color: {COLORS['warning']};
    color: #410002;
}}

/* Кнопка включения/выключения */
QPushButton#toggleBtn {{
    font-size: 15px;
    font-weight: 600;
    padding: 14px 28px;
    border-radius: 24px; /* Material 3 large button */
    letter-spacing: 0.5px;
}}
QPushButton#toggleBtn[enabled_state="true"] {{
    background-color: {COLORS['accent']};
    color: {COLORS['on_accent']};
}}
QPushButton#toggleBtn[enabled_state="false"] {{
    background-color: {COLORS['danger']};
    color: #410002;
}}
QPushButton#toggleBtn:hover {{
    opacity: 0.9;
}}

/* ── SpinBox (Material 3 style text field) ── */
QSpinBox {{
    background-color: {COLORS['bg_widget']};
    color: {COLORS['text_primary']};
    border: none;
    border-bottom: 2px solid {COLORS['text_secondary']};
    border-radius: 4px; /* Топовые углы скруглены, внизу линия */
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
    font-size: 14px;
    padding: 6px 8px;
    min-width: 65px;
}}
QSpinBox:focus {{
    border-bottom: 2px solid {COLORS['accent']};
    background-color: {COLORS['border']};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    width: 0px; /* Прячем стрелки для минимализма */
}}

/* ── Разделитель ── */
QFrame#separator {{
    background-color: {COLORS['border']};
    max-height: 1px;
}}

/* ── Меню трея ── */
QMenu {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 8px;
    font-size: 13px;
}}
QMenu::item:selected {{
    background-color: {COLORS['bg_widget']};
    border-radius: 8px;
}}
"""


def _make_card(parent=None) -> QFrame:
    """Создаёт карточку-контейнер с рамкой и тёмным фоном."""
    frame = QFrame(parent)
    frame.setObjectName("card")
    return frame


def _section_label(text: str, parent=None) -> QLabel:
    """Создаёт надпись-заголовок секции."""
    lbl = QLabel(text.upper(), parent)
    lbl.setObjectName("sectionTitle")
    return lbl


# ══════════════════════════════════════════════════════════════════════════════
#  Вспомогательный поток для операций с буфером (во избежание фризов GUI)
# ══════════════════════════════════════════════════════════════════════════════

class HotkeySignalBridge(QObject):
    """
    Мост для безопасной передачи сигналов из фонового потока keyboard
    в главный поток Qt через QueuedConnection.
    """
    triggered = pyqtSignal()          # горячая клавиша нажата
    hotkey_recorded = pyqtSignal(str) # клавиша записана


class PasteWorker(QThread):
    """
    Поток, выполняющий посимвольный ввод синхронно.
    Сигналы используются для безопасного обновления GUI из фонового потока.
    """
    started_typing = pyqtSignal()
    finished_typing = pyqtSignal()
    clipboard_empty = pyqtSignal()

    def __init__(self, text: str, delay_ms: int):
        super().__init__()
        self.text = text
        self.delay_ms = delay_ms

    def run(self):
        """Выполняет посимвольный ввод в текущем потоке."""
        import time
        if not self.text:
            self.clipboard_empty.emit()
            return

        self.started_typing.emit()
        delay_sec = self.delay_ms / 1000.0
        for char in self.text:
            _type_char(char)
            if delay_sec > 0:
                time.sleep(delay_sec)
        self.finished_typing.emit()


# ══════════════════════════════════════════════════════════════════════════════
#  Главное окно
# ══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    """
    Главное окно SimplyPaste.
    Содержит настройки горячей клавиши, задержки, кнопку вкл/откл.
    """

    def __init__(self, app: QApplication):
        super().__init__()
        self._app = app
        self._config = load_config()
        self._listener = HotkeyListener()
        self._recorder = HotkeyRecorder()
        self._worker: PasteWorker | None = None
        self._is_typing = False

        # Мост для безопасного crossthread вызова из потока keyboard -> Qt
        self._hotkey_bridge = HotkeySignalBridge()
        self._hotkey_bridge.triggered.connect(
            self._on_hotkey_triggered, Qt.QueuedConnection
        )
        # Безопасная доставка записанной клавиши из фонового потока
        self._hotkey_bridge.hotkey_recorded.connect(
            self._apply_hotkey_to_ui, Qt.QueuedConnection
        )

        self._setup_window()
        self._setup_ui()
        self._setup_tray()
        self._apply_config()
        self._start_hotkey()

    # ── Инициализация окна ─────────────────────────────────────────────────

    def _setup_window(self):
        """Настраивает параметры главного окна."""
        self.setWindowTitle("SimplyPaste")
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        icon_path = self._get_icon_path()
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setStyleSheet(STYLESHEET)

    def _get_icon_path(self) -> str:
        """Возвращает путь к файлу иконки."""
        if getattr(sys, "frozen", False):
            base = sys._MEIPASS
        else:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, "assets", "icon.png")

    # ── Построение интерфейса ──────────────────────────────────────────────

    def _setup_ui(self):
        """Строит всё дерево виджетов."""
        central = QWidget()
        central.setObjectName("centralWidget")
        central.setFixedWidth(320)
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(16)
        root_layout.setSizeConstraint(QVBoxLayout.SetFixedSize)

        # ── Заголовок ──
        root_layout.addWidget(self._build_header())

        # ── Горячая клавиша ──
        root_layout.addWidget(self._build_hotkey_card())

        # ── Задержка ──
        root_layout.addWidget(self._build_delay_card())

        # ── Toggle ──
        root_layout.addWidget(self._build_toggle_card())

    def _build_header(self) -> QWidget:
        """Шапка с логотипом и названием."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        title_col = QVBoxLayout()
        title = QLabel("SimplyPaste")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        title_col.addWidget(title)
        title_col.setSpacing(2)

        layout.addLayout(title_col)
        layout.addStretch()
        return widget

    def _build_hotkey_card(self) -> QFrame:
        """Карточка выбора горячей клавиши."""
        card = _make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        layout.addWidget(_section_label("hotkey"))

        # Поле с текущей клавишей + кнопка «Записать»
        row = QHBoxLayout()
        self._hotkey_display = QLabel(self._config.get("hotkey", "F9"))
        self._hotkey_display.setObjectName("hotkeyDisplay")
        self._hotkey_display.setMinimumWidth(130)

        self._record_btn = QPushButton("Record")
        self._record_btn.setObjectName("recordBtn")
        self._record_btn.setProperty("recording", False)
        self._record_btn.clicked.connect(self._on_record_clicked)
        self._record_btn.setCursor(QCursor(Qt.PointingHandCursor))

        row.addWidget(self._hotkey_display, stretch=1)
        row.addWidget(self._record_btn)
        layout.addLayout(row)

        return card

    def _build_delay_card(self) -> QFrame:
        """Карточка настройки задержки."""
        card = _make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # Задержка между символами
        row1 = QHBoxLayout()
        lbl1 = QLabel("Char delay:")
        lbl1.setFont(QFont("Segoe UI", 10))
        self._delay_spin = QSpinBox()
        self._delay_spin.setRange(0, 500)
        self._delay_spin.setValue(self._config.get("delay_ms", 50))
        self._delay_spin.setSuffix(" ms")
        self._delay_spin.valueChanged.connect(self._on_delay_changed)
        row1.addWidget(lbl1)
        row1.addStretch()
        row1.addWidget(self._delay_spin)
        layout.addLayout(row1)

        # Пауза перед вводом
        row2 = QHBoxLayout()
        pre_lbl = QLabel("Pre-delay:")
        pre_lbl.setFont(QFont("Segoe UI", 10))
        self._pre_delay_spin = QSpinBox()
        self._pre_delay_spin.setRange(100, 5000)
        self._pre_delay_spin.setValue(self._config.get("pre_delay_ms", 500))
        self._pre_delay_spin.setSuffix(" ms")
        self._pre_delay_spin.setToolTip("Wait time before typing starts (lets you switch windows)")
        self._pre_delay_spin.valueChanged.connect(self._on_pre_delay_changed)
        row2.addWidget(pre_lbl)
        row2.addStretch()
        row2.addWidget(self._pre_delay_spin)
        layout.addLayout(row2)
        return card

    def _build_toggle_card(self) -> QFrame:
        """Карточка включения/выключения утилиты."""
        card = _make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        layout.addWidget(_section_label("control"))

        self._toggle_btn = QPushButton()
        self._toggle_btn.setObjectName("toggleBtn")
        self._toggle_btn.setMinimumHeight(48)
        self._toggle_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._toggle_btn.clicked.connect(self._on_toggle_clicked)

        # Добавляем эффект тени
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(COLORS["accent"]))
        shadow.setOffset(0, 4)
        self._toggle_btn.setGraphicsEffect(shadow)

        layout.addWidget(self._toggle_btn)
        self._update_toggle_btn(self._config.get("enabled", True))
        return card

    # ── Системный трей ─────────────────────────────────────────────────────

    def _setup_tray(self):
        """Создаёт иконку в системном трее."""
        self._tray = QSystemTrayIcon(self)
        icon_path = self._get_icon_path()
        if os.path.exists(icon_path):
            self._tray.setIcon(QIcon(icon_path))
        else:
            self._tray.setIcon(self.style().standardIcon(
                self.style().SP_ComputerIcon))

        self._tray.setToolTip("SimplyPaste")

        # Контекстное меню трея
        tray_menu = QMenu()
        tray_menu.setStyleSheet(STYLESHEET)

        act_show = QAction("Show", self)
        act_show.triggered.connect(self._show_window)

        self._act_toggle = QAction("Disable", self)
        self._act_toggle.triggered.connect(self._on_toggle_clicked)

        act_quit = QAction("Quit", self)
        act_quit.triggered.connect(self._quit_app)

        tray_menu.addAction(act_show)
        tray_menu.addSeparator()
        tray_menu.addAction(self._act_toggle)
        tray_menu.addSeparator()
        tray_menu.addAction(act_quit)

        self._tray.setContextMenu(tray_menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._update_tray_menu()
        self._tray.show()

    # ── Применение конфигурации ────────────────────────────────────────────

    def _apply_config(self):
        """Применяет загруженные настройки к виджетам."""
        self._hotkey_display.setText(self._config.get("hotkey", "F9"))
        self._delay_spin.setValue(self._config.get("delay_ms", 50))
        self._pre_delay_spin.setValue(self._config.get("pre_delay_ms", 500))
        self._update_toggle_btn(self._config.get("enabled", True))

    def _start_hotkey(self):
        """Запускает перехват горячей клавиши согласно настройкам."""
        hotkey = self._config.get("hotkey", "F9")
        # Передаём bridge.triggered.emit как callback — это thread-safe
        self._listener.set_hotkey(hotkey, self._hotkey_bridge.triggered.emit)
        if self._config.get("enabled", True):
            self._listener.enable()

    # ── Обработчики событий ────────────────────────────────────────────────

    def _on_record_clicked(self):
        """Пользователь нажал «Записать клавишу»."""
        if self._recorder.is_recording:
            return   # Уже пишем

        # Временно отключаем текущую горячую клавишу, чтобы не перехватить её
        self._listener.disable()

        # Меняем кнопку на «ожидание»
        self._record_btn.setText("Press a key…")
        self._record_btn.setProperty("recording", True)
        self._record_btn.style().unpolish(self._record_btn)
        self._record_btn.style().polish(self._record_btn)

        self._recorder.start(self._on_hotkey_recorded)

    def _on_hotkey_recorded(self, hotkey: str):
        """Callback — клавиша записана. Вызывается из фонового потока."""
        # Передаём значение в главный поток Qt через signal (QueuedConnection)
        self._hotkey_bridge.hotkey_recorded.emit(hotkey)

    def _apply_hotkey_to_ui(self, hotkey: str):
        """Обновляет UI и регистрирует новую горячую клавишу."""
        self._config["hotkey"] = hotkey
        save_config(self._config)

        self._hotkey_display.setText(hotkey)

        self._record_btn.setText("Record")
        self._record_btn.setProperty("recording", False)
        self._record_btn.style().unpolish(self._record_btn)
        self._record_btn.style().polish(self._record_btn)

        # Перерегистрируем горячую клавишу (через bridge для thread-safety)
        self._listener.set_hotkey(hotkey, self._hotkey_bridge.triggered.emit)
        if self._config.get("enabled", True):
            self._listener.enable()

    def _on_delay_changed(self, value: int):
        """Пользователь изменил задержку."""
        self._config["delay_ms"] = value
        save_config(self._config)

    def _on_pre_delay_changed(self, value: int):
        """Пользователь изменил паузу перед вводом."""
        self._config["pre_delay_ms"] = value
        save_config(self._config)

    def _on_toggle_clicked(self):
        """Включение/выключение утилиты."""
        enabled = not self._config.get("enabled", True)
        self._config["enabled"] = enabled
        save_config(self._config)

        if enabled:
            self._listener.enable()
        else:
            self._listener.disable()

        self._update_toggle_btn(enabled)
        self._update_tray_menu()

    def _on_hotkey_triggered(self):
        """
        Вызывается при нажатии горячей клавиши (в главном потоке Qt).
        Читает буфер обмена и запускает ввод с pre_delay задержкой.
        """
        if self._is_typing:
            return   # Уже идёт ввод — игнорируем

        # Читаем буфер сразу (QApplication.clipboard() — только из главного потока)
        text = get_clipboard_text()
        if not text:
            return
            
        self._is_typing = True  # Блокируем повторные нажатия на время pre_delay

        pre_delay = self._config.get("pre_delay_ms", 500)
        # Запускаем ввод через pre_delay мс, чтобы пользователь успел переключиться
        QTimer.singleShot(pre_delay, lambda: self._start_typing(text))

    def _start_typing(self, text: str):
        """Запускает рабочий поток с посимвольным вводом."""
        delay_ms = self._config.get("delay_ms", 50)

        self._worker = PasteWorker(text, delay_ms)
        self._worker.started_typing.connect(self._on_typing_started)
        self._worker.finished_typing.connect(self._on_typing_finished)
        self._worker.clipboard_empty.connect(self._on_clipboard_empty)
        self._worker.start()

    # ── Обратная связь во время ввода ─────────────────────────────────────

    def _on_typing_started(self):
        pass  # Флаг self._is_typing уже установлен в _on_hotkey_triggered

    def _on_typing_finished(self):
        self._is_typing = False

    def _on_clipboard_empty(self):
        self._is_typing = False

    # ── Вспомогательные методы ─────────────────────────────────────────────

    def _update_toggle_btn(self, enabled: bool):
        """Обновляет текст и стиль кнопки вкл/откл."""
        if enabled:
            self._toggle_btn.setText("Enabled")
        else:
            self._toggle_btn.setText("Disabled")

        self._toggle_btn.setProperty("enabled_state", str(enabled).lower())
        self._toggle_btn.style().unpolish(self._toggle_btn)
        self._toggle_btn.style().polish(self._toggle_btn)

        # Обновляем тень
        shadow = self._toggle_btn.graphicsEffect()
        if isinstance(shadow, QGraphicsDropShadowEffect):
            shadow.setColor(QColor(COLORS["accent"] if enabled else COLORS["danger"]))

    def _update_tray_menu(self):
        """Обновляет пункт меню трея в зависимости от состояния."""
        enabled = self._config.get("enabled", True)
        self._act_toggle.setText("Disable" if enabled else "Enable")

    # ── Управление окном ───────────────────────────────────────────────────

    def _on_tray_activated(self, reason):
        """Двойной клик по иконке трея — показать/скрыть окно."""
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_window()

    def _show_window(self):
        """Показывает и поднимает главное окно."""
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        """При закрытии окна — сворачиваем в трей вместо выхода."""
        event.ignore()
        self.hide()
        self._tray.showMessage(
            "SimplyPaste",
            "Running in background.\nDouble-click the tray icon to restore.",
            QSystemTrayIcon.Information,
            2000
        )

    def _quit_app(self):
        """Полное завершение приложения."""
        self._listener.stop()
        save_config(self._config)
        self._tray.hide()
        QApplication.quit()
