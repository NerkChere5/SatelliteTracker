"""Модуль для формирования текстовых отчётов с использованием pandas."""

# from collections import Counter
import os
import pandas as pd

from Units.Common import common


_lang_strings = {}


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


def _satellites_dataframe_get(satellites):
    """
    Преобразование списка спутников в DataFrame.

    Args:
        satellites (list): Список спутников

    Returns:
        pd.DataFrame: DataFrame с данными
    """
    if not satellites:
        return pd.DataFrame()
    return pd.DataFrame(satellites)


def altitude_statistics_build(satellites):
    """
    Статистический отчёт по высотам.
    Использует описательные статистики pandas.

    Args:
        satellites (list): Список спутников

    Returns:
        str: Текст отчёта
    """
    if not satellites:
        return _language_get("report_no_data", "No satellite data available")

    df = _satellites_dataframe_get(satellites)

    if "altitude" not in df.columns:
        return _language_get("report_no_altitude", "No altitude data available")

    # Удаление NaN и нулевых значений
    altitudes_df = df[df["altitude"].notna() & (df["altitude"] > 0)]

    if altitudes_df.empty:
        return _language_get("report_no_altitude", "No altitude data available")

    n = len(altitudes_df)
    min_alt = altitudes_df["altitude"].min()
    max_alt = altitudes_df["altitude"].max()
    mean_alt = altitudes_df["altitude"].mean()
    median_alt = altitudes_df["altitude"].median()
    variance = altitudes_df["altitude"].var()
    std_dev = altitudes_df["altitude"].std()

    report = []
    report.append("=" * 60)
    report.append(
        _language_get(
            "report_title_altitude",
            "STATISTICAL REPORT: Satellite Altitude (km)"
        )
    )
    report.append("=" * 60)
    report.append(
        f"\n{_language_get('report_col_stat', 'Statistic'):<30} "
        f"{_language_get('report_col_value', 'Value'):<15}"
    )
    report.append("-" * 45)
    report.append(
        f"{_language_get('report_col_count', 'Count'):<30} {n:<15}"
    )
    report.append(
        f"{_language_get('report_stat_min', 'Minimum'):<30} {min_alt:<15.2f}"
    )
    report.append(
        f"{_language_get('report_stat_max', 'Maximum'):<30} {max_alt:<15.2f}"
    )
    report.append(
        f"{_language_get('report_stat_mean', 'Mean'):<30} {mean_alt:<15.2f}"
    )
    report.append(
        f"{_language_get('report_stat_median', 'Median'):<30} {median_alt:<15.2f}"
    )
    report.append(
        f"{_language_get('report_stat_variance', 'Variance'):<30} {variance:<15.2f}"
    )
    report.append(
        f"{_language_get('report_stat_std', 'Standard Deviation'):<30} {std_dev:<15.2f}"
    )
    report.append("=" * 60)

    # Категоризация по высоте (LEO, MEO, HEO, GEO)
    report.append("\n" + _language_get("report_category_label", "CATEGORIZATION:"))
    report.append("-" * 40)

    def categorize_altitude(alt):
        if alt < 500:
            return _language_get("report_category_leo", "LEO < 500 km")
        if alt < 2000:
            return _language_get("report_category_meo", "MEO 500-2000 km")
        if alt < 35786:
            return _language_get("report_category_heo", "HEO 2000-35786 km")

        return _language_get("report_category_geo", "GEO ~35786 km")

    altitudes_df_copy = altitudes_df.copy()
    altitudes_df_copy["category"] = altitudes_df_copy["altitude"].apply(categorize_altitude)
    category_counts = altitudes_df_copy.groupby("category").size()

    for category, count in category_counts.items():
        percentage = (count / n) * 100
        report.append(f"{category:<40} {count:>3} ({percentage:>5.1f}%)")

    report.append("=" * 60)

    return "\n".join(report)


def export(report_text, report_name):
    """
    Экспорт отчёта в файл.

    Args:
        report_text (str): Текст отчёта
        report_name (str): Название отчёта

    Returns:
        str: Путь к сохранённому файлу
    """
    output_dir = os.path.join("Output", "Reports")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = common.timestamp_get()
    filename = os.path.join(
        output_dir,
        f"Report_{report_name}_{timestamp}.txt"
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report_text)

    return filename


def inclination_statistics_build(satellites):
    """
    Статистический отчёт по наклонениям.
    Использует описательные статистики pandas.

    Args:
        satellites (list): Список спутников

    Returns:
        str: Текст отчёта
    """
    if not satellites:
        return _language_get("report_no_data", "No satellite data available")

    df = _satellites_dataframe_get(satellites)

    if "inclination" not in df.columns:
        return _language_get(
            "report_no_inclination",
            "No inclination data available"
        )

    incl_df = df[df["inclination"].notna() & (df["inclination"] > 0)]

    if incl_df.empty:
        return _language_get(
            "report_no_inclination",
            "No inclination data available"
        )

    n = len(incl_df)
    min_inc = incl_df["inclination"].min()
    max_inc = incl_df["inclination"].max()
    mean_inc = incl_df["inclination"].mean()
    variance = incl_df["inclination"].var()
    std_dev = incl_df["inclination"].std()

    report = []
    report.append("=" * 60)
    report.append(
        _language_get(
            "report_title_inclination",
            "STATISTICAL REPORT: Satellite Inclination (degrees)"
        )
    )
    report.append("=" * 60)
    report.append(
        f"\n{_language_get('report_col_stat', 'Statistic'):<30} "
        f"{_language_get('report_col_value', 'Value'):<15}"
    )
    report.append("-" * 45)
    report.append(
        f"{_language_get('report_col_count', 'Count'):<30} {n:<15}"
    )
    report.append(
        f"{_language_get('report_stat_min', 'Minimum'):<30} {min_inc:<15.2f}"
    )
    report.append(
        f"{_language_get('report_stat_max', 'Maximum'):<30} {max_inc:<15.2f}"
    )
    report.append(
        f"{_language_get('report_stat_mean', 'Mean'):<30} {mean_inc:<15.2f}"
    )
    report.append(
        f"{_language_get('report_stat_variance', 'Variance'):<30} {variance:<15.2f}"
    )
    report.append(
        f"{_language_get('report_stat_std', 'Standard Deviation'):<30} {std_dev:<15.2f}"
    )
    report.append("=" * 60)

    # Таблица частот с использованием pandas cut
    report.append("\n" + _language_get("report_frequency_table", "FREQUENCY TABLE:"))
    report.append("-" * 60)
    report.append(
        f"{_language_get('report_range', 'Range (°)'):<20} "
        f"{_language_get('report_col_count', 'Count'):<10} "
        f"{_language_get('report_col_percent', 'Percent (%)'):<10}"
    )
    report.append("-" * 40)

    # Диапазоны наклонений: 0-30, 30-60, 60-90, 90-100, 100-180 градусов
    bins = [0, 30, 60, 90, 100, 180]
    labels = ["0-30", "30-60", "60-90", "90-100", "100-180"]

    incl_df_copy = incl_df.copy()
    incl_df_copy["range"] = pd.cut(
        incl_df_copy["inclination"],
        bins=bins,
        labels=labels,
        right=False
    )
    range_counts = incl_df_copy.groupby("range", observed=True).size()

    for range_label, count in range_counts.items():
        percentage = (count / n) * 100
        report.append(
            f"{range_label:<20} {count:<10} {percentage:<10.1f}"
        )

    report.append("=" * 60)

    return "\n".join(report)


def language_set(lang_dict):
    """
    Установка языковых строк для отчётов.

    Args:
        lang_dict (dict): Словарь с переводами
    """
    global _lang_strings
    _lang_strings = lang_dict


def satellites_by_country_build(satellites):
    """
    Отчёт: количество спутников по странам.
    Использует операции проекции и группировки pandas.

    Args:
        satellites (list): Список спутников

    Returns:
        str: Текст отчёта
    """
    if not satellites:
        return _language_get("report_no_data", "No satellite data available")

    df = _satellites_dataframe_get(satellites)

    # Группировка по стране с подсчётом количества
    country_counts = df.groupby("country").size().reset_index(name="count")
    country_counts = country_counts.sort_values("count", ascending=False)

    total = len(df)
    country_counts["percent"] = (country_counts["count"] / total) * 100

    report = []
    report.append("=" * 60)
    report.append(
        _language_get("report_title_by_country", "REPORT: Satellites by Country")
    )
    report.append("=" * 60)
    report.append(
        f"\n{_language_get('report_col_country', 'Country'):<30} "
        f"{_language_get('report_col_count', 'Count'):<10} "
        f"{_language_get('report_col_percent', 'Percent (%)'):<10}"
    )
    report.append("-" * 50)

    for x, row in country_counts.iterrows():
        report.append(
            f"{row['country']:<30} {row['count']:<10} {row['percent']:<10.1f}"
        )

    report.append("-" * 50)
    report.append(
        f"{_language_get('report_total', 'TOTAL:'):<30} {total:<10} {100:<10.1f}"
    )
    report.append("=" * 60)

    return "\n".join(report)


def year_distribution_build(satellites):
    """
    Отчёт о распределении по годам запуска.
    Использует группировку pandas.

    Args:
        satellites (list): Список спутников

    Returns:
        str: Текст отчёта
    """
    if not satellites:
        return _language_get("report_no_data", "No satellite data available")

    df = _satellites_dataframe_get(satellites)

    if "launch_year" not in df.columns:
        return _language_get(
            "report_no_launch_year",
            "No launch year data available"
        )

    years_df = df[df["launch_year"].notna() & (df["launch_year"] > 1950)]

    if years_df.empty:
        return _language_get(
            "report_no_launch_year",
            "No launch year data available"
        )

    # Группировка по годам
    year_counts = years_df.groupby("launch_year").size().reset_index(name="count")
    year_counts = year_counts.sort_values("launch_year")

    report = []
    report.append("=" * 60)
    report.append(
        _language_get(
            "report_title_launch_years",
            "REPORT: Satellite Launch Year Distribution"
        )
    )
    report.append("=" * 60)
    report.append(
        f"\n{_language_get('report_year', 'Year'):<10} "
        f"{_language_get('report_col_count', 'Count'):<12} "
        f"{_language_get('report_visualization', 'Visualization')}"
    )
    report.append("-" * 60)

    max_count = year_counts["count"].max() if not year_counts.empty else 1

    # Построение текстовой гистограммы
    for i, row in year_counts.iterrows():
        year = int(row["launch_year"])
        count = row["count"]
        bar_length = int(40 * count / max_count) if max_count > 0 else 0
        points = "█" * bar_length
        report.append(f"{year:<10} {count:<12} {points}")

    report.append("-" * 60)
    report.append(
        f"Total satellites with launch year data: {len(years_df)}"
    )
    report.append(
        f"Period: {int(years_df['launch_year'].min())} - "
        f"{int(years_df['launch_year'].max())}"
    )
    report.append("=" * 60)

    return "\n".join(report)


# def table_pivot_build(satellites, index_col, columns_col, values_col, aggfunc="count"):
#     """
#     Сводная таблица для пары качественных атрибутов.
#     Использует pandas.pivot_table().

#     Args:
#         satellites (list): Список спутников
#         index_col (str): Столбец для индекса
#         columns_col (str): Столбец для колонок
#         values_col (str): Столбец для значений
#         aggfunc (str): Функция агрегации

#     Returns:
#         str: Текст отчёта
#     """
#     if not satellites:
#         return "No data available"

#     df = _satellites_dataframe_get(satellites)

#     if index_col not in df.columns or columns_col not in df.columns:
#         return f"Columns {index_col} or {columns_col} not found"

#     # Удаление NaN значений
#     if values_col in df.columns:
#         df_clean = df[[index_col, columns_col, values_col]].dropna()
#     else:
#         df_clean = df[[index_col, columns_col]].dropna()

#     if values_col in df.columns:
#         pivot = pd.pivot_table(
#             df_clean,
#             values=values_col,
#             index=index_col,
#             columns=columns_col,
#             aggfunc=aggfunc,
#             fill_value=0,
#         )
#     else:
#         # Если нет колонки значений, считаем количество
#         pivot = pd.pivot_table(
#             df_clean,
#             index=index_col,
#             columns=columns_col,
#             aggfunc="size",
#             fill_value=0,
#         )

#     report = []
#     report.append("=" * 60)
#     report.append(f"PIVOT TABLE: {index_col} vs {columns_col}")
#     report.append("=" * 60)
#     report.append("\n" + pivot.to_string())
#     report.append("=" * 60)

#     return "\n".join(report)
