"""Модуль для визуализации траекторий спутников."""

from datetime import datetime, timedelta
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

    if not positions:
        print("Не удалось вычислить траекторию")
        return

    lons = [p[0] for p in positions]
    lats = [p[1] for p in positions]

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
