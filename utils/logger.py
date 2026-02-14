import logging

# 1) Конфигурируем корневой логгер
logger = logging.getLogger()              # корневой логгер
logger.setLevel(logging.INFO)             # уровень логирования

# 2) Хэндлер для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_fmt = logging.Formatter(
    "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    "%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(console_fmt)
logger.addHandler(console_handler)

# 3) Хэндлер для записи в файл
file_handler = logging.FileHandler("bot.log", encoding="utf-8", mode="a")
file_handler.setLevel(logging.INFO)
file_fmt = logging.Formatter(
    "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    "%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(file_fmt)
logger.addHandler(file_handler)
