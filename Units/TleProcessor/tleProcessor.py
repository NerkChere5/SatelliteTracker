"""Модуль для обработки TLE данных и вычисления координат спутников"""

from datetime import datetime, timedelta
import math

from Units.Common import common

_earth_mu = 398600.4418
_earth_radius = 6371.0
_earth_rotation_rate = 7.292115e-5



def _days_since_epoch_get(tle_epoch_str, target_time):
    """
    Вычисление количества дней между эпохой TLE и целевым временем.

    Формат эпохи TLE: YYDDD.FFFFFFFF
    где YY - год, DDD - день года, FFFFFF - дробная часть дня

    Args:
        tle_epoch_str (str): Строка эпохи в формате YYDDD.FFFFFFFF
        target_time (datetime): Целевое время

    Returns:
        float: Количество дней
    """
    if not tle_epoch_str or len(tle_epoch_str) < 10:
        return 0

    try:
        # Парсинг TLE (формат: YYDDD.FFFFFFFF)
        year = int(tle_epoch_str[0:2])
        # Определение века: года 57-99 относятся к 1900м, 00-56 к 2000м
        year += 2000 if year < 57 else 1900

        day_of_year = float(tle_epoch_str[2:11])
        days = int(day_of_year)
        fractional_day = day_of_year - days

        # Создание даты
        epoch_date = datetime(year, 1, 1) + timedelta(days=days - 1)
        epoch_date = epoch_date.replace(hour=int(fractional_day * 24))
        fractional_day -= int(fractional_day * 24) / 24
        epoch_date = epoch_date.replace(minute=int(fractional_day * 1440))
        fractional_day -= int(fractional_day * 1440) / 1440
        epoch_date = epoch_date.replace(second=int(fractional_day * 86400))

        # Разница в днях
        delta = (target_time - epoch_date).total_seconds() / 86400.0
        return delta
    except (ValueError, TypeError, OverflowError) as e:
        print(f"Error parsing epoch: {e}")
        return 0


def _earth_mu_get():
    """Возвращает гравитационный параметр Земли."""
    return _earth_mu


def _earth_radius_get():
    """Возвращает средний радиус Земли."""
    return _earth_radius


def _earth_velocity_rotation_get():
    """Возвращает скорость вращения Земли."""
    return _earth_rotation_rate


def _position_instant_get(tle_params, target_time):
    """
    Вычисление моментальной позиции спутника в заданное время.

    Алгоритм:
    1. Вычисление текущей средней аномалии с учётом прошедшего времени
    2. Решение уравнения Кеплера для нахождения эксцентрической аномалии
    3. Вычисление истинной аномалии и радиуса-вектора
    4. Преобразование из орбитальной системы координат в экваториальную
    5. Учёт вращения Земли для получения долготы

    Args:
        tle_params (dict): Орбитальные параметры из TLE
        target_time (datetime): Целевое время (UTC)

    Returns:
        dict: Координаты (x, y, z) в км и широта/долгота в градусах
    """
    if not tle_params:
        return None

    # Извлечение параметров орбиты
    mean_motion = tle_params.get("mean_motion", 15.0)      # Среднее движение (оборотов/день)
    mean_anomaly_deg = tle_params.get("mean_anomaly", 0.0) # Средняя аномалия в эпоху (градусы)
    eccentricity = tle_params.get("eccentricity", 0.0)     # Эксцентриситет
    inclination_deg = tle_params.get("inclination", 0.0)   # Наклонение (градусы)
    raan_deg = tle_params.get("raan", 0.0)                 # Долгота восходящего узла (градусы)
    arg_perigee_deg = tle_params.get("arg_perigee", 0.0)   # Аргумент перигея (градусы)

    # Расчёт времени, прошедшего с эпохи TLE
    tle_epoch = tle_params.get("epoch", "")
    days_since_epoch = _days_since_epoch_get(tle_epoch, target_time)

    # Угловая скорость (градусов в день)
    angular_velocity_deg_per_day = mean_motion * 360

    # Текущая средняя аномалия (градусы)
    current_mean_anomaly_deg = mean_anomaly_deg + angular_velocity_deg_per_day * days_since_epoch
    current_mean_anomaly_deg = current_mean_anomaly_deg % 360

    # Преобразование в радианы
    current_mean_anomaly_rad = math.radians(current_mean_anomaly_deg)
    inclination_rad = math.radians(inclination_deg)
    raan_rad = math.radians(raan_deg)
    arg_perigee_rad = math.radians(arg_perigee_deg)

    # Решение уравнения Кеплера для эксцентрической аномалии
    # E = M + e * sin(E) - итерационное решение
    if eccentricity < 0.001:
        eccentric_anomaly_rad = current_mean_anomaly_rad
    else:
        eccentric_anomaly_rad = current_mean_anomaly_rad
        for x in range(10):
            eccentric_anomaly_rad = eccentricity * math.sin(eccentric_anomaly_rad)
            eccentric_anomaly_rad += current_mean_anomaly_rad

    # Истинная аномалия (угол от перицентра до спутника)
    cos_nu = (
        (math.cos(eccentric_anomaly_rad) - eccentricity)
        / (1 - eccentricity * math.cos(eccentric_anomaly_rad))
    )
    sin_nu = (
        (math.sqrt(1 - eccentricity ** 2)
        * math.sin(eccentric_anomaly_rad))
        / (1 - eccentricity * math.cos(eccentric_anomaly_rad))
    )
    true_anomaly_rad = math.atan2(sin_nu, cos_nu)

    # Радиус-вектор в орбитальной плоскости
    a = tle_params.get("semi_major_axis", _earth_radius_get() + 500)
    r = a * (1 - eccentricity * math.cos(eccentric_anomaly_rad))

    # Координаты в орбитальной плоскости (система координат перицентра)
    x_orbit = r * math.cos(true_anomaly_rad)
    y_orbit = r * math.sin(true_anomaly_rad)

    # Преобразование в экваториальные координаты (поворот на аргумент перигея)
    cos_omega = math.cos(arg_perigee_rad)
    sin_omega = math.sin(arg_perigee_rad)
    x1 = x_orbit * cos_omega - y_orbit * sin_omega
    y1 = x_orbit * sin_omega + y_orbit * cos_omega

    # Поворот на наклонение (вокруг оси X)
    cos_i = math.cos(inclination_rad)
    sin_i = math.sin(inclination_rad)
    x2 = x1
    y2 = y1 * cos_i
    z2 = y1 * sin_i

    # Поворот на восходящий узел (вокруг оси Z)
    cos_raan = math.cos(raan_rad)
    sin_raan = math.sin(raan_rad)
    x_eq = x2 * cos_raan - y2 * sin_raan
    y_eq = x2 * sin_raan + y2 * cos_raan
    z_eq = z2

    # Учёт вращения Земли для долготы
    seconds_since_epoch = days_since_epoch * 86400
    rotation_angle = _earth_velocity_rotation_get() * seconds_since_epoch

    # Вычисление географических координат
    r_total = math.sqrt(x_eq**2 + y_eq**2 + z_eq**2)
    latitude = math.degrees(math.asin(z_eq / r_total)) if r_total > 0 else 0

    raw_longitude = math.degrees(math.atan2(y_eq, x_eq))
    longitude = raw_longitude - math.degrees(rotation_angle)

    # Нормализация долготы к диапазону [-180, 180]
    while longitude > 180:
        longitude -= 360
    while longitude < -180:
        longitude += 360

    return {
        "x": x_eq,
        "y": y_eq,
        "z": z_eq,
        "latitude": latitude,
        "longitude": longitude,
        "altitude": r_total - _earth_radius_get(),
        "radius": r_total,
        "days_since_epoch": days_since_epoch,
        "current_mean_anomaly": current_mean_anomaly_deg,
    }


def _tle_parse(tle_line1, tle_line2):
    """
    Парсинг TLE строк и извлечение орбитальных параметров.

    TLE (Two-Line Element) - стандартный формат описания орбит спутников.
    Каждая строка имеет строго определённую структуру символов.

    Args:
        tle_line1 (str): Первая строка TLE
        tle_line2 (str): Вторая строка TLE

    Returns:
        dict: Орбитальные параметры
    """
    if not tle_line1 or not tle_line2:
        return None

    params = {}

    # Парсинг первой строки TLE (NORAD ID, эпоха)
    # Формат: строка из 69 символов, NORAD ID на позициях 2-7
    if len(tle_line1) >= 68:
        try:
            params["norad_id"] = int(tle_line1[2:7].strip())
            # Эпоха (первые две цифры года и день года) на позициях 18-32
            epoch_str = tle_line1[18:32].strip()
            if epoch_str:
                params["epoch"] = epoch_str
        except (ValueError, IndexError) as e:
            print(f"Error parsing TLE line 1: {e}")

    # Парсинг второй строки TLE
    # Формат: наклонение (8-16), восходящий узел (17-25),
    # эксцентриситет (26-33), аргумент перигея (34-42),
    # средняя аномалия (43-51), среднее движение (52-63)
    if len(tle_line2) >= 68:
        try:
            params["inclination"] = float(tle_line2[8:16].strip()) if len(tle_line2) >= 16 else 0
            params["raan"] = float(tle_line2[17:25].strip()) if len(tle_line2) >= 25 else 0
            eccentricity_str = "0." + tle_line2[26:33].strip() if len(tle_line2) >= 33 else "0.0"
            params["eccentricity"] = float(eccentricity_str)
            params["arg_perigee"] = float(tle_line2[34:42].strip()) if len(tle_line2) >= 42 else 0
            params["mean_anomaly"] = float(tle_line2[43:51].strip()) if len(tle_line2) >= 51 else 0
            params["mean_motion"] = float(tle_line2[52:63].strip()) if len(tle_line2) >= 63 else 0
        except (ValueError, IndexError) as e:
            print(f"Error parsing TLE line 2: {e}")
            return None

    # Вычисление большой полуоси (км) по третьему закону Кеплера
    # n = mean_motion (оборотов в день) -> угловая скорость в рад/с
    if "mean_motion" in params and params["mean_motion"] > 0:
        try:
            params["semi_major_axis"] = (
                (_earth_mu_get() / (params["mean_motion"] * 2 * math.pi / 86400) ** 2) ** (1/3)
            )
        except (ValueError, ZeroDivisionError) as e:
            print(f"Error calculating semi-major axis: {e}")
            params["semi_major_axis"] = _earth_radius_get() + 500
    else:
        params["semi_major_axis"] = _earth_radius_get() + 500

    # Вычисление периода в минутах
    if "mean_motion" in params and params["mean_motion"] > 0:
        params["period_minutes"] = 1440 / params["mean_motion"]

    # Высота (км) - приблизительная (большая полуось минус радиус Земли)
    params["altitude"] = params["semi_major_axis"] - _earth_radius_get()

    return params


def consts_load():
    """
    Загрузка констант Земли из конфигурационного файла.
    """
    global _earth_mu, _earth_radius, _earth_rotation_rate
    constants = common.consts_import()
    _earth_mu = constants["earth_mu"]
    _earth_radius = constants["earth_radius"]
    _earth_rotation_rate = constants["earth_rotation_rate"]


def position_get(satellite, target_time):
    """
    Получение позиции спутника на заданное время.

    Args:
        satellite (dict): Данные спутника с TLE
        target_time (datetime): Целевое время

    Returns:
        dict: Координаты спутника
    """
    tle_line1 = satellite.get("tle_line1", "")
    tle_line2 = satellite.get("tle_line2", "")

    if not tle_line1 or not tle_line2:
        return None

    tle_params = _tle_parse(tle_line1, tle_line2)
    if not tle_params:
        return None

    position = _position_instant_get(tle_params, target_time)

    if position:
        position["satellite_name"] = satellite.get("name", "Unknown")
        position["norad_id"] = satellite.get("norad_id", "Unknown")

    return position


def trajectory_get(satellite, start_time, end_time, num_points=100):
    """
    Вычисление наземной траектории спутника.

    Args:
        satellite (dict): Данные спутника
        start_time (datetime): Начальное время
        end_time (datetime): Конечное время
        num_points (int): Количество точек

    Returns:
        list: Список координат (долгота, широта)
    """
    if not satellite:
        return []

    positions = []
    total_seconds = (end_time - start_time).total_seconds()

    # Равномерное распределение точек по времени
    for i in range(num_points):
        t = start_time + timedelta(seconds=total_seconds * i / (num_points - 1))
        pos = position_get(satellite, t)
        if pos:
            positions.append((pos["longitude"], pos["latitude"]))

    return positions
