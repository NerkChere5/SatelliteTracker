"""Главный модуль приложения для трекинга спутников."""

from tkinter import ttk, messagebox
import json
import os
import tkinter as tk

from Units.Database import database
from Units.Settings import settings
from Units.TleProcessor import tleProcessor
from Units.UI import ui


_app_config = {}
_app_lang = {}
_app_notebook = None
_app_root = None
_app_satellites_data = []
_app_status_var = None
_app_tabs = {}
_app_theme = {}


def _bar_status_build(root):
    """
    Создание строки состояния.

    Args:
        root (tk.Tk): Корневое окно

    Returns:
        tk.StringVar: Переменная для текста статуса
    """
    global _app_status_var
    _app_status_var = tk.StringVar()
    _app_status_var.set(_localization_get("status_ready", "Ready"))

    status_bar = ttk.Label(
        root,
        textvariable=_app_status_var,
        relief=tk.SUNKEN,
        anchor=tk.W
    )
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    return _app_status_var


def _bar_status_refresh(message):
    """
    Обновление строки состояния.

    Args:
        message (str): Новое сообщение
    """
    # global _app_status_var, _app_root
    if _app_status_var:
        _app_status_var.set(message)
        _app_root.update_idletasks()


def _config_load():
    """
    Загрузка конфигурационного файла Config.json.

    Returns:
        dict: Словарь с настройками конфигурации
    """
    config_path = os.path.join("Config", "Config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _data_init_get():
    """
    Загрузка начальных данных из справочников.

    Returns:
        list: Список спутников
    """
    # global _app_config
    _bar_status_refresh(_localization_get("status_loading", "Loading..."))

    satellites_data = database.satellites_load(_app_config["data_directory"])

    _bar_status_refresh(_localization_get("status_ready", "Ready"))
    return satellites_data


def _langs_load(lang_name):
    """
    Загрузка языкового файла Lang_{lang_name}.json.

    Args:
        lang_name (str): Название языка ("ru" или "eng")

    Returns:
        dict: Словарь с переводами
    """
    lang_path = os.path.join("Config", f"Lang_{lang_name}.json")

    if not os.path.exists(lang_path):
        raise FileNotFoundError(f"Language file not found: {lang_path}")

    with open(lang_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _localization_get(key, default=""):
    """
    Получение локализованного текста.

    Args:
        key (str): Ключ в словаре локализации
        default (str): Значение по умолчанию

    Returns:
        str: Локализованный текст
    """
    # global _app_lang
    return _app_lang.get(key, default)


def _menu_build(root):
    """
    Создание главного меню.

    Args:
        root (tk.Tk): Корневое окно

    Returns:
        tk.Menu: Созданное меню
    """
    menubar = tk.Menu(root)

    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(
        label=_localization_get("menu_exit", "Exit"),
        command=lambda: _on_closing(root)
    )
    menubar.add_cascade(
        label=_localization_get("menu_file", "File"),
        menu=file_menu
    )

    settings_menu = tk.Menu(menubar, tearoff=0)
    settings_menu.add_command(
        label=_localization_get("settings_language", "Language"),
        command=lambda: _settings_lang_open(root)
    )
    settings_menu.add_command(
        label=_localization_get("settings_theme", "Theme"),
        command=lambda: _settings_theme_open(root)
    )
    menubar.add_cascade(
        label=_localization_get("menu_settings", "Settings"),
        menu=settings_menu
    )

    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(
        label=_localization_get("about_title", "About"),
        command=_show_about
    )
    menubar.add_cascade(
        label=_localization_get("menu_help", "Help"),
        menu=help_menu
    )

    root.config(menu=menubar)
    return menubar


def _notebook_build(root):
    """
    Создание вкладок приложения.

    Args:
        root (tk.Tk): Корневое окно

    Returns:
        ttk.Notebook: Созданный виджет вкладок
    """
    global _app_tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Создание вкладок (без Settings)
    satellites_tab = ui.satellites_tab_build(notebook)
    reports_tab = ui.reports_tab_build(notebook)
    graphics_tab = ui.graphics_tab_build(notebook)
    visualization_tab = ui.visualization_tab_build(notebook)
    coordinates_tab = ui.coordinates_tab_build(notebook)

    _app_tabs = {
        "satellites": satellites_tab,
        "reports": reports_tab,
        "graphics": graphics_tab,
        "visualization": visualization_tab,
        "coordinates": coordinates_tab,
    }

    notebook.add(
        satellites_tab,
        text=_localization_get("tab_satellites", "Satellites")
    )
    notebook.add(
        reports_tab,
        text=_localization_get("tab_reports", "Reports")
    )
    notebook.add(
        graphics_tab,
        text=_localization_get("tab_graphics", "Graphics")
    )
    notebook.add(
        visualization_tab,
        text=_localization_get("tab_visualization", "Visualization")
    )
    notebook.add(
        coordinates_tab,
        text=_localization_get("tab_coordinates", "Coordinates")
    )

    return notebook


def _on_closing(root):
    """
    Обработка закрытия приложения.

    Args:
        root (tk.Tk): Корневое окно
    """
    if messagebox.askokcancel(
        _localization_get("confirmation_title", "Confirmation"),
        _localization_get("error_delete", "Are you sure?")
    ):
        root.destroy()


def _settings_lang_open(parent):
    """
    Открытие диалога выбора языка.

    Args:
        parent (tk.Tk/window): Родительское окно
    """
    # global _app_config
    dialog = tk.Toplevel(parent)
    dialog.title(_localization_get("settings_language", "Language"))
    dialog.geometry("300x150")
    dialog.transient(parent)
    dialog.grab_set()

    ttk.Label(
        dialog,
        text=_localization_get("settings_language", "Language") + ":"
    ).pack(pady=10)

    lang_var = tk.StringVar(value=_app_config["current_language"])
    langs = [
        ("Русский", "ru"),
        ("English", "eng"),
    ]

    for text, value in langs:
        ttk.Radiobutton(
            dialog,
            text=text,
            variable=lang_var,
            value=value
        ).pack(anchor=tk.W, padx=20)

    def _save_lang():
        new_lang = lang_var.get()
        if new_lang != _app_config["current_language"]:
            _app_config["current_language"] = new_lang
            settings.config_save(_app_config)
            messagebox.showinfo(
                _localization_get("info_title", "Information"),
                _localization_get("status_saved", "Saved") + ". " +
                _localization_get("settings_restart", "Restart required")
            )
        dialog.destroy()

    ttk.Button(
        dialog,
        text=_localization_get("btn_save", "Save"),
        command=_save_lang
    ).pack(pady=20)


def _settings_theme_open(parent):
    """
    Открытие диалога выбора темы.

    Args:
        parent (tk.Tk/window): Родительское окно
    """
    # global _app_config
    dialog = tk.Toplevel(parent)
    dialog.title(_localization_get("settings_theme", "Theme"))
    dialog.geometry("300x150")
    dialog.transient(parent)
    dialog.grab_set()

    ttk.Label(
        dialog,
        text=_localization_get("settings_theme", "Theme") + ":"
    ).pack(pady=10)

    theme_var = tk.StringVar(value=_app_config["current_theme"])
    themes = [
        (_localization_get("theme_dark", "Dark"), "dark"),
        (_localization_get("theme_light", "Light"), "light"),
    ]

    for text, value in themes:
        ttk.Radiobutton(
            dialog,
            text=text,
            variable=theme_var,
            value=value
        ).pack(anchor=tk.W, padx=20)

    def _save_theme():
        new_theme = theme_var.get()
        if new_theme != _app_config["current_theme"]:
            _app_config["current_theme"] = new_theme
            settings.config_save(_app_config)
            messagebox.showinfo(
                _localization_get("info_title", "Information"),
                _localization_get("status_saved", "Saved") + ". " +
                _localization_get("settings_restart", "Restart required")
            )
        dialog.destroy()

    ttk.Button(
        dialog,
        text=_localization_get("btn_save", "Save"),
        command=_save_theme
    ).pack(pady=20)


def _show_about():
    """Показать информацию о программе."""
    about_text = _localization_get("about_text", "Satellite Tracker\nVersion 1.0")
    messagebox.showinfo(
        _localization_get("about_title", "About"),
        about_text
    )


def _tabs_refresh():
    """Обновление всех вкладок."""
    # global _app_tabs
    ui.satellites_tab_refresh(_app_tabs.get("satellites"))
    ui.visualization_tab_refresh(_app_tabs.get("visualization"))
    ui.coordinates_tab_refresh(_app_tabs.get("coordinates"))


def _theme_apply(root):
    """
    Применение текущей темы к окну.

    Args:
        root (tk.Tk): Корневое окно
    """
    # global _app_theme
    root.configure(bg=_app_theme["bg_primary"])

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "TFrame",
        background=_app_theme["bg_primary"]
    )
    style.configure(
        "TLabel",
        background=_app_theme["bg_primary"],
        foreground=_app_theme["fg_primary"]
    )
    style.configure(
        "TButton",
        background=_app_theme["button_bg"],
        foreground=_app_theme["button_fg"]
    )
    style.map(
        "TButton",
        background=[(
            "active",
            _app_theme.get("accent_hover", _app_theme["accent"])
        )]
    )
    style.configure(
        "TNotebook",
        background=_app_theme["bg_primary"]
    )
    style.configure(
        "TNotebook.Tab",
        background=_app_theme["bg_secondary"],
        foreground=_app_theme["fg_primary"]
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", _app_theme["accent"])]
    )
    style.configure(
        "Treeview",
        background=_app_theme["bg_secondary"],
        foreground=_app_theme["fg_primary"],
        fieldbackground=_app_theme["bg_secondary"]
    )
    style.configure(
        "Treeview.Heading",
        background=_app_theme["bg_tertiary"],
        foreground=_app_theme["fg_primary"]
    )


def _theme_load(theme_name):
    """
    Загрузка темы оформления из Theme.json.

    Args:
        theme_name (str): Название темы ("dark" или "light")

    Returns:
        dict: Словарь с цветами темы
    """
    theme_path = os.path.join("Config", "Theme.json")

    if not os.path.exists(theme_path):
        raise FileNotFoundError(f"Theme file not found: {theme_path}")

    with open(theme_path, "r", encoding="utf-8") as f:
        themes = json.load(f)

    if theme_name not in themes:
        raise KeyError(f"Theme '{theme_name}' not found in Theme.json")

    return themes[theme_name]


def _window_start(root):
    """
    Настройка главного окна приложения.

    Args:
        root (tk.Tk): Корневое окно
    """
    # global _app_config
    root.title(_localization_get("app_title", "Satellite Tracker"))
    root.geometry(f"{_app_config['window_width']}x{_app_config['window_height']}")
    root.minsize(900, 700)
    root.protocol("WM_DELETE_WINDOW", lambda: _on_closing(root))


def main():
    """Точка входа в приложение."""
    global _app_config, _app_theme, _app_lang, _app_root, _app_satellites_data

    # Загрузка конфигурации
    _app_config = _config_load()
    _app_theme = _theme_load(_app_config["current_theme"])
    _app_lang = _langs_load(_app_config["current_language"])

    tleProcessor.consts_load()

    # Передача локализации в модули
    ui.language_set(_app_lang)
    database.language_set(_app_lang)
    ui.directory_set(_app_config.get("data_directory", "data"))

    # Создание GUI
    _app_root = tk.Tk()
    _window_start(_app_root)
    _theme_apply(_app_root)
    _menu_build(_app_root)
    _notebook_build(_app_root)
    _bar_status_build(_app_root)

    # Загрузка данных
    _app_satellites_data = _data_init_get()

    # Установка данных в UI
    ui.satellites_set(_app_satellites_data)

    # Обновление всех вкладок
    _tabs_refresh()

    # Запуск главного цикла
    _app_root.mainloop()


if __name__ == "__main__":
    main()
