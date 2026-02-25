from config.settings_bd import bd_config

import os

def create_backup():
    # Формируем команду
    command = f'pg_dump --dbname=postgresql://{bd_config.DB_USER}:{bd_config.DB_PASSWORD}@{bd_config.DB_HOST}:{bd_config.DB_PORT}/{bd_config.DB_NAME} > {bd_config.BACKUP_PATH}'
    os.system(command)

