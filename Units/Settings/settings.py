"""Модуль для работы с настройками приложения"""

import json
import os


def config_save(config):
    """
    Сохранение конфигурации в файл.

    Args:
        config (dict): Конфигурация приложения

    Returns:
        bool: True при успешном сохранении
    """
    config_path = os.path.join("Config", "Config.json")

    try:
        # Создаём директорию Config, если она не существует
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except (OSError, PermissionError, TypeError) as e:
        print(f"Ошибка сохранения конфигурации: {e}")
        return False
