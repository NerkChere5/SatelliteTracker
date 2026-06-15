"""Модуль для работы с базой данных спутников"""

from tkinter import filedialog, messagebox, ttk
import os
import tkinter as tk
import pandas as pd

from Units.Common import common


_lang_strings = {}


def _checkboxes_toggle(vars_dict, select_var):
    """Выбрать/снять все чекбоксы."""
    for var in vars_dict.values():
        var.set(select_var.get())


def _countries_path_get(data_dir):
    """Путь к файлу со странами."""
    return os.path.join(data_dir, "countries.csv")


def _mapping_dialog_open(parent, csv_columns, expected_columns):
    """
    Диалог сопоставления столбцов CSV с полями базы данных.

    Args:
        parent: Родительский виджет
        csv_columns (list): Список столбцов из CSV
        expected_columns (dict): Ожидаемые поля

    Returns:
        dict: результат сопоставления
    """
    dialog = tk.Toplevel(parent)
    dialog.title(_language_get("csv_import_title", "Сопоставление столбцов"))
    dialog.geometry("500x400")
    dialog.transient(parent)
    dialog.grab_set()

    # Фрейм для списка
    main_frame = ttk.Frame(dialog, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(
        main_frame,
        text=_language_get("csv_import_header", "Сопоставьте столбцы из CSV с полями базы данных:"),
        font=("Arial", 10, "bold")).pack(pady=5
    )

    # Фрейм для таблицы сопоставления
    mapping_frame = ttk.Frame(main_frame)
    mapping_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    # Заголовки
    header_frame = ttk.Frame(mapping_frame)
    header_frame.pack(fill=tk.X)
    ttk.Label(
        header_frame,
        text=_language_get("csv_import_db_field", "Поле в БД"),
        width=20, anchor=tk.W
    ).pack(side=tk.LEFT, padx=5)
    ttk.Label(
        header_frame,
        text=_language_get("csv_import_csv_column", "Столбец из CSV"),
        width=30,
        anchor=tk.W
    ).pack(side=tk.LEFT, padx=5)

    separator = ttk.Separator(mapping_frame, orient="horizontal")
    separator.pack(fill=tk.X, pady=5)

    # Создание выпадающих списков для каждого поля
    comboboxes = {}

    # Добавляем опцию пропуска столбца
    csv_options = [_language_get("csv_import_skip", "(пропустить)")] + csv_columns

    for db_field, description in expected_columns.items():
        row_frame = ttk.Frame(mapping_frame)
        row_frame.pack(fill=tk.X, pady=2)

        ttk.Label(
            row_frame,
            text=f"{description} ({db_field}):",
            width=20,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=5)

        combo = ttk.Combobox(row_frame, values=csv_options, state="readonly", width=28)
        combo.pack(side=tk.LEFT, padx=5)
        # По умолчанию пытаемся найти совпадение по имени
        default_value = _language_get("csv_import_skip", "(пропустить)")
        for col in csv_columns:
            if col.lower() == db_field.lower() or col.lower() == description.lower():
                default_value = col
                break
        combo.set(default_value)
        comboboxes[db_field] = combo

    # Кнопки
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=10)

    result_mapping = {}

    def on_ok():
        nonlocal result_mapping
        result_mapping = {}
        skip_value = _language_get("csv_import_skip", "(пропустить)")
        for db_field, combo in comboboxes.items():
            selected = combo.get()
            if selected != skip_value:
                result_mapping[db_field] = selected
        dialog.destroy()

    def on_cancel():
        nonlocal result_mapping
        result_mapping = None
        dialog.destroy()

    ttk.Button(
        button_frame,
        text=_language_get("csv_import_ok", "OK"),
        command=on_ok
    ).pack(side=tk.LEFT, padx=5)
    ttk.Button(
        button_frame,
        text=_language_get("csv_import_cancel", "Отмена"),
        command=on_cancel
    ).pack(side=tk.LEFT, padx=5)

    # Центрирование диалога
    dialog.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() - dialog.winfo_width()) // 2
    y = parent.winfo_y() + (parent.winfo_height() - dialog.winfo_height()) // 2
    dialog.geometry(f"+{x}+{y}")

    dialog.wait_window()
    return result_mapping


def _language_get(key, default=""):
    """Получение локализованного текста."""
    return _lang_strings.get(key, default)


def _satellites_dataframe_get(data_dir):
    """
    Получение DataFrame со спутниками.

    Args:
        data_dir (str): Директория с данными

    Returns:
        pd.DataFrame: DataFrame со спутниками
    """
    filepath = _satellites_path_get(data_dir)

    if not os.path.exists(filepath):
        return pd.DataFrame()

    df = common.csv_import(filepath)
    return df if df is not None else pd.DataFrame()


def _satellites_path_get(data_dir):
    """Путь к файлу со спутниками."""
    return os.path.join(data_dir, "satellites.csv")


def _satellites_save(data_dir, satellites):
    """
    Сохранение списка спутников в CSV файл с помощью pandas.

    Args:
        data_dir (str): Директория с данными
        satellites (list): Список словарей с данными

    Returns:
        bool: True при успешном сохранении
    """
    filepath = _satellites_path_get(data_dir)
    if not satellites:
        return False

    df = common.list_transform(satellites)
    return common.csv_export(df, filepath)


def _selection_dialog_open(parent, all_columns):
    """
    Диалог выбора столбцов для экспорта.

    Args:
        parent: Родительский виджет
        all_columns (list): Список всех столбцов

    Returns:
        list: Выбранные столбцы или None при отмене
    """
    dialog = tk.Toplevel(parent)
    dialog.title(_language_get("csv_export_title", "Выбор столбцов для экспорта"))
    dialog.geometry("400x400")
    dialog.transient(parent)
    dialog.grab_set()

    main_frame = ttk.Frame(dialog, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(
        main_frame,
        text=_language_get("csv_export_header", "Выберите столбцы для экспорта:"),
        font=("Arial", 10, "bold")
    ).pack(pady=5)

    # Фрейм для чекбоксов с прокруткой
    canvas_frame = ttk.Frame(main_frame)
    canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)

    canvas = tk.Canvas(canvas_frame)
    scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Чекбоксы для каждого столбца
    check_vars = {}
    header_frame = ttk.Frame(scrollable_frame)
    header_frame.pack(fill=tk.X)
    ttk.Label(
        header_frame,
        text=_language_get("csv_export_select_all", "Выбрать все")
    ).pack(side=tk.LEFT, padx=5)

    select_all_var = tk.BooleanVar(value=True)
    select_all_check = ttk.Checkbutton(
        header_frame,
        variable=select_all_var,
        command=lambda: _checkboxes_toggle(check_vars, select_all_var)
    )
    select_all_check.pack(side=tk.LEFT, padx=5)

    separator = ttk.Separator(scrollable_frame, orient="horizontal")
    separator.pack(fill=tk.X, pady=5)

    for col in all_columns:
        var = tk.BooleanVar(value=True)
        check_vars[col] = var
        cb_frame = ttk.Frame(scrollable_frame)
        cb_frame.pack(fill=tk.X, pady=2)
        ttk.Checkbutton(cb_frame, text=col, variable=var).pack(anchor=tk.W, padx=20)

    # Кнопки
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=10)

    selected_columns = []

    def on_ok():
        nonlocal selected_columns
        selected_columns = [col for col, var in check_vars.items() if var.get()]
        dialog.destroy()

    def on_cancel():
        nonlocal selected_columns
        selected_columns = None
        dialog.destroy()

    ttk.Button(
        button_frame,
        text=_language_get("csv_import_ok", "OK"),
        command=on_ok
    ).pack(side=tk.LEFT, padx=5)
    ttk.Button(
        button_frame,
        text=_language_get("csv_import_cancel", "Отмена"),
        command=on_cancel
    ).pack(side=tk.LEFT, padx=5)

    # Центрирование
    dialog.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() - dialog.winfo_width()) // 2
    y = parent.winfo_y() + (parent.winfo_height() - dialog.winfo_height()) // 2
    dialog.geometry(f"+{x}+{y}")

    dialog.wait_window()
    return selected_columns


def csv_export(parent, data_dir):
    """
    Экспорт данных в CSV файл.

    Args:
        parent: Родительский виджет
        data_dir (str): Директория с данными

    Returns:
        bool: True при успешном экспорте
    """
    satellites = satellites_load(data_dir)

    if not satellites:
        messagebox.showwarning(
            _language_get("warning_title", "Предупреждение"),
            _language_get("csv_export_no_data", "Нет данных для экспорта")
        )
        return False

    # Выбор места сохранения
    filepath = filedialog.asksaveasfilename(
        title=_language_get("csv_export_save_title", "Сохранить CSV файл"),
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )

    if not filepath:
        return False

    df = common.list_transform(satellites)

    # Диалог выбора столбцов для экспорта
    columns_to_export = _selection_dialog_open(parent, df.columns.tolist())

    if columns_to_export is None:
        return False

    if columns_to_export:
        df = df[columns_to_export]

    try:
        df.to_csv(filepath, index=False, encoding="utf-8")
        messagebox.showinfo(
            _language_get("success_title", "Успех"),
            _language_get(
                "csv_export_success", "Данные экспортированы в {path}"
            ).format(path=filepath)
        )
        return True
    except (PermissionError, OSError) as e:
        messagebox.showerror(
            _language_get("error_title", "Ошибка"),
            _language_get(
                "csv_export_error", "Не удалось сохранить файл: {error}"
            ).format(error=e)
        )
        return False


def csv_import(parent, data_dir):
    """
    Импорт данных из CSV файла.

    Args:
        parent: Родительский виджет
        data_dir (str): Директория с данными

    Returns:
        bool: True при успешном импорте
    """
    # Выбор CSV файла через диалог
    filepath = filedialog.askopenfilename(
        title=_language_get("csv_import_select", "Выберите CSV файл"),
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )

    if not filepath:
        return False

    # Загрузка CSV
    try:
        df = pd.read_csv(filepath, encoding="utf-8")
        if df.empty:
            messagebox.showerror(
                _language_get("error_title", "Ошибка"),
                _language_get("csv_import_empty", "Файл пуст")
            )
            return False
    except (FileNotFoundError, UnicodeDecodeError, pd.errors.EmptyDataError,
            pd.errors.ParserError) as e:
        messagebox.showerror(
            _language_get("error_title", "Ошибка"),
            _language_get(
                "import_csv_load_error", "Не удалось загрузить файл: {error}"
            ).format(error=e)
        )
        return False

    # Определяем словарь ожидаемых столбцов
    expected_columns_dict = {
        "norad_id": _language_get("data_norad_id"),
        "name": _language_get("data_name"),
        "country": _language_get("data_country"),
        "launch_year": _language_get("data_launch_year"),
        "altitude": _language_get("data_altitude"),
        "inclination": _language_get("data_inclination"),
        "period": _language_get("data_period"),
        "tle_line1": _language_get("data_tle_line1"),
        "tle_line2": _language_get("data_tle_line2"),
    }

    # Диалог сопоставления столбцов
    mapping = _mapping_dialog_open(parent, df.columns.tolist(), expected_columns_dict)

    if mapping is None:
        return False

    # Преобразование данных согласно маппингу
    imported_data = []
    for x, row in df.iterrows():
        satellite = {}
        for db_field, csv_col in mapping.items():
            if csv_col and csv_col in row:
                value = row[csv_col]
                # Преобразование типов данных
                if db_field in ["norad_id", "launch_year"]:
                    try:
                        value = int(float(value)) if pd.notna(value) else 0
                    except (ValueError, TypeError):
                        value = 0
                elif db_field in ["altitude", "inclination", "period"]:
                    try:
                        value = float(value) if pd.notna(value) else 0.0
                    except (ValueError, TypeError):
                        value = 0.0
                else:
                    value = str(value) if pd.notna(value) else ""
            else:
                value = "" if db_field not in ["norad_id", "launch_year"] else 0
            satellite[db_field] = value
        imported_data.append(satellite)

    # Загрузка существующих данных для проверки дубликатов
    existing_satellites = satellites_load(data_dir)
    existing_ids = {str(s.get("norad_id", "")) for s in existing_satellites}

    # Фильтрация новых записей (без дубликатов)
    new_satellites = []
    duplicates = 0
    for sat in imported_data:
        if str(sat.get("norad_id", "")) not in existing_ids and sat.get("norad_id"):
            new_satellites.append(sat)
        else:
            duplicates += 1

    if not new_satellites:
        messagebox.showwarning(
            _language_get("warning_title"),
            _language_get("import_csv_no_new_data")
        )
        return False

    # Добавление новых записей
    all_satellites = existing_satellites + new_satellites
    success = _satellites_save(data_dir, all_satellites)

    if success:
        msg = _language_get(
            "import_csv_success", "Импортировано {count} спутников"
        ).format(count=len(new_satellites))
        if duplicates > 0:
            msg += f"\n{
                _language_get(
                    'import_csv_duplicates', 'Пропущено дубликатов: {count}'
                ).format(count=duplicates)
            }"
        messagebox.showinfo(_language_get("success_title", "Успех"), msg)
        return True

    messagebox.showerror(
        _language_get("error_title", "Ошибка"),
        _language_get("import_csv_save_error", "Не удалось сохранить данные")
    )
    return False


def language_set(lang_dict):
    """
    Установка языковых строк.

    Args:
        lang_dict (dict): Словарь с переводами
    """
    global _lang_strings
    _lang_strings = lang_dict


def satellite_add(data_dir, satellite):
    """Добавление спутника."""
    df = _satellites_dataframe_get(data_dir)

    # Проверка на дубликат по NORAD ID
    if "norad_id" in df.columns:
        existing = df[df["norad_id"].astype(str) == str(satellite.get("norad_id", ""))]
        if not existing.empty:
            return False

    # Добавление новой записи
    new_row = pd.DataFrame([satellite])
    df = pd.concat([df, new_row], ignore_index=True)

    return common.csv_export(df, _satellites_path_get(data_dir))


def satellite_by_id_get(data_dir, norad_id):
    """Получение спутника по ID."""
    df = _satellites_dataframe_get(data_dir)

    if df.empty or "norad_id" not in df.columns:
        return None

    mask = df["norad_id"].astype(str) == str(norad_id)
    if not mask.any():
        return None

    return df[mask].iloc[0].to_dict()


def satellite_delete(data_dir, norad_id):
    """Удаление спутника."""
    df = _satellites_dataframe_get(data_dir)

    if df.empty or "norad_id" not in df.columns:
        return False

    df = df[df["norad_id"].astype(str) != str(norad_id)]
    return common.csv_export(df, _satellites_path_get(data_dir))


def satellite_refresh(data_dir, norad_id, updated_data):
    """Обновление спутника."""
    df = _satellites_dataframe_get(data_dir)

    if df.empty or "norad_id" not in df.columns:
        return False

    mask = df["norad_id"].astype(str) == str(norad_id)
    if not mask.any():
        return False

    for key, value in updated_data.items():
        if key in df.columns:
            df.loc[mask, key] = value

    return common.csv_export(df, _satellites_path_get(data_dir))


def satellites_binary_export(data_dir):
    """Сохранение справочника в бинарный файл."""
    df = _satellites_dataframe_get(data_dir)

    if df.empty:
        return False, None

    storage_dir = "Storage"
    os.makedirs(storage_dir, exist_ok=True)

    timestamp = common.timestamp_get()
    filepath = os.path.join(storage_dir, f"dataSet_{timestamp}.pkl")

    success = common.binary_export(df, filepath)
    return success, filepath if success else None


def satellites_load(data_dir):
    """
    Загрузка списка спутников из CSV файла с помощью pandas.

    Args:
        data_dir (str): Директория с данными

    Returns:
        list: Список словарей с данными спутников
    """
    filepath = _satellites_path_get(data_dir)
    if not os.path.exists(filepath):
        return []

    df = common.csv_import(filepath)
    if df is None or df.empty:
        return []

    return common.dataframe_transform(df)
