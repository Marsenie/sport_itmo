import re
from typing import Union

async def validate(input_data: Union[str, int, float], max_length: int = 255) -> bool:
    """
    Продвинутая валидация входных данных для защиты от SQL-инъекций
    
    Args:
        input_data: Входные данные для проверки
        max_length: Максимальная допустимая длина строки
    
    Returns:
        bool: True если данные безопасны, False если опасны
    """
    
    # Если входные данные не строка, конвертируем в строку
    if not isinstance(input_data, str):
        input_data = str(input_data)
    
    # Проверка длины
    if len(input_data) > max_length:
        return False
    
    # Опасные SQL конструкции
    sql_keywords = [
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'UNION', 'JOIN', 'WHERE', 'FROM', 'TABLE', 'DATABASE', 'SCHEMA',
        'EXEC', 'EXECUTE', 'TRUNCATE', 'MERGE', 'OUTPUT', 'INTO'
    ]
    
    # Опасные символы и конструкции
    dangerous_patterns = [
        r'--', r'#', r'/\*', r'\*/',  # комментарии
        r';', r'\|\|', r'&&',  # разделители команд
        r'(\bOR\b|\bAND\b)\s+[\w\s]*=',  # OR/AND с условиями
        r'XP_', r'SP_',  # расширенные процедуры
        r'WAITFOR\s+DELAY',  # временные задержки
        r'CHAR\s*\(',  # CHAR функции
        r'BENCHMARK\s*\(',  # бенчмарк функции
        r'SLEEP\s*\(',  # функции сна
    ]
    
    input_upper = input_data.upper()
    
    # Проверка ключевых слов
    for keyword in sql_keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', input_upper):
            return False
    
    # Проверка опасных паттернов
    for pattern in dangerous_patterns:
        if re.search(pattern, input_data, re.IGNORECASE):
            return False
    
    # Проверка на множественные кавычки (может указывать на инъекцию)
    if input_data.count("'") > 5 or input_data.count('"') > 5:
        return False
    
    return True


