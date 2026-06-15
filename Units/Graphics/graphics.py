"""Модуль для построения графических отчётов с использованием pandas и matplotlib."""


# import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt

from Units.Common import common


_lang_strings = {}


def _dataframe_get(satellites):
    """Преобразование списка спутников в DataFrame."""
    if not satellites:
        return pd.DataFrame()
    return pd.DataFrame(satellites)


def _language_get(key, default=""):
    """Получение локализованного текста."""
    return _lang_strings.get(key, default)


def altitude_histogram_build(satellites):
    """
    Построение гистограммы распределения высот спутников.

    Args:
        satellites (list): Список спутников

    Автор: Кошелев Н.Ю.
    """
    if not satellites:
        return

    df = _dataframe_get(satellites)

    if "altitude" not in df.columns:
        return

    # Фильтрация: только положительные значения высоты
    altitudes = df[df["altitude"].notna() & (df["altitude"] > 0)]["altitude"]

    if altitudes.empty:
        return

    params = plt.subplots(figsize=(10, 6))
    ax = params[1]
    ax.hist(altitudes, bins=20, color="steelblue", edgecolor="black", alpha=0.7)
    ax.set_xlabel(_language_get("graph_x_altitude", "Altitude (km)"))
    ax.set_ylabel(_language_get("graph_y_count", "Number of Satellites"))
    ax.set_title(_language_get("graph_title_altitude_hist", "Satellite Altitude Distribution"))
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def altitude_histogram_save(satellites):
    """Сохранение гистограммы высот в файл."""
    if not satellites:
        return None

    df = _dataframe_get(satellites)

    if "altitude" not in df.columns:
        return None

    altitudes = df[df["altitude"].notna() & (df["altitude"] > 0)]["altitude"]

    if altitudes.empty:
        return None

    params = plt.subplots(figsize=(10, 6))
    ax = params[1]
    ax.hist(altitudes, bins=20, color="steelblue", edgecolor="black", alpha=0.7)
    ax.set_xlabel(_language_get("graph_x_altitude", "Altitude (km)"))
    ax.set_ylabel(_language_get("graph_y_count", "Number of Satellites"))
    ax.set_title(_language_get("graph_title_altitude_hist", "Satellite Altitude Distribution"))
    ax.grid(True, alpha=0.3)

    output_dir = os.path.join("Output", "Graphics")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = common.timestamp_get()
    filename = os.path.join(output_dir, f"Graphic_altitudeDistribution_{timestamp}.png")

    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()

    return filename


def country_pie_build(satellites):
    """Построение круговой диаграммы спутников по странам."""
    if not satellites:
        return

    df = _dataframe_get(satellites)

    if "country" not in df.columns:
        return

    country_counts = df["country"].value_counts()

    if country_counts.empty:
        return

    params = plt.subplots(figsize=(10, 8))
    ax = params[1]
    ax.pie(
        country_counts.values,
        labels=country_counts.index,
        autopct="%1.1f%%",
        startangle=90,
    )
    ax.set_title(_language_get("graph_title_country_pie", "Satellites by Country"))

    plt.tight_layout()
    plt.show()


def country_pie_save(satellites):
    """Сохранение круговой диаграммы в файл."""
    if not satellites:
        return None

    df = _dataframe_get(satellites)

    if "country" not in df.columns:
        return None

    country_counts = df["country"].value_counts()

    if country_counts.empty:
        return None

    params = plt.subplots(figsize=(10, 8))
    ax = params[1]
    ax.pie(country_counts.values, labels=country_counts.index, autopct="%1.1f%%", startangle=90)
    ax.set_title(_language_get("graph_title_country_pie", "Satellites by Country"))

    output_dir = os.path.join("Output", "Graphics")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = common.timestamp_get()
    filename = os.path.join(output_dir, f"Graphic_countryPieChart_{timestamp}.png")

    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()

    return filename


def inclination_histogram_build(satellites):
    """Построение гистограммы распределения наклонений."""
    if not satellites:
        return

    df = _dataframe_get(satellites)

    if "inclination" not in df.columns:
        return

    inclinations = df[df["inclination"].notna() & (df["inclination"] > 0)]["inclination"]

    if inclinations.empty:
        return

    params = plt.subplots(figsize=(10, 6))
    ax = params[1]
    ax.hist(inclinations, bins=15, color="coral", edgecolor="black", alpha=0.7)
    ax.set_xlabel(_language_get("graph_x_inclination", "Inclination (degrees)"))
    ax.set_ylabel(_language_get("graph_y_count", "Number of Satellites"))
    ax.set_title(
        _language_get("graph_title_inclination_hist", "Satellite Inclination Distribution")
    )
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def inclination_histogram_save(satellites):
    """Сохранение гистограммы наклонений в файл."""
    if not satellites:
        return None

    df = _dataframe_get(satellites)

    if "inclination" not in df.columns:
        return None

    inclinations = df[df["inclination"].notna() & (df["inclination"] > 0)]["inclination"]

    if inclinations.empty:
        return None

    params = plt.subplots(figsize=(10, 6))
    ax = params[1]
    ax.hist(inclinations, bins=15, color="coral", edgecolor="black", alpha=0.7)
    ax.set_xlabel(_language_get("graph_x_inclination", "Inclination (degrees)"))
    ax.set_ylabel(_language_get("graph_y_count", "Number of Satellites"))
    ax.set_title(
        _language_get("graph_title_inclination_hist", "Satellite Inclination Distribution")
    )
    ax.grid(True, alpha=0.3)

    output_dir = os.path.join("Output", "Graphics")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = common.timestamp_get()
    filename = os.path.join(output_dir, f"Graphic_inclinationDistribution_{timestamp}.png")

    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()

    return filename


def language_set(lang_dict):
    """Установка языковых строк для графиков."""
    global _lang_strings
    _lang_strings = lang_dict


def launch_timeline_build(satellites):
    """
    Построение графика запусков по годам.
    Использует группировку pandas.
    """
    if not satellites:
        return

    df = _dataframe_get(satellites)

    if "launch_year" not in df.columns:
        return

    # Фильтрация: только года после 1950 (эра космических запусков)
    years_df = df[df["launch_year"].notna() & (df["launch_year"] > 1950)]

    if years_df.empty:
        return

    # Группировка по годам с подсчётом количества
    year_counts = years_df.groupby("launch_year").size()

    params = plt.subplots(figsize=(12, 6))
    ax = params[1]
    ax.bar(
        year_counts.index.astype(int),
        year_counts.values,
        color="forestgreen",
        edgecolor="black",
        alpha=0.7
    )
    ax.set_xlabel(_language_get("graph_x_year", "Launch Year"))
    ax.set_ylabel(_language_get("graph_y_count", "Number of Satellites"))
    ax.set_title(_language_get("graph_title_launch_timeline", "Satellite Launch Timeline by Year"))
    ax.grid(True, alpha=0.3, axis="y")

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def launch_timeline_save(satellites):
    """Сохранение графика запусков в файл."""
    if not satellites:
        return None

    df = _dataframe_get(satellites)

    if "launch_year" not in df.columns:
        return None

    years_df = df[df["launch_year"].notna() & (df["launch_year"] > 1950)]

    if years_df.empty:
        return None

    year_counts = years_df.groupby("launch_year").size()

    params = plt.subplots(figsize=(12, 6))
    ax = params[1]
    ax.bar(
        year_counts.index.astype(int),
        year_counts.values,
        color="forestgreen",
        edgecolor="black",
        alpha=0.7
    )
    ax.set_xlabel(_language_get("graph_x_year", "Launch Year"))
    ax.set_ylabel(_language_get("graph_y_count", "Number of Satellites"))
    ax.set_title(_language_get("graph_title_launch_timeline", "Satellite Launch Timeline by Year"))
    ax.grid(True, alpha=0.3, axis="y")

    plt.xticks(rotation=45)

    output_dir = os.path.join("Output", "Graphics")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = common.timestamp_get()
    filename = os.path.join(output_dir, f"Graphic_launchTimeline_{timestamp}.png")

    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()

    return filename
