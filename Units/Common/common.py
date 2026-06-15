"""Универсальные функции"""

from datetime import datetime
import json
import os
import pickle

import numpy as np
import pandas as pd


def _directory_create(directory):
    """Создание директории если она не существует"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        return True
    return False


def _file_is_exists(filepath):
    """Проверка существования файла"""
    return os.path.exists(filepath)


def _json_import(filepath):
    """Загрузка данных из JSON файла"""
    try:
        if _file_is_exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
    except (json.JSONDecodeError, UnicodeDecodeError, FileNotFoundError) as e:
        print(f"Ошибка загрузки JSON: {e}")
        return None


def binary_export(data, filepath):
    """Сохранение данных в бинарный файл (pickle)."""
    try:
        _directory_create(os.path.dirname(filepath))
        with open(filepath, "wb") as f:
            pickle.dump(data, f)
        return True
    except (pickle.PickleError, OSError, TypeError) as e:
        print(f"Ошибка сохранения pickle: {e}")
        return False


def binary_import(filepath):
    """Загрузка данных из бинарного файла (pickle)."""
    try:
        if _file_is_exists(filepath):
            with open(filepath, "rb") as f:
                return pickle.load(f)
        return None
    except (pickle.PickleError, EOFError, FileNotFoundError, OSError) as e:
        print(f"Ошибка загрузки pickle: {e}")
        return None


def consts_import(config_path="Config/Config.json"):
    """
    Загрузка констант Земли из конфигурационного файла.

    Args:
        config_path (str): Путь к файлу конфигурации

    Returns:
        dict: Словарь с константами Земли
    """
    try:
        config = _json_import(config_path)
        if config is None:
            config = {}
        return {
            "earth_mu": config.get("earth_mu", 398600.4418),
            "earth_radius": config.get("earth_radius", 6371.0),
            "earth_rotation_rate": config.get("earth_rotation_rate", 7.292115e-5),
        }
    except (TypeError, AttributeError) as e:
        print(f"Ошибка загрузки констант: {e}")
        return {
            "earth_mu": 398600.4418,
            "earth_radius": 6371.0,
            "earth_rotation_rate": 7.292115e-5,
        }


def csv_export(data, filepath):
    """
    Сохранение данных в CSV файл с помощью pandas.

    Args:
        data (list or pd.DataFrame): Данные для сохранения
        filepath (str): Путь к файлу

    Returns:
        bool: True при успешном сохранении
    """
    try:
        _directory_create(os.path.dirname(filepath))

        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            return False

        df.to_csv(filepath, index=False, encoding="utf-8")
        return True
    except (OSError, PermissionError, ValueError, TypeError) as e:
        print(f"Ошибка сохранения CSV: {e}")
        return False


def csv_import(filepath):
    """
    Загрузка данных из CSV файла с помощью pandas.

    Args:
        filepath (str): Путь к файлу

    Returns:
        pd.DataFrame: DataFrame с данными или None при ошибке
    """
    try:
        if _file_is_exists(filepath):
            df = pd.read_csv(filepath, encoding="utf-8")
            df = df.replace({np.nan: None})
            return df
        return None
    except (FileNotFoundError, UnicodeDecodeError, pd.errors.EmptyDataError,
            pd.errors.ParserError) as e:
        print(f"Ошибка загрузки CSV: {e}")
        return None


def dataframe_transform(df):
    """
    Преобразование DataFrame в список словарей.

    Args:
        df (pd.DataFrame): DataFrame

    Returns:
        list: Список словарей
    """
    if df is None or df.empty:
        return []
    try:
        return df.to_dict(orient="records")
    except (AttributeError, TypeError) as e:
        print(f"Ошибка преобразования DataFrame: {e}")
        return []


def list_transform(data_list):
    """
    Преобразование списка словарей в DataFrame.

    Args:
        data_list (list): Список словарей

    Returns:
        pd.DataFrame: DataFrame
    """
    if not data_list:
        return pd.DataFrame()
    try:
        return pd.DataFrame(data_list)
    except (ValueError, TypeError) as e:
        print(f"Ошибка преобразования списка: {e}")
        return pd.DataFrame()


def timestamp_get():
    """Получение временной метки."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
