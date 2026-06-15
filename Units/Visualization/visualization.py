"""Модуль для визуализации траекторий спутников."""

from datetime import datetime, timedelta
from tkinter import messagebox
import matplotlib.pyplot as plt

from Units.TleProcessor import tleProcessor


_lang_strings = {}


def localization_get(key, default=""):
    """Получение локализованного текста."""
    return _lang_strings.get(key, default)


def localization_set(lang_dict):
    """Установка языковых строк для визуализации."""
    global _lang_strings
    _lang_strings = lang_dict


def trajectory_build(satellite, duration_hours):
    """
    Построение траектории движения спутника.

    Args:
        satellite (dict): Данные спутника
        duration_hours (float): Длительность в часах
    """
    if not satellite:
        print("Ошибка: спутник не найден")
        return

    # Проверка наличия TLE данных
    tle_line1 = satellite.get("tle_line1", "")
    tle_line2 = satellite.get("tle_line2", "")

    if not tle_line1 or not tle_line2:
        print(f"Ошибка: отсутствуют TLE данные для спутника {satellite.get('name', 'Unknown')}")
        messagebox.showerror(
            localization_get("error_title", "Error"),
            localization_get("error_no_tle", "No TLE data available for this satellite")
        )
        return

    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=duration_hours)

    # Вычисление наземной траектории спутника
    positions = tleProcessor.trajectory_get(
        satellite,
        start_time,
        end_time,
        num_points=200
    )

    if not positions or len(positions) < 2:
        print(f"Не удалось вычислить траекторию для {satellite.get('name', 'Unknown')}")
        messagebox.showwarning(
            localization_get("warning_title", "Warning"),
            localization_get("warning_no_trajectory", "Cannot compute trajectory. Check TLE data.")
        )
        return

    lons = [p[0] for p in positions]
    lats = [p[1] for p in positions]

    # Проверка, не является ли траектория точкой
    if max(lons) - min(lons) < 0.01 and max(lats) - min(lats) < 0.01:
        print(f"Спутник {satellite.get('name', 'Unknown')} геостационарный - траектория - точка")
        # Для геостационарных спутников показываем специальное сообщение
        messagebox.showinfo(
            localization_get("info_title", "Information"),
            f"{satellite.get('name', 'Satellite')} is geostationary.\n"
            f"Position: Lon={lons[0]:.2f}°, Lat={lats[0]:.2f}°"
        )
        # Всё равно показываем точку на карте
        params = plt.subplots(figsize=(14, 8))
        ax = params[1]
        ax.plot(lons[0], lats[0], "bo", markersize=10, label=satellite.get('name', ''))
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel(localization_get("graph_x_longitude", "Longitude (degrees)"))
        ax.set_ylabel(localization_get("graph_x_latitude", "Latitude (degrees)"))
        ax.set_title(f"{satellite.get('name', '')} - Geostationary Satellite")
        ax.legend()
        plt.tight_layout()
        plt.show()
        return

    params = plt.subplots(figsize=(14, 8))
    ax = params[1]

    # Траектория
    ax.plot(
        lons,
        lats,
        "b-",
        linewidth=2,
        alpha=0.8,
        label=f"{satellite.get('name', '')} {localization_get(
            'graph_trajectory_duration',
            'trajectory'
        )}"
    )

    # Начальная точка (зелёный маркер)
    ax.plot(
        lons[0],
        lats[0],
        "go",
        markersize=8,
        label=localization_get("graph_trajectory_start", "Start")
    )

    # Конечная точка (красный маркер)
    ax.plot(
        lons[-1],
        lats[-1],
        "ro",
        markersize=8,
        label=localization_get("graph_trajectory_end", "End")
    )

    # Настройка графика
    ax.set_xlabel(localization_get("graph_x_longitude", "Longitude (degrees)"))
    ax.set_ylabel(localization_get("graph_x_latitude", "Latitude (degrees)"))
    ax.set_title(
        f"{localization_get('graph_title_trajectory', 'Satellite Trajectory')}"
        + f": {satellite.get('name', '')}\n"
        f"{localization_get('graph_trajectory_duration', 'Duration')}: "
        + f"{duration_hours} {localization_get('graph_trajectory_hours', 'hours')}"
    )
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Границы карты: долгота от -180 до 180, широта от -90 до 90
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)

    # Линии экватора и нулевого меридиана
    ax.axhline(
        y=0, color="gray",
        linestyle="--", alpha=0.5,
        label=localization_get("graph_equator", "Equator")
    )
    ax.axvline(
        x=0, color="gray",
        linestyle="--", alpha=0.5,
        label=localization_get("graph_prime_meridian", "Prime Meridian")
    )

    plt.tight_layout()
    plt.show()
