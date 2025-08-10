# lib/logger/config.py

import logging.config
import os

# Определяем базовый уровень логирования из переменной окружения, по умолчанию INFO
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Конфигурация в виде словаря
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False, # Не отключаем логгеры библиотек
    
    # Форматтеры определяют, как будет выглядеть итоговая строка лога
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    
    # Обработчики определяют, куда будут отправляться логи (в консоль, файл и т.д.)
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default", # Используем форматтер 'default'
            "stream": "ext://sys.stdout", # Вывод в стандартный поток вывода
        },
    },
    
    # Логгеры - это "входные точки" в систему логирования
    "loggers": {
        # Корневой логгер, который ловит все сообщения
        "": {
            "handlers": ["console"], # Направляем всё в 'console'
            "level": LOG_LEVEL,
        },
        # Отдельно настраиваем логгеры uvicorn, чтобы они соответствовали нашему формату
        "uvicorn.error": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False, # Не передавать сообщения корневому логгеру
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


def setup_logging():
    """Применяет конфигурацию логирования из словаря."""
    logging.config.dictConfig(LOGGING_CONFIG)
    logging.info("Logging configured successfully.")
