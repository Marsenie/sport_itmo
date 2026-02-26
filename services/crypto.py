from config.settings_crypto import crypto_config
from cryptography.fernet import Fernet
import base64
import hashlib

# Функция для генерации ключа из парольной фразы (если вы не хотите хранить сырой ключ)
def get_cipher():
    key_string = crypto_config.PARSER_MASTER_KEY
    if not key_string:
        # На локальной машине для теста можно сгенерировать, но в проде это фатальная ошибка
        raise Exception("PARSER_MASTER_KEY not set in environment variables")
    
    # Убеждаемся, что ключ в байтах
    key = key_string.encode() if isinstance(key_string, str) else key_string
    return Fernet(key)

def encrypt_password(password: str) -> str:
    """Принимает строку пароля, возвращает зашифрованную строку для БД"""
    cipher = get_cipher()
    encrypted = cipher.encrypt(password.encode())
    return encrypted.decode() # Возвращаем как строку для хранения в TEXT поле

def decrypt_password(encrypted_password: str) -> str:
    """Принимает строку из БД, возвращает оригинальный пароль"""
    cipher = get_cipher()
    decrypted = cipher.decrypt(encrypted_password.encode())
    return decrypted.decode()

