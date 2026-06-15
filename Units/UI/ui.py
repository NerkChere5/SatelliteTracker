"""Модуль для создания графического интерфейса."""

from datetime import datetime
from tkinter import ttk, messagebox
import tkinter as tk

from Units.Database import database
from Units.Graphics import graphics
from Units.Reports import reports
from Units.TleProcessor import tleProcessor
from Units.Visualization import visualization


_data_dir_path = ""
_lang_strings = {}
_satellites_data = []


def _binary_save():
    """Сохранение справочника в бинарный файл."""
    # global _data_dir_path
    success, filepath = database.satellites_binary_export(_data_dir_path)
    if success:
        messagebox.showinfo(
            _language_get("info_title", "Information"),
            _language_get("success_saved", "Saved to {filepath}").format(filepath=filepath)
        )
    else:
        messagebox.showerror(
            _language_get("error_title", "Error"),
            _language_get("error_no_data", "No data available")
        )


def _csv_export(parent):
    """Экспорт данных в CSV с выбором столбцов."""
    # global _data_dir_path
    database.csv_export(parent, _data_dir_path)


def _csv_import(parent):
    """Импорт данных из CSV"""
    # global _data_dir_path, _satellites_data

    success = database.csv_import(parent, _data_dir_path)
    if success:
        # Перезагрузка данных
        _satellites_data[:] = database.satellites_load(_data_dir_path)
        # Обновляем таблицу
        current_frame = parent
        while current_frame:
            if hasattr(current_frame, "tree"):
                _satellites_table_refresh(current_frame)
                break
            current_frame = current_frame.master if hasattr(current_frame, "master") else None


def _language_get(key, default=""):
    """
    Получение локализованного текста.

    Args:
        key (str): Ключ в словаре локализации
        default (str): Значение по умолчанию

    Returns:
        str: Локализованный текст
    """
    return _lang_strings.get(key, default)


def _plot_chart_build(chart_type_name):
    """Построение графика."""
    # global _satellites_data

    if not _satellites_data:
        messagebox.showwarning(
            _language_get("warning_title", "Warning"),
            _language_get("warning_no_data", "No data to plot chart")
        )
        return

    chart_map = {
        _language_get("chart_type_altitude_hist", "Altitude Histogram"): "altitude_hist",
        _language_get("chart_type_inclination_hist", "Inclination Histogram"): "inclination_hist",
        _language_get("chart_type_country_pie", "Country Pie Chart"): "country_pie",
        _language_get("chart_type_launch_timeline", "Launch Timeline"): "launch_timeline",
    }
    chart_type = chart_map.get(chart_type_name, "altitude_hist")

    if chart_type == "altitude_hist":
        graphics.altitude_histogram_build(_satellites_data)
    elif chart_type == "inclination_hist":
        graphics.inclination_histogram_build(_satellites_data)
    elif chart_type == "country_pie":
        graphics.country_pie_build(_satellites_data)
    elif chart_type == "launch_timeline":
        graphics.launch_timeline_build(_satellites_data)


def _plot_chart_export(chart_type_name):
    """Сохранение графика в файл."""
    # global _satellites_data

    if not _satellites_data:
        messagebox.showwarning(
            _language_get("warning_title", "Warning"),
            _language_get("warning_no_data", "No data to plot chart")
        )
        return

    chart_map = {
        _language_get("chart_type_altitude_hist", "Altitude Histogram"): "altitude_hist",
        _language_get("chart_type_inclination_hist", "Inclination Histogram"): "inclination_hist",
        _language_get("chart_type_country_pie", "Country Pie Chart"): "country_pie",
        _language_get("chart_type_launch_timeline", "Launch Timeline"): "launch_timeline",
    }
    chart_type = chart_map.get(chart_type_name, "altitude_hist")

    filename = None
    if chart_type == "altitude_hist":
        filename = graphics.altitude_histogram_save(_satellites_data)
    elif chart_type == "inclination_hist":
        filename = graphics.inclination_histogram_save(_satellites_data)
    elif chart_type == "country_pie":
        filename = graphics.country_pie_save(_satellites_data)
    elif chart_type == "launch_timeline":
        filename = graphics.launch_timeline_save(_satellites_data)

    if filename:
        messagebox.showinfo(
            _language_get("info_title", "Information"),
            _language_get(
                "success_chart_saved", "Chart saved to {filename}"
            ).format(filename=filename)
        )
    else:
        messagebox.showerror(
            _language_get("error_title", "Error"),
            _language_get("error_no_data", "No data available")
        )


def _position_calc(
    frame,
    satellite_str,
    year_str,
    month_str,
    day_str,
    hour_str,
    minute_str,
    second_str
):
    """
    Вычисление позиции спутника на заданное время.

    Args:
        frame: Фрейм с результатами
        satellite_str (str): Строка с информацией о спутнике
        year_str, month_str, day_str, hour_str, minute_str, second_str: Компоненты времени
    """
    # global _satellites_data

    if not satellite_str:
        messagebox.showwarning(
            _language_get("warning_title", "Warning"),
            _language_get("error_no_selection", "Select a satellite")
        )
        return

    try:
        target_time = datetime(
            int(year_str),
            int(month_str),
            int(day_str),
            int(hour_str),
            int(minute_str),
            int(second_str)
        )
    except ValueError as e:
        messagebox.showerror(
            _language_get("error_title", "Error"),
            f"Invalid date/time: {e}"
        )
        return

    norad_id = satellite_str.split(" - ")[0]
    satellite = None
    for s in _satellites_data:
        if str(s.get("norad_id")) == norad_id:
            satellite = s
            break

    if not satellite:
        messagebox.showerror(
            _language_get("error_title", "Error"),
            _language_get("error_satellite_not_found", "Satellite not found")
        )
        return

    # Вычисление позиции
    position = tleProcessor.position_get(satellite, target_time)

    if not position:
        frame.result_text.delete(1.0, tk.END)
        frame.result_text.insert(
            tk.END,
            _language_get("coordinates_no_tle", "No TLE data available for this satellite")
        )
        return

    # Форматирование результатов
    result = []
    result.append("=" * 60)
    result.append(_language_get("coordinates_position_title", "SATELLITE POSITION CALCULATION"))
    result.append("=" * 60)
    result.append(f"\n{_language_get('satellite_name', 'Satellite')}: {satellite.get('name', 'Unknown')}")
    result.append(f"NORAD ID: {satellite.get('norad_id', 'Unknown')}")
    result.append(
        f"{_language_get('coordinates_time_label', 'Time')}: "
        f"{target_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
    )
    result.append("")
    result.append("-" * 40)
    result.append(_language_get("coordinates_cartesian", "Cartesian Coordinates (km):"))
    result.append(f"  X: {position['x']:.2f} km")
    result.append(f"  Y: {position['y']:.2f} km")
    result.append(f"  Z: {position['z']:.2f} km")
    result.append("")
    result.append("-" * 40)
    result.append(_language_get("coordinates_geographic", "Geographic Coordinates:"))
    result.append(f"  {_language_get('graph_x_latitude', 'Latitude')}: {position['latitude']:.4f}°")
    result.append(f"  {_language_get('graph_x_longitude', 'Longitude')}: {position['longitude']:.4f}°")
    result.append(f"  {_language_get('satellite_altitude', 'Altitude')}: {position['altitude']:.2f} km")
    result.append(f"  {_language_get('coordinates_radius', 'Radius')}: {position['radius']:.2f} km")
    result.append("")
    result.append("-" * 40)

    # Дополнительная информация об орбите
    result.append(_language_get("coordinates_orbital", "Orbital Information:"))
    result.append(f"  {_language_get('satellite_inclination', 'Inclination')}: {satellite.get('inclination', 'N/A')}°")
    result.append(f"  {_language_get('satellite_period', 'Period')}: {satellite.get('period', 'N/A')} min")
    result.append(f"  {_language_get('satellite_altitude', 'Altitude')}: {satellite.get('altitude', 'N/A')} km")

    result.append("")
    result.append("=" * 60)

    frame.result_text.delete(1.0, tk.END)
    frame.result_text.insert(tk.END, "\n".join(result))


def _report_build(frame, report_type):
    """Генерация отчёта."""
    # global _satellites_data
    if not _satellites_data:
        frame.text_widget.delete(1.0, tk.END)
        frame.text_widget.insert(
            tk.END,
            _language_get("report_no_data", "No satellite data available")
        )
        return

    if report_type == "by_country":
        report_text = reports.satellites_by_country_build(_satellites_data)
    elif report_type == "altitude_stats":
        report_text = reports.altitude_statistics_build(_satellites_data)
    elif report_type == "inclination_stats":
        report_text = reports.inclination_statistics_build(_satellites_data)
    elif report_type == "launch_years":
        report_text = reports.year_distribution_build(_satellites_data)
    else:
        report_text = _language_get("error_no_data", "No data available")

    frame.text_widget.delete(1.0, tk.END)
    frame.text_widget.insert(tk.END, report_text)


def _report_export(report_type):
    """Экспорт отчёта в файл."""
    # global _satellites_data
    if not _satellites_data:
        messagebox.showwarning(
            _language_get("warning_title", "Warning"),
            _language_get("warning_no_data_export", "No data to export")
        )
        return

    if report_type == "by_country":
        report_text = reports.satellites_by_country_build(_satellites_data)
        filename = reports.export(
            report_text,
            "satellites_by_country"
        )
    elif report_type == "altitude_stats":
        report_text = reports.altitude_statistics_build(_satellites_data)
        filename = reports.export(
            report_text,
            "altitude_statistics"
        )
    elif report_type == "inclination_stats":
        report_text = reports.inclination_statistics_build(_satellites_data)
        filename = reports.export(
            report_text,
            "inclination_statistics"
        )
    elif report_type == "launch_years":
        report_text = reports.year_distribution_build(_satellites_data)
        filename = reports.export(
            report_text,
            "launch_years"
        )
    else:
        return

    messagebox.showinfo(
        _language_get("info_title", "Information"),
        _language_get(
            "success_report_exported", "Report saved to {filename}"
        ).format(filename=filename)
    )


def _satellite_delete(parent):
    """Удаление выбранного спутника."""
    # global _data_dir_path, _satellites_data

    if not hasattr(parent, "tree") or not parent.tree.selection():
        messagebox.showwarning(
            _language_get("warning_title", "Warning"),
            _language_get("warning_select_delete", "Select a satellite to delete")
        )
        return

    if not messagebox.askyesno(
        _language_get("confirmation_title", "Confirmation"),
        _language_get("dialog_confirm_delete", "Delete selected satellite?")
    ):
        return

    selected = parent.tree.selection()[0]
    values = parent.tree.item(selected, "values")

    success = database.satellite_delete(_data_dir_path, values[0])

    if success:
        _satellites_data[:] = [
            s for s in _satellites_data
            if str(s.get("norad_id")) != str(values[0])
        ]
        _satellites_table_refresh(parent)


def _satellite_dialog_add(parent):
    """Диалог добавления спутника."""
    # global _data_dir_path, _satellites_data

    dialog = tk.Toplevel(parent)
    dialog.title(_language_get("dialog_add_title", "Add Satellite"))
    dialog.geometry("500x600")
    dialog.transient(parent)
    dialog.grab_set()

    fields = {}
    labels = [
        ("norad_id", _language_get("dialog_norad_id", "NORAD ID:")),
        ("name", _language_get("dialog_name", "Name:")),
        ("country", _language_get("dialog_country", "Country:")),
        ("launch_year", _language_get("dialog_launch_year", "Launch Year:")),
        ("altitude", _language_get("dialog_altitude", "Altitude (km):")),
        ("inclination", _language_get("dialog_inclination", "Inclination (°):")),
        ("period", _language_get("dialog_period", "Period (min):")),
        ("tle_line1", _language_get("dialog_tle_line1", "TLE Line 1:")),
        ("tle_line2", _language_get("dialog_tle_line2", "TLE Line 2:")),
    ]

    row = 0
    for key, label in labels:
        ttk.Label(dialog, text=label).grid(
            row=row,
            column=0,
            padx=5,
            pady=5,
            sticky=tk.W
        )
        entry = ttk.Entry(dialog, width=50)
        entry.grid(row=row, column=1, padx=5, pady=5)
        fields[key] = entry
        row += 1

    def save():
        # global _data_dir_path, _satellites_data

        new_satellite = {}
        for key, entry in fields.items():
            value = entry.get()
            if key in ["norad_id", "launch_year"]:
                try:
                    value = int(value) if value else 0
                except ValueError:
                    value = 0
            elif key in ["altitude", "inclination", "period"]:
                try:
                    value = float(value) if value else 0.0
                except ValueError:
                    value = 0.0
            new_satellite[key] = value

        if not new_satellite.get("name"):
            messagebox.showerror(
                _language_get("error_title", "Error"),
                _language_get("error_required", "Please fill required fields")
            )
            return

        success = database.satellite_add(_data_dir_path, new_satellite)
        if success:
            _satellites_data.append(new_satellite)
            _satellites_table_refresh(parent)
            dialog.destroy()
        else:
            messagebox.showerror(
                _language_get("error_title", "Error"),
                _language_get("error_duplicate", "Satellite with this NORAD ID already exists")
            )

    ttk.Button(
        dialog,
        text=_language_get("btn_save", "Save"),
        command=save
    ).grid(row=row, column=0, columnspan=2, pady=20)


def _satellite_dialog_edit(parent):
    """Диалог редактирования спутника."""
    # global _data_dir_path, _satellites_data

    if not hasattr(parent, "tree") or not parent.tree.selection():
        messagebox.showwarning(
            _language_get("warning_title", "Warning"),
            _language_get("warning_select_satellite", "Select a satellite to edit")
        )
        return

    selected = parent.tree.selection()[0]
    values = parent.tree.item(selected, "values")

    sat = database.satellite_by_id_get(_data_dir_path, values[0])

    if not sat:
        return

    dialog = tk.Toplevel(parent)
    dialog.title(_language_get("dialog_edit_title", "Edit Satellite"))
    dialog.geometry("500x600")
    dialog.transient(parent)
    dialog.grab_set()

    fields = {}
    labels = [
        ("name", _language_get("dialog_name", "Name:")),
        ("country", _language_get("dialog_country", "Country:")),
        ("launch_year", _language_get("dialog_launch_year", "Launch Year:")),
        ("altitude", _language_get("dialog_altitude", "Altitude (km):")),
        ("inclination", _language_get("dialog_inclination", "Inclination (°):")),
        ("period", _language_get("dialog_period", "Period (min):")),
        ("tle_line1", _language_get("dialog_tle_line1", "TLE Line 1:")),
        ("tle_line2", _language_get("dialog_tle_line2", "TLE Line 2:")),
    ]

    row = 0
    norad_label = _language_get(
        "dialog_satellite_norad_label",
        "NORAD ID: {norad_id}"
    ).format(norad_id=sat.get("norad_id", ""))
    ttk.Label(dialog, text=norad_label).grid(
        row=row,
        column=0,
        columnspan=2,
        padx=5,
        pady=5
    )
    row += 1

    for key, label in labels:
        ttk.Label(dialog, text=label).grid(
            row=row,
            column=0,
            padx=5,
            pady=5,
            sticky=tk.W
        )
        entry = ttk.Entry(dialog, width=50)
        entry.insert(0, str(sat.get(key, "")))
        entry.grid(row=row, column=1, padx=5, pady=5)
        fields[key] = entry
        row += 1

    def save():
        # global _data_dir_path, _satellites_data

        updated_data = {}
        for key, entry in fields.items():
            value = entry.get()
            if key == "launch_year":
                try:
                    value = int(value) if value else 0
                except ValueError:
                    value = 0
            elif key in ["altitude", "inclination", "period"]:
                try:
                    value = float(value) if value else 0.0
                except ValueError:
                    value = 0.0
            updated_data[key] = value

        success = database.satellite_refresh(
            _data_dir_path,
            sat["norad_id"],
            updated_data
        )
        if success:
            for i, s in enumerate(_satellites_data):
                if str(s.get("norad_id")) == str(sat["norad_id"]):
                    _satellites_data[i].update(updated_data)
                    break
            _satellites_table_refresh(parent)
            dialog.destroy()
        else:
            messagebox.showerror(
                _language_get("error_title", "Error"),
                _language_get("error_update_failed", "Failed to update data")
            )

    ttk.Button(
        dialog,
        text=_language_get("btn_save", "Save"),
        command=save
    ).grid(row=row, column=0, columnspan=2, pady=20)


def _satellites_table_refresh(frame):
    """Обновление таблицы спутников."""
    #global _satellites_data
    if hasattr(frame, "tree"):
        for item in frame.tree.get_children():
            frame.tree.delete(item)

        for sat in _satellites_data:
            frame.tree.insert(
                "",
                tk.END,
                values=(
                    sat.get("norad_id", ""),
                    sat.get("name", ""),
                    sat.get("country", ""),
                    sat.get("launch_year", ""),
                    sat.get("altitude", ""),
                    sat.get("inclination", ""),
                    sat.get("period", ""),
                )
            )


def coordinates_tab_build(parent):
    """
    Создание вкладки для вычисления текущих координат спутников.

    Args:
        parent: Родительский виджет

    Returns:
        tk.Frame: Созданный фрейм
    """
    # global _satellites_data

    frame = ttk.Frame(parent)

    # Панель выбора спутника
    select_frame = ttk.LabelFrame(
        frame,
        text=_language_get("coordinates_select_satellite", "Select Satellite")
    )
    select_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(
        select_frame,
        text=_language_get("dialog_select_satellite", "Satellite:")
    ).pack(side=tk.LEFT, padx=5, pady=5)

    satellite_combo = ttk.Combobox(
        select_frame,
        state="readonly",
        width=40
    )
    satellite_combo.pack(side=tk.LEFT, padx=5, pady=5)

    # Панель выбора времени
    time_frame = ttk.LabelFrame(
        frame,
        text=_language_get("coordinates_time", "Time Settings")
    )
    time_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(
        time_frame,
        text=_language_get("coordinates_time_label", "Time (UTC):")
    ).pack(side=tk.LEFT, padx=5, pady=5)

    # Переменные для компонентов даты и времени
    now = datetime.now()
    year_var = tk.StringVar(value=str(now.year))
    month_var = tk.StringVar(value=str(now.month))
    day_var = tk.StringVar(value=str(now.day))
    hour_var = tk.StringVar(value=str(now.hour))
    minute_var = tk.StringVar(value=str(now.minute))
    second_var = tk.StringVar(value="0")

    # Год
    ttk.Label(time_frame, text="Год:").pack(side=tk.LEFT, padx=2)
    year_spin = ttk.Spinbox(
        time_frame,
        from_=2020,
        to_=2030,
        textvariable=year_var,
        width=6
    )
    year_spin.pack(side=tk.LEFT, padx=2)

    # Месяц
    ttk.Label(time_frame, text="Месяц:").pack(side=tk.LEFT, padx=2)
    month_spin = ttk.Spinbox(
        time_frame,
        from_=1,
        to_=12,
        textvariable=month_var,
        width=4
    )
    month_spin.pack(side=tk.LEFT, padx=2)

    # День
    ttk.Label(time_frame, text="День:").pack(side=tk.LEFT, padx=2)
    day_spin = ttk.Spinbox(
        time_frame,
        from_=1,
        to_=31,
        textvariable=day_var,
        width=4
    )
    day_spin.pack(side=tk.LEFT, padx=2)

    # Час
    ttk.Label(time_frame, text="Час:").pack(side=tk.LEFT, padx=2)
    hour_spin = ttk.Spinbox(
        time_frame,
        from_=0,
        to_=23,
        textvariable=hour_var,
        width=4
    )
    hour_spin.pack(side=tk.LEFT, padx=2)

    # Минута
    ttk.Label(time_frame, text="Мин:").pack(side=tk.LEFT, padx=2)
    minute_spin = ttk.Spinbox(
        time_frame,
        from_=0,
        to_=59,
        textvariable=minute_var,
        width=4
    )
    minute_spin.pack(side=tk.LEFT, padx=2)

    # Секунда
    ttk.Label(time_frame, text="Сек:").pack(side=tk.LEFT, padx=2)
    second_spin = ttk.Spinbox(
        time_frame,
        from_=0,
        to_=59,
        textvariable=second_var,
        width=4
    )
    second_spin.pack(side=tk.LEFT, padx=2)

    # Кнопка "Текущее время"
    def set_current_time():
        now = datetime.now()
        year_var.set(str(now.year))
        month_var.set(str(now.month))
        day_var.set(str(now.day))
        hour_var.set(str(now.hour))
        minute_var.set(str(now.minute))
        second_var.set(str(now.second))

    ttk.Button(
        time_frame,
        text=_language_get("coordinates_current_time", "Now"),
        command=set_current_time
    ).pack(side=tk.LEFT, padx=10)

    # Кнопка вычисления
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Button(
        button_frame,
        text=_language_get("coordinates_calculate", "Calculate Position"),
        command=lambda: _position_calc(
            frame,
            satellite_combo.get(),
            year_var.get(),
            month_var.get(),
            day_var.get(),
            hour_var.get(),
            minute_var.get(),
            second_var.get()
        )
    ).pack()

    # Панель результатов
    result_frame = ttk.LabelFrame(
        frame,
        text=_language_get("coordinates_results", "Position Results")
    )
    result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    result_text = tk.Text(
        result_frame,
        wrap=tk.WORD,
        height=20,
        font=("Courier", 10)
    )
    scrollbar = ttk.Scrollbar(
        result_frame,
        orient=tk.VERTICAL,
        command=result_text.yview
    )
    result_text.configure(yscrollcommand=scrollbar.set)

    result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    frame.result_text = result_text

    # Обновление списка спутников
    def update_satellite_list():
        # global _satellites_data
        names = [
            f"{s.get('norad_id', '')} - {s.get('name', '')}"
            for s in _satellites_data
        ]
        satellite_combo["values"] = names
        if names:
            satellite_combo.set(names[0])

    frame.update_satellite_list = update_satellite_list
    update_satellite_list()

    return frame


def coordinates_tab_refresh(frame):
    """Обновление вкладки координат."""
    if frame and hasattr(frame, "update_satellite_list"):
        frame.update_satellite_list()



def directory_set(data_dir):
    """Установка директории с данными."""
    global _data_dir_path
    _data_dir_path = data_dir


def graphics_tab_build(parent):
    """Создание вкладки графиков."""
    frame = ttk.Frame(parent)

    control_panel = ttk.Frame(frame)
    control_panel.pack(fill=tk.X, padx=5, pady=5)

    chart_types = [
        (_language_get("chart_type_altitude_hist", "Altitude Histogram"), "altitude_hist"),
        (_language_get("chart_type_inclination_hist", "Inclination Histogram"), "inclination_hist"),
        (_language_get("chart_type_country_pie", "Country Pie Chart"), "country_pie"),
        (_language_get("chart_type_launch_timeline", "Launch Timeline"), "launch_timeline"),
    ]

    ttk.Label(
        control_panel,
        text=_language_get("chart_type_label", "Chart type:")
    ).pack(side=tk.LEFT, padx=5)

    chart_var = tk.StringVar(value="altitude_hist")
    chart_combo = ttk.Combobox(
        control_panel,
        textvariable=chart_var,
        values=[t[0] for t in chart_types],
        state="readonly",
        width=30
    )
    chart_combo.pack(side=tk.LEFT, padx=5)

    ttk.Button(
        control_panel,
        text=_language_get("btn_plot", "Plot"),
        command=lambda: _plot_chart_build(chart_var.get())
    ).pack(side=tk.LEFT, padx=5)

    ttk.Button(
        control_panel,
        text=_language_get("btn_save", "Save"),
        command=lambda: _plot_chart_export(chart_var.get())
    ).pack(side=tk.LEFT, padx=5)

    frame.chart_var = chart_var

    return frame


def language_set(lang_dict):
    """
    Установка языковых строк для UI.

    Args:
        lang_dict (dict): Словарь с переводами
    """
    global _lang_strings
    _lang_strings = lang_dict
    reports.language_set(lang_dict)
    graphics.language_set(lang_dict)
    visualization.localization_set(lang_dict)


def plot_trajectory_build(satellite_str, duration_str):
    """Построение траектории."""
    # global _satellites_data

    if not satellite_str:
        messagebox.showwarning(
            _language_get("warning_title", "Warning"),
            _language_get("error_no_selection", "Select a satellite")
        )
        return

    try:
        duration_hours = float(duration_str)
    except ValueError:
        messagebox.showerror(
            _language_get("error_title", "Error"),
            _language_get("error_invalid_duration", "Invalid duration")
        )
        return

    norad_id = satellite_str.split(" - ")[0]
    satellite = None
    for s in _satellites_data:
        if str(s.get("norad_id")) == norad_id:
            satellite = s
            break

    if not satellite:
        messagebox.showerror(
            _language_get("error_title", "Error"),
            _language_get("error_satellite_not_found", "Satellite not found")
        )
        return

    visualization.trajectory_build(satellite, duration_hours)


def reports_tab_build(parent):
    """Создание вкладки отчётов."""
    frame = ttk.Frame(parent)

    # Левая панель
    left_panel = ttk.Frame(frame)
    left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

    report_types = [
        (_language_get("report_type_by_country", "Satellites by Country"), "by_country"),
        (_language_get("report_type_altitude_stats", "Altitude Statistics"), "altitude_stats"),
        (
            _language_get("report_type_inclination_stats", "Inclination Statistics"),
            "inclination_stats"
        ),
        (_language_get("report_type_launch_years", "Launch Years Distribution"), "launch_years"),
    ]

    ttk.Label(
        left_panel,
        text=_language_get("report_type_label", "Report type:")
    ).pack(anchor=tk.W)

    report_var = tk.StringVar(value="by_country")

    for text, value in report_types:
        ttk.Radiobutton(
            left_panel,
            text=text,
            variable=report_var,
            value=value
        ).pack(anchor=tk.W, pady=2)

    ttk.Button(
        left_panel,
        text=_language_get("btn_generate", "Generate"),
        command=lambda: _report_build(frame, report_var.get())
    ).pack(pady=20)

    ttk.Button(
        left_panel,
        text=_language_get("btn_export", "Export"),
        command=lambda: _report_export(report_var.get())
    ).pack(pady=5)

    # Правая панель
    right_panel = ttk.Frame(frame)
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    text_widget = tk.Text(right_panel, wrap=tk.WORD, height=30, width=60)
    scrollbar = ttk.Scrollbar(
        right_panel,
        orient=tk.VERTICAL,
        command=text_widget.yview
    )
    text_widget.configure(yscrollcommand=scrollbar.set)

    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    frame.text_widget = text_widget

    return frame


def satellites_set(data):
    """Установка данных о спутниках."""
    global _satellites_data
    _satellites_data = data


def satellites_tab_build(parent):
    """Создание вкладки управления спутниками."""
    frame = ttk.Frame(parent)

    # Панель инструментов
    toolbar = ttk.Frame(frame)
    toolbar.pack(fill=tk.X, padx=5, pady=5)

    ttk.Button(
        toolbar,
        text=_language_get("btn_add", "Add"),
        command=lambda: _satellite_dialog_add(frame)
    ).pack(side=tk.LEFT, padx=2)

    ttk.Button(
        toolbar,
        text=_language_get("btn_edit", "Edit"),
        command=lambda: _satellite_dialog_edit(frame)
    ).pack(side=tk.LEFT, padx=2)

    ttk.Button(
        toolbar,
        text=_language_get("btn_delete", "Delete"),
        command=lambda: _satellite_delete(frame)
    ).pack(side=tk.LEFT, padx=2)

    ttk.Button(
        toolbar,
        text=_language_get("btn_refresh", "Refresh"),
        command=lambda: _satellites_table_refresh(frame)
    ).pack(side=tk.LEFT, padx=2)

    ttk.Button(
        toolbar,
        text=_language_get("btn_import_csv", "Import CSV"),
        command=lambda: _csv_import(frame)
    ).pack(side=tk.LEFT, padx=2)

    ttk.Button(
        toolbar,
        text=_language_get("btn_export_csv", "Export CSV"),
        command=lambda: _csv_export(frame)
    ).pack(side=tk.LEFT, padx=2)

    ttk.Button(
        toolbar,
        text=_language_get("toolbar_save_binary", "Save to binary"),
        command=lambda: _binary_save()
    ).pack(side=tk.LEFT, padx=2)

    # Таблица со спутниками
    columns = (
        "norad_id",
        "name",
        "country",
        "launch_year",
        "altitude",
        "inclination",
        "period"
    )
    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        height=20
    )

    tree.heading("norad_id", text=_language_get("table_norad", "NORAD ID"))
    tree.heading("name", text=_language_get("table_name", "Name"))
    tree.heading("country", text=_language_get("table_country", "Country"))
    tree.heading("launch_year", text=_language_get("table_launch_year", "Launch Year"))
    tree.heading("altitude", text=_language_get("table_altitude", "Altitude (km)"))
    tree.heading("inclination", text=_language_get("table_inclination", "Inclination (°)"))
    tree.heading("period", text=_language_get("table_period", "Period (min)"))

    tree.column("norad_id", width=80)
    tree.column("name", width=200)
    tree.column("country", width=120)
    tree.column("launch_year", width=80)
    tree.column("altitude", width=80)
    tree.column("inclination", width=100)
    tree.column("period", width=80)

    scrollbar = ttk.Scrollbar(
        frame,
        orient=tk.VERTICAL,
        command=tree.yview
    )
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    frame.tree = tree

    _satellites_table_refresh(frame)

    return frame


def satellites_tab_refresh(frame):
    """Обновление вкладки спутников."""
    if frame and hasattr(frame, "tree"):
        _satellites_table_refresh(frame)


def visualization_tab_build(parent):
    """Создание вкладки визуализации траекторий."""
    frame = ttk.Frame(parent)

    select_frame = ttk.Frame(frame)
    select_frame.pack(fill=tk.X, padx=5, pady=5)

    ttk.Label(
        select_frame,
        text=_language_get("dialog_select_satellite", "Select satellite:")
    ).pack(side=tk.LEFT, padx=5)

    satellite_combo = ttk.Combobox(
        select_frame,
        state="readonly",
        width=40
    )
    satellite_combo.pack(side=tk.LEFT, padx=5)

    ttk.Label(
        select_frame,
        text=_language_get("dialog_duration_hours", "Duration (hours):")
    ).pack(side=tk.LEFT, padx=5)

    duration_entry = ttk.Entry(select_frame, width=10)
    duration_entry.insert(0, "24")
    duration_entry.pack(side=tk.LEFT, padx=5)

    ttk.Button(
        select_frame,
        text=_language_get("dialog_trajectory", "Plot Trajectory"),
        command=lambda: plot_trajectory_build(
            satellite_combo.get(),
            duration_entry.get()
        )
    ).pack(side=tk.LEFT, padx=20)

    def update_satellite_list():
        # global _satellites_data
        names = [
            f"{s.get('norad_id', '')} - {s.get('name', '')}"
            for s in _satellites_data
        ]
        satellite_combo["values"] = names

    frame.update_satellite_list = update_satellite_list
    update_satellite_list()

    return frame


def visualization_tab_refresh(frame):
    """Обновление вкладки визуализации."""
    if frame and hasattr(frame, "update_satellite_list"):
        frame.update_satellite_list()
