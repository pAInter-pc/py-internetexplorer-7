# -*- coding: utf-8 -*-
import sys
import os
import random
import time
import json
from datetime import datetime

from PyQt6.QtCore import (
    Qt,
    QUrl,
    QTimer,
    QSize,
)

from PyQt6.QtGui import (
    QIcon,
    QPixmap,
    QDesktopServices,
    QAction,
)

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QLineEdit,
    QStatusBar,
    QToolBar,
    QToolButton,
    QFileDialog,
    QMessageBox,
    QTextEdit,
    QTabWidget,
    QWidget,
    QInputDialog,
    QCompleter,
    QGroupBox,
    QProgressBar,
)

from PyQt6.QtWebEngineWidgets import (
    QWebEngineView,
)

from PyQt6.QtWebEngineCore import (
    QWebEnginePage,
    QWebEngineProfile,
)


SETTINGS_FILE = "ie7_settings.json"
DEFAULT_HOME_PAGE = "https://www.google.com"
DOWNLOADS_DIR_NAME = "IE7 Downloads"


class IE7DownloadManager(QDialog):
    """
    Менеджер загрузок в стиле IE7.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Загрузки Internet Explorer 7")
        self.setFixedSize(540, 420)

        self.downloads = []  # список словарей: filename, path, time, size
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel("Загрузки")
        title.setStyleSheet("font-family: Segoe UI; font-size: 13px; font-weight: bold;")
        main_layout.addWidget(title)

        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)

        stats_layout = QHBoxLayout()
        self.total_downloads_label = QLabel("Файлов: 0")
        self.total_size_label = QLabel("Общий размер: 0 КБ")
        stats_layout.addWidget(self.total_downloads_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.total_size_label)
        main_layout.addLayout(stats_layout)

        buttons_layout = QHBoxLayout()

        self.open_button = QPushButton("Открыть")
        self.open_button.clicked.connect(self.open_file)
        buttons_layout.addWidget(self.open_button)

        self.open_folder_button = QPushButton("Открыть папку")
        self.open_folder_button.clicked.connect(self.open_folder)
        buttons_layout.addWidget(self.open_folder_button)

        clear_button = QPushButton("Очистить список")
        clear_button.clicked.connect(self.clear_downloads)
        buttons_layout.addWidget(clear_button)

        buttons_layout.addStretch()

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.close)
        buttons_layout.addWidget(close_button)

        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

    def add_download(self, filename: str, path: str, size: str = "Неизвестно"):
        download_time = datetime.now().strftime("%H:%M:%S")
        info = {
            "filename": filename,
            "path": path,
            "time": download_time,
            "size": size,
        }
        self.downloads.append(info)

        item_text = f"{filename}  |  {size}  |  {download_time}"
        self.list_widget.addItem(QListWidgetItem(item_text))

        self._update_stats()

    def _update_stats(self):
        self.total_downloads_label.setText(f"Файлов: {len(self.downloads)}")

        total_kb = 0
        for d in self.downloads:
            if "КБ" in d["size"]:
                try:
                    kb = int(d["size"].split()[0])
                    total_kb += kb
                except ValueError:
                    pass
        self.total_size_label.setText(f"Общий размер: {total_kb} КБ")

    def open_file(self):
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.downloads):
            return
        path = self.downloads[row]["path"]
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def open_folder(self):
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.downloads):
            return
        folder = os.path.dirname(self.downloads[row]["path"])
        if os.path.isdir(folder):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def clear_downloads(self):
        self.downloads.clear()
        self.list_widget.clear()
        self._update_stats()


class IE7FavoritesManager(QDialog):
    """
    Менеджер избранного в стиле IE7.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Избранное Internet Explorer 7")
        self.setFixedSize(520, 420)

        self.favorites = []  # список кортежей (name, url)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        header_label = QLabel("Избранное")
        header_label.setStyleSheet("font-family: Segoe UI; font-size: 13px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        input_layout = QGridLayout()
        name_label = QLabel("Имя:")
        url_label = QLabel("Адрес:")

        self.name_edit = QLineEdit()
        self.url_edit = QLineEdit()

        input_layout.addWidget(name_label, 0, 0)
        input_layout.addWidget(self.name_edit, 0, 1)
        input_layout.addWidget(url_label, 1, 0)
        input_layout.addWidget(self.url_edit, 1, 1)

        add_button = QPushButton("Добавить")
        add_button.clicked.connect(self.add_favorite)
        input_layout.addWidget(add_button, 0, 2, 2, 1)

        main_layout.addLayout(input_layout)

        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)

        buttons_layout = QHBoxLayout()
        open_button = QPushButton("Перейти")
        open_button.clicked.connect(self.visit_selected)
        buttons_layout.addWidget(open_button)

        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(self.delete_selected)
        buttons_layout.addWidget(delete_button)

        buttons_layout.addStretch()

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.close)
        buttons_layout.addWidget(close_button)

        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

    def set_favorites(self, favorites_list):
        self.favorites = list(favorites_list)
        self._reload_list()

    def _reload_list(self):
        self.list_widget.clear()
        for name, url in self.favorites:
            self.list_widget.addItem(f"{name}  |  {url}")

    def add_favorite(self):
        name = self.name_edit.text().strip()
        url = self.url_edit.text().strip()
        if not name or not url:
            return
        if not url.startswith(("http://", "https://")):
            url = "http://" + url

        self.favorites.append((name, url))
        self._reload_list()
        self.name_edit.clear()
        self.url_edit.clear()

    def delete_selected(self):
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.favorites):
            return
        self.favorites.pop(row)
        self._reload_list()

    def visit_selected(self):
        parent = self.parent()
        if not isinstance(parent, QMainWindow):
            return
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.favorites):
            return
        url = self.favorites[row][1]
        parent.set_url(QUrl(url))
        self.close()
class IE7QuickCommands(QDialog):
    """
    Быстрые команды IE7: история, кэш, информация о странице и т.п.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_browser = parent
        self.setWindowTitle("Быстрые команды")
        self.setFixedSize(320, 400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        header = QLabel("Быстрые команды")
        header.setStyleSheet("font-family: Segoe UI; font-size: 13px; font-weight: bold;")
        layout.addWidget(header)

        actions = [
            ("Очистить историю", self._clear_history),
            ("Очистить кэш", self._clear_cache),
            ("Информация о странице", self._show_page_info),
            ("Исходный код", self._view_source),
            ("Сделать скриншот", self._screenshot),
            ("Инструменты разработчика", self._developer_tools),
        ]

        for text, slot in actions:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        layout.addStretch()

        info_group = QGroupBox("Состояние")
        info_layout = QVBoxLayout(info_group)
        self.history_label = QLabel("История: 0 записей")
        self.cache_label = QLabel("Кэш: 0 элементов")
        info_layout.addWidget(self.history_label)
        info_layout.addWidget(self.cache_label)
        layout.addWidget(info_group)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def update_info(self, history_count: int, cache_items: int):
        self.history_label.setText(f"История: {history_count} записей")
        self.cache_label.setText(f"Кэш: {cache_items} элементов")

    # обёртки
    def _clear_history(self):
        if self.parent_browser:
            self.parent_browser.clear_history()

    def _clear_cache(self):
        if self.parent_browser:
            self.parent_browser.clear_cache()

    def _show_page_info(self):
        if self.parent_browser:
            self.parent_browser.show_page_info()

    def _view_source(self):
        if self.parent_browser:
            self.parent_browser.view_page_source()

    def _screenshot(self):
        if self.parent_browser:
            self.parent_browser.take_screenshot()

    def _developer_tools(self):
        if self.parent_browser:
            self.parent_browser.show_developer_tools()


class IE7SecurityCertificates(QDialog):
    """
    Простое окно просмотра "сертификатов" в духе IE7 (фиктивные данные).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Сертификаты безопасности")
        self.setFixedSize(620, 420)
        self.certificates = []
        self._setup_ui()
        self._load_dummy_certs()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        header = QLabel("Сертификаты")
        header.setStyleSheet("font-family: Segoe UI; font-size: 13px; font-weight: bold;")
        main_layout.addWidget(header)

        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)

        self.details_edit = QTextEdit()
        self.details_edit.setReadOnly(True)
        main_layout.addWidget(self.details_edit)

        buttons_layout = QHBoxLayout()
        view_btn = QPushButton("Просмотреть")
        view_btn.clicked.connect(self.view_selected)
        buttons_layout.addWidget(view_btn)

        import_btn = QPushButton("Импорт...")
        import_btn.clicked.connect(self.import_cert)
        buttons_layout.addWidget(import_btn)

        export_btn = QPushButton("Экспорт...")
        export_btn.clicked.connect(self.export_cert)
        buttons_layout.addWidget(export_btn)

        buttons_layout.addStretch()

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(close_btn)

        main_layout.addLayout(buttons_layout)

        self.list_widget.currentRowChanged.connect(self._show_details)

        self.setLayout(main_layout)

    def _load_dummy_certs(self):
        self.certificates = [
            {
                "name": "Microsoft Internet Authority",
                "issuer": "Microsoft Corporation",
                "valid_from": "01.01.2015",
                "valid_to": "31.12.2030",
                "purpose": "Проверка подлинности сервера",
            },
            {
                "name": "DigiCert Global Root CA",
                "issuer": "DigiCert Inc",
                "valid_from": "01.01.2013",
                "valid_to": "31.12.2033",
                "purpose": "Удостоверяющий центр",
            },
            {
                "name": "Local Development CA",
                "issuer": "Local Authority",
                "valid_from": "01.01.2020",
                "valid_to": "31.12.2030",
                "purpose": "Тестовый сертификат",
            },
        ]
        self.list_widget.clear()
        for cert in self.certificates:
            self.list_widget.addItem(cert["name"])

    def _show_details(self, index: int):
        if index < 0 or index >= len(self.certificates):
            self.details_edit.clear()
            return
        cert = self.certificates[index]
        text = (
            f"Сертификат: {cert['name']}\n"
            f"Издатель: {cert['issuer']}\n"
            f"Действителен с: {cert['valid_from']}\n"
            f"Действителен до: {cert['valid_to']}\n"
            f"Назначение: {cert['purpose']}\n\n"
            "Статус: Действителен\n"
            "Уровень доверия: Высокий"
        )
        self.details_edit.setPlainText(text)

    def view_selected(self):
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.certificates):
            return
        QMessageBox.information(
            self,
            "Сертификат",
            "Подробный просмотр сертификата не реализован в данном эмуляторе.",
        )

    def import_cert(self):
        QMessageBox.information(
            self,
            "Импорт",
            "Импорт сертификатов в этом эмуляторе не реализован.",
        )

    def export_cert(self):
        QMessageBox.information(
            self,
            "Экспорт",
            "Экспорт сертификатов в этом эмуляторе не реализован.",
        )


class IE7Browser(QMainWindow):
    """
    Основное окно браузера IE7 (эмулятор).
    """
    def __init__(self):
        super().__init__()

        # --- пути и состояние ---
        self.downloads_folder = os.path.join(
            os.path.expanduser("~"), DOWNLOADS_DIR_NAME
        )
        os.makedirs(self.downloads_folder, exist_ok=True)

        self.current_download = None
        self.is_offline = False
        self.zoom_level = 100
        self.history = []          # список словарей {url, title, time}
        self.browser_cache = []    # фиктивный кэш
        self.session_start = datetime.now()

        # вспомогательные переменные
        self.page_load_time = 0.0

        # менеджеры
        self.download_manager = IE7DownloadManager(self)
        self.favorites_manager = IE7FavoritesManager(self)
        self.certificates_manager = IE7SecurityCertificates(self)
        self.quick_commands = IE7QuickCommands(self)

        # UI элементы, инициализируем до методов
        self.browser: QWebEngineView | None = None
        self.urlbar: QLineEdit | None = None
        self.url_completer: QCompleter | None = None
        self.status: QStatusBar | None = None
        self.zone_label: QLabel | None = None
        self.offline_label: QLabel | None = None
        self.load_time_label: QLabel | None = None
        self.page_counter_label: QLabel | None = None
        self.download_progress: QProgressBar | None = None
        self.logo_label: QLabel | None = None

        # загрузка настроек (история, избранное)
        self._load_settings()

        # базовые параметры окна
        self.setWindowTitle("Windows Internet Explorer 7")
        self.resize(1100, 750)

        self._setup_styles()
        self._setup_browser()
        self._create_menu_bar()
        self._create_toolbars()
        self._create_status_bar()
        self._setup_connections()

        # таймеры
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._animate_status)

        self.load_timer = QTimer(self)
        self.load_timer.timeout.connect(self._update_load_time)

        # запускаем анимацию статуса
        self.status_timer.start(1000)

    # ---------- настройки и стили ----------

    def _load_settings(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.history = data.get("history", [])
                favs = data.get("favorites", [])
                self.favorites_manager.set_favorites(favs)
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")

    def _save_settings(self):
        try:
            data = {
                "history": self.history[-200:],  # ограничим размер
                "favorites": self.favorites_manager.favorites,
            }
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

    def _setup_styles(self):
        # упрощённая тема под IE7 / Vista
        self.setStyleSheet("""
        QMainWindow {
            background-color: #F1F5FB;
        }
        QMenuBar {
            background-color: #E3EDF9;
            font-family: Segoe UI;
            font-size: 9pt;
        }
        QMenuBar::item:selected {
            background: #C5D8F4;
        }
        QToolBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #F7FBFF, stop:1 #D7E3F2);
            border-bottom: 1px solid #9FB3D9;
            spacing: 3px;
        }
        QToolButton {
            font-family: Segoe UI;
            font-size: 9pt;
            padding: 3px 8px;
        }
        QStatusBar {
            background-color: #EEF2FB;
            font-family: Segoe UI;
            font-size: 8pt;
        }
        QLineEdit {
            border: 1px solid #9FB3D9;
            padding: 2px;
            font-family: Segoe UI;
            font-size: 9pt;
            background: white;
        }
        QPushButton {
            font-family: Segoe UI;
            font-size: 9pt;
        }
        QListWidget {
            font-family: Segoe UI;
            font-size: 9pt;
        }
        QTextEdit {
            font-family: Consolas, 'Courier New';
            font-size: 9pt;
        }
        QProgressBar {
            border: 1px solid #9FB3D9;
            background: white;
            text-align: center;
            font-family: Segoe UI;
            font-size: 8pt;
        }
        QProgressBar::chunk {
            background-color: #4A8BE8;
        }
        """)

    # ---------- браузер и базовые элементы ----------

    def _setup_browser(self):
        self.browser = QWebEngineView(self)
        self.browser.setUrl(QUrl(DEFAULT_HOME_PAGE))
        self.setCentralWidget(self.browser)

        # настройка скачиваний
        profile = self.browser.page().profile()
        profile.downloadRequested.connect(self._on_download_requested)

    def _create_menu_bar(self):
        menubar = self.menuBar()

        # Файл
        file_menu = menubar.addMenu("&Файл")
        new_tab_action = QAction("Новое окно", self)
        new_tab_action.triggered.connect(self._new_window)
        file_menu.addAction(new_tab_action)

        file_menu.addSeparator()

        open_file_action = QAction("Открыть...", self)
        open_file_action.triggered.connect(self._open_file_dialog)
        file_menu.addAction(open_file_action)

        save_page_action = QAction("Сохранить как...", self)
        save_page_action.triggered.connect(self._save_page)
        file_menu.addAction(save_page_action)

        file_menu.addSeparator()

        offline_action = QAction("Автономный режим", self, checkable=True)
        offline_action.triggered.connect(self._toggle_offline)
        file_menu.addAction(offline_action)

        file_menu.addSeparator()

        downloads_action = QAction("Загрузки...", self)
        downloads_action.triggered.connect(self.show_downloads)
        file_menu.addAction(downloads_action)

        file_menu.addSeparator()

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self._close_app)
        file_menu.addAction(exit_action)

        # Правка
        edit_menu = menubar.addMenu("&Правка")
        cut_action = QAction("Вырезать", self)
        cut_action.triggered.connect(self._cut)
        copy_action = QAction("Копировать", self)
        copy_action.triggered.connect(self._copy)
        paste_action = QAction("Вставить", self)
        paste_action.triggered.connect(self._paste)
        find_action = QAction("Найти на странице...", self)
        find_action.triggered.connect(self._find_on_page)

        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(find_action)

        # Вид
        view_menu = menubar.addMenu("&Вид")
        zoom_in_action = QAction("Увеличить", self)
        zoom_in_action.triggered.connect(self._zoom_in)
        zoom_out_action = QAction("Уменьшить", self)
        zoom_out_action.triggered.connect(self._zoom_out)
        zoom_reset_action = QAction("Сбросить масштаб", self)
        zoom_reset_action.triggered.connect(self._zoom_reset)

        view_menu.addAction(zoom_in_action)
        view_menu.addAction(zoom_out_action)
        view_menu.addAction(zoom_reset_action)

        view_menu.addSeparator()

        page_info_action = QAction("Свойства страницы", self)
        page_info_action.triggered.connect(self.show_page_info)
        view_menu.addAction(page_info_action)

        source_action = QAction("Просмотр исходного кода", self)
        source_action.triggered.connect(self.view_page_source)
        view_menu.addAction(source_action)

        fullscreen_action = QAction("Во весь экран", self)
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        # Избранное
        fav_menu = menubar.addMenu("&Избранное")
        add_fav_action = QAction("Добавить в избранное...", self)
        add_fav_action.triggered.connect(self.add_to_favorites)
        manage_fav_action = QAction("Управление избранным...", self)
        manage_fav_action.triggered.connect(self.show_favorites)

        fav_menu.addAction(add_fav_action)
        fav_menu.addAction(manage_fav_action)

        # Сервис
        tools_menu = menubar.addMenu("&Сервис")
        options_action = QAction("Свойства обозревателя...", self)
        options_action.triggered.connect(self.internet_options)
        tools_menu.addAction(options_action)

        tools_menu.addSeparator()

        cert_action = QAction("Сертификаты безопасности...", self)
        cert_action.triggered.connect(self.show_certificates)
        tools_menu.addAction(cert_action)

        dev_tools_action = QAction("Инструменты разработчика", self)
        dev_tools_action.triggered.connect(self.show_developer_tools)
        tools_menu.addAction(dev_tools_action)

        quick_cmd_action = QAction("Быстрые команды", self)
        quick_cmd_action.triggered.connect(self.show_quick_commands)
        tools_menu.addAction(quick_cmd_action)

        # Справка
        help_menu = menubar.addMenu("&Справка")
        about_action = QAction("О программе Internet Explorer", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _create_toolbars(self):
        # абсолютные пути к иконкам рядом со скриптом
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        back_icon_path = os.path.join(base_dir, "ie7_back.png")
        fwd_icon_path = os.path.join(base_dir, "ie7_forward.png")

        nav_toolbar = QToolBar("Навигация", self)
        nav_toolbar.setIconSize(QSize(24, 24))  # было 32x32, можно даже 20x20
        nav_toolbar.setMinimumHeight(32)        # или не задавать вообще
        self.addToolBar(nav_toolbar)

        # --- Кнопка "Назад" ---
        back_icon = QIcon(back_icon_path)
        back_btn = QToolButton()
        back_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        back_btn.setIcon(back_icon)
        back_btn.setIconSize(QSize(24, 18))
        back_btn.setToolTip("Назад")
        back_btn.clicked.connect(self.browser.back)
        nav_toolbar.addWidget(back_btn)

        # --- Кнопка "Вперёд" ---
        fwd_icon = QIcon(fwd_icon_path)
        forward_btn = QToolButton()
        forward_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)  
        forward_btn.setIcon(fwd_icon)
        forward_btn.setIconSize(QSize(24, 18))
        forward_btn.setToolTip("Вперёд")
        forward_btn.clicked.connect(self.browser.forward)
        nav_toolbar.addWidget(forward_btn)

    # дальше остальные кнопки (Стоп, Обновить, Домой, Избранное, Журнал, адресная строка) с тем же уровнем отступа

        # Стоп
        stop_btn = QToolButton()
        stop_btn.setText("Стоп")
        stop_btn.clicked.connect(self.browser.stop)
        nav_toolbar.addWidget(stop_btn)

        # Обновить
        refresh_btn = QToolButton()
        refresh_btn.setText("Обновить")
        refresh_btn.clicked.connect(self.browser.reload)
        nav_toolbar.addWidget(refresh_btn)

        # Домой
        home_btn = QToolButton()
        home_btn.setText("Домой")
        home_btn.clicked.connect(self.navigate_home)
        nav_toolbar.addWidget(home_btn)

        nav_toolbar.addSeparator()

        # Избранное
        favorites_btn = QToolButton()
        favorites_btn.setText("Избранное")
        favorites_btn.clicked.connect(self.show_favorites)
        nav_toolbar.addWidget(favorites_btn)

        # Журнал
        history_btn = QToolButton()
        history_btn.setText("Журнал")
        history_btn.clicked.connect(self.show_history)
        nav_toolbar.addWidget(history_btn)

        # -------- адресная строка оставляем как было --------
        addr_toolbar = QToolBar("Адрес", self)
        self.addToolBar(addr_toolbar)

        addr_label = QLabel("Адрес:")
        addr_toolbar.addWidget(addr_label)

        self.urlbar = QLineEdit()
        self.urlbar.setMinimumWidth(500)
        addr_toolbar.addWidget(self.urlbar)
        self.urlbar.returnPressed.connect(self._navigate_from_bar)

        go_btn = QToolButton()
        go_btn.setText("Перейти")
        go_btn.clicked.connect(self._navigate_from_bar)
        addr_toolbar.addWidget(go_btn)

        self.url_completer = QCompleter([h["url"] for h in self.history])
        self.url_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.urlbar.setCompleter(self.url_completer)

        stop_btn = QToolButton()
        stop_btn.setText("Стоп")
        stop_btn.clicked.connect(self.browser.stop)
        nav_toolbar.addWidget(stop_btn)

        refresh_btn = QToolButton()
        refresh_btn.setText("Обновить")
        refresh_btn.clicked.connect(self.browser.reload)
        nav_toolbar.addWidget(refresh_btn)

        home_btn = QToolButton()
        home_btn.setText("Домой")
        home_btn.clicked.connect(self.navigate_home)
        nav_toolbar.addWidget(home_btn)

        nav_toolbar.addSeparator()

        favorites_btn = QToolButton()
        favorites_btn.setText("Избранное")
        favorites_btn.clicked.connect(self.show_favorites)
        nav_toolbar.addWidget(favorites_btn)

        history_btn = QToolButton()
        history_btn.setText("Журнал")
        history_btn.clicked.connect(self.show_history)
        nav_toolbar.addWidget(history_btn)

        nav_toolbar.addSeparator()

        # Адресная строка
        addr_toolbar = QToolBar("Адрес", self)
        self.addToolBar(addr_toolbar)

        addr_label = QLabel("Адрес:")
        addr_toolbar.addWidget(addr_label)

        self.urlbar = QLineEdit()
        self.urlbar.setMinimumWidth(500)
        addr_toolbar.addWidget(self.urlbar)
        self.urlbar.returnPressed.connect(self._navigate_from_bar)

        go_btn = QToolButton()
        go_btn.setText("Перейти")
        go_btn.clicked.connect(self._navigate_from_bar)
        addr_toolbar.addWidget(go_btn)

        self.url_completer = QCompleter([h["url"] for h in self.history])
        self.url_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.urlbar.setCompleter(self.url_completer)

    def _create_status_bar(self):
        self.status = QStatusBar(self)
        self.setStatusBar(self.status)

        self.download_progress = QProgressBar()
        self.download_progress.setMaximumWidth(160)
        self.download_progress.setVisible(False)
        self.status.addPermanentWidget(self.download_progress)

        self.zone_label = QLabel("Интернет")
        self.status.addPermanentWidget(self.zone_label)

        self.offline_label = QLabel("Автономно")
        self.offline_label.setVisible(False)
        self.status.addPermanentWidget(self.offline_label)

        self.load_time_label = QLabel("0.0 c")
        self.status.addPermanentWidget(self.load_time_label)

        self.page_counter_label = QLabel("Страниц: 0")
        self.status.addPermanentWidget(self.page_counter_label)

        self.status.showMessage("Готово")

    def _setup_connections(self):
        self.browser.urlChanged.connect(self._on_url_changed)
        self.browser.loadFinished.connect(self._on_load_finished)
        self.browser.loadStarted.connect(self._on_load_started)
        self.browser.loadProgress.connect(self._on_load_progress)
    
    # ---------- события WebEngine ----------

    def _on_url_changed(self, url: QUrl):
        url_str = url.toString()
        self.urlbar.setText(url_str)
        self.urlbar.setCursorPosition(0)
        self._add_to_history(url_str, self.browser.title() or url_str)

    def _on_load_started(self):
        self.page_load_time = time.time()
        self.load_timer.start(100)
        self.status.showMessage("Загрузка страницы...")

    def _on_load_finished(self, ok: bool):
        self.load_timer.stop()
        if ok:
            self.status.showMessage("Готово")
        else:
            self.status.showMessage("Ошибка загрузки страницы")

        title = self.browser.title() or "Windows Internet Explorer 7"
        self.setWindowTitle(f"{title} - Windows Internet Explorer 7")

    def _on_load_progress(self, progress: int):
        # можно при желании показывать прогресс в статусе
        pass

    def _update_load_time(self):
        if self.page_load_time:
            elapsed = time.time() - self.page_load_time
            self.load_time_label.setText(f"{elapsed:.1f} c")

    def _animate_status(self):
        # простая "мигающая" точка в статусе при загрузке
        current = self.status.currentMessage()
        if "Загрузка" in current:
            if current.endswith("..."):
                self.status.showMessage(current.rstrip("."))
            else:
                self.status.showMessage(current + ".")

    # ---------- история ----------

    def _add_to_history(self, url: str, title: str):
        if not url or url == "about:blank":
            return
        # не добавляем дубликаты подряд
        if self.history and self.history[-1]["url"] == url:
            return

        item = {
            "url": url,
            "title": title,
            "time": datetime.now().strftime("%H:%M:%S"),
        }
        self.history.append(item)
        self.page_counter_label.setText(f"Страниц: {len(self.history)}")

        self.url_completer = QCompleter([h["url"] for h in self.history])
        self.url_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.urlbar.setCompleter(self.url_completer)

        self._save_settings()

    def clear_history(self):
        reply = QMessageBox.question(
            self,
            "Очистка журнала",
            "Очистить журнал посещённых страниц?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.history.clear()
            self.page_counter_label.setText("Страниц: 0")
            self._save_settings()
            self.status.showMessage("Журнал очищен", 3000)

    def show_history(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Журнал Internet Explorer 7")
        dialog.setFixedSize(480, 520)

        layout = QVBoxLayout(dialog)

        search_layout = QHBoxLayout()
        search_label = QLabel("Поиск:")
        search_edit = QLineEdit()
        search_layout.addWidget(search_label)
        search_layout.addWidget(search_edit)
        layout.addLayout(search_layout)

        list_widget = QListWidget()
        layout.addWidget(list_widget)

        shown_items = []

        def rebuild_list(items):
            list_widget.clear()
            shown_items.clear()
            for it in items:
                list_widget.addItem(f"{it['time']}  |  {it['title']}")
                shown_items.append(it)

        def on_search(text: str):
            text_l = text.lower()
            if not text_l:
                rebuild_list(self.history[-100:])
                return
            filtered = [
                h for h in self.history
                if text_l in h["title"].lower() or text_l in h["url"].lower()
            ]
            rebuild_list(filtered)

        search_edit.textChanged.connect(on_search)
        rebuild_list(self.history[-100:])

        btn_layout = QHBoxLayout()
        open_btn = QPushButton("Перейти")
        clear_btn = QPushButton("Очистить журнал")
        close_btn = QPushButton("Закрыть")
        btn_layout.addWidget(open_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        def open_selected():
            row = list_widget.currentRow()
            if 0 <= row < len(shown_items):
                url = shown_items[row]["url"]
                self.set_url(QUrl(url))
                dialog.close()

        open_btn.clicked.connect(open_selected)
        clear_btn.clicked.connect(self.clear_history)
        close_btn.clicked.connect(dialog.close)

        dialog.setLayout(layout)
        dialog.exec()

    # ---------- кэш (фиктивный) ----------

    def clear_cache(self):
        self.browser_cache.clear()
        self.status.showMessage("Кэш очищен", 3000)

    # ---------- навигация ----------

    def set_url(self, url: QUrl):
        if self.is_offline:
            QMessageBox.information(
                self,
                "Автономный режим",
                "Вы находитесь в автономном режиме. Подключите интернет или выключите автономный режим.",
            )
            return
        self.browser.setUrl(url)

    def _navigate_from_bar(self):
        url_text = self.urlbar.text().strip()
        if not url_text:
            return
        if not url_text.startswith(("http://", "https://")):
            url_text = "http://" + url_text
        self.set_url(QUrl(url_text))

    def navigate_home(self):
        self.set_url(QUrl(DEFAULT_HOME_PAGE))

    # ---------- зум ----------

    def _zoom_in(self):
        self.zoom_level = min(200, self.zoom_level + 10)
        self.browser.setZoomFactor(self.zoom_level / 100.0)
        self.status.showMessage(f"Масштаб: {self.zoom_level}%", 2000)

    def _zoom_out(self):
        self.zoom_level = max(30, self.zoom_level - 10)
        self.browser.setZoomFactor(self.zoom_level / 100.0)
        self.status.showMessage(f"Масштаб: {self.zoom_level}%", 2000)

    def _zoom_reset(self):
        self.zoom_level = 100
        self.browser.setZoomFactor(1.0)
        self.status.showMessage("Масштаб: 100%", 2000)

    # ---------- поиск, буфер обмена ----------

    def _find_on_page(self):
        text, ok = QInputDialog.getText(self, "Поиск на странице", "Введите текст:")
        if ok and text:
            self.browser.findText(text)

    def _cut(self):
        self.browser.page().triggerAction(QWebEnginePage.WebAction.Cut)

    def _copy(self):
        self.browser.page().triggerAction(QWebEnginePage.WebAction.Copy)

    def _paste(self):
        self.browser.page().triggerAction(QWebEnginePage.WebAction.Paste)

    # ---------- режимы окна ----------

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _toggle_offline(self, checked: bool):
        self.is_offline = checked
        self.offline_label.setVisible(checked)
        if checked:
            self.status.showMessage("Автономный режим включён", 3000)
        else:
            self.status.showMessage("Автономный режим выключен", 3000)

    # ---------- загрузки ----------

    def _on_download_requested(self, download):
        suggested = download.downloadFileName() or "загрузка"
        default_path = os.path.join(self.downloads_folder, suggested)

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл",
            default_path,
            "Все файлы (*.*)",
        )

        if not file_path:
            download.cancel()
            self.current_download = None
            return

        self.current_download = download
        self.download_progress.setVisible(True)
        self.download_progress.setValue(0)
        self.status.showMessage(f"Загрузка {os.path.basename(file_path)}...")

        download.downloadProgress.connect(self._on_download_progress)
        download.finished.connect(self._on_download_finished)
        download.setDownloadFileName(os.path.basename(file_path))
        download.setPath(file_path)
        download.accept()

    def _on_download_progress(self, received: int, total: int):
        if total > 0:
            percent = int(received * 100 / total)
            self.download_progress.setValue(percent)

    def _on_download_finished(self):
        self.download_progress.setVisible(False)
        self.status.showMessage("Загрузка завершена", 3000)

        if not self.current_download:
            return

        file_path = self.current_download.path()
        filename = os.path.basename(file_path)
        size_bytes = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        if size_bytes >= 1024:
            size_str = f"{size_bytes // 1024} КБ"
        else:
            size_str = f"{size_bytes} байт"

        self.download_manager.add_download(filename, file_path, size_str)
        self._show_download_complete_dialog(filename, file_path)

        self.current_download = None

    def _show_download_complete_dialog(self, filename: str, file_path: str):
        msg = QMessageBox(self)
        msg.setWindowTitle("Загрузка завершена")
        msg.setText(f"Файл «{filename}» успешно загружен.")
        msg.setIcon(QMessageBox.Icon.Information)

        open_btn = msg.addButton("Открыть", QMessageBox.ButtonRole.AcceptRole)
        folder_btn = msg.addButton("Открыть папку", QMessageBox.ButtonRole.ActionRole)
        close_btn = msg.addButton("Закрыть", QMessageBox.ButtonRole.RejectRole)

        msg.exec()

        clicked = msg.clickedButton()
        if clicked == open_btn:
            if os.path.exists(file_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        elif clicked == folder_btn:
            folder = os.path.dirname(file_path)
            if os.path.isdir(folder):
                QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def show_downloads(self):
        self.download_manager.show()
        self.download_manager.raise_()
        self.download_manager.activateWindow()

    # ---------- скриншот ----------

    def take_screenshot(self):
        screenshot_dir = os.path.join(self.downloads_folder, "Screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{ts}.png"
        path = os.path.join(screenshot_dir, filename)

        pixmap = self.browser.grab()
        if not pixmap.isNull():
            pixmap.save(path)
            self.status.showMessage(f"Скриншот сохранён: {filename}", 3000)
            QMessageBox.information(
                self,
                "Скриншот",
                f"Скриншот сохранён по пути:\n{path}",
            )
        else:
            QMessageBox.warning(self, "Скриншот", "Не удалось сделать скриншот.")

    # ---------- информация / исходный код ----------

    def show_page_info(self):
        url = self.browser.url().toString()
        title = self.browser.title() or url
        load_time = self.load_time_label.text()
        text = (
            f"Заголовок: {title}\n"
            f"Адрес: {url}\n"
            f"Время загрузки: {load_time}\n"
            f"Автономный режим: {'Да' if self.is_offline else 'Нет'}\n"
            f"Зона безопасности: {self.zone_label.text()}"
        )
        QMessageBox.information(self, "Свойства страницы", text)

    def view_page_source(self):
        def show_html(html: str):
            win = QMainWindow(self)
            win.setWindowTitle("Исходный код - Internet Explorer 7")
            win.resize(800, 600)
            edit = QTextEdit()
            edit.setPlainText(html)
            win.setCentralWidget(edit)
            win.show()
        self.browser.page().toHtml(show_html)

    # ---------- избранное ----------

    def add_to_favorites(self):
        url = self.browser.url().toString()
        title = self.browser.title() or url
        self.favorites_manager.favorites.append((title, url))
        self.favorites_manager._reload_list()
        self._save_settings()
        QMessageBox.information(
            self,
            "Избранное",
            f"Страница «{title}» добавлена в избранное.",
        )

    def show_favorites(self):
        self.favorites_manager.show()
        self.favorites_manager.raise_()
        self.favorites_manager.activateWindow()

    def show_certificates(self):
        self.certificates_manager.show()
        self.certificates_manager.raise_()
        self.certificates_manager.activateWindow()

    def show_quick_commands(self):
        self.quick_commands.update_info(len(self.history), len(self.browser_cache))
        self.quick_commands.show()
        self.quick_commands.raise_()
        self.quick_commands.activateWindow()

    # ---------- "инструменты разработчика" и о программе ----------

    def show_developer_tools(self):
        QMessageBox.information(
            self,
            "Инструменты разработчика",
            "В этом эмуляторе инструменты разработчика не реализованы.\n\n"
            "Можно добавить вывод отладочной информации, логов и т.п.",
        )

    def internet_options(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Свойства обозревателя")
        dialog.setFixedSize(440, 320)

        layout = QVBoxLayout(dialog)
        tabs = QTabWidget()
        general_tab = QWidget()
        g_layout = QVBoxLayout(general_tab)

        home_layout = QHBoxLayout()
        home_label = QLabel("Домашняя страница:")
        home_edit = QLineEdit(DEFAULT_HOME_PAGE)
        home_layout.addWidget(home_label)
        home_layout.addWidget(home_edit)
        g_layout.addLayout(home_layout)

        g_layout.addStretch()
        general_tab.setLayout(g_layout)
        tabs.addTab(general_tab, "Общие")

        layout.addWidget(tabs)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Отмена")
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)

        dialog.setLayout(layout)
        dialog.exec()

    def show_about(self):
        text = (
            "Windows Internet Explorer 7 (эмулятор)\n"
            "Создано на Python и PyQt6\n\n"
            "Этот проект не является продуктом Microsoft.\n"
        )
        QMessageBox.about(self, "О программе Internet Explorer", text)

    # ---------- file / app ----------

    def _open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть HTML файл",
            "",
            "HTML файлы (*.html *.htm);;Все файлы (*.*)",
        )
        if path:
            self.set_url(QUrl.fromLocalFile(path))

    def _save_page(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить страницу",
            "",
            "HTML файлы (*.html)",
        )
        if not path:
            return

        def save_html(html: str):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(html)
                self.status.showMessage(f"Страница сохранена: {path}", 4000)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Не удалось сохранить страницу:\n{e}",
                )

        self.browser.page().toHtml(save_html)

    def _new_window(self):
        new = IE7Browser()
        new.show()

    def _close_app(self):
        self._save_settings()
        self.close()

    def closeEvent(self, event):
        self._save_settings()
        super().closeEvent(event)


# ---------- точка входа ----------

def main():
    app = QApplication(sys.argv)
    browser = IE7Browser()
    browser.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()