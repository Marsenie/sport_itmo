from config.settings_bd import bd_config

import random
import asyncpg
import asyncio
import logging
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

async def run_command(command : str, ans = False):
    # Подключение с параметрами
    conn = await asyncpg.connect(
        user=bd_config.DB_USER,
        password=bd_config.DB_PASSWORD,
        database=bd_config.DB_NAME,
        host=bd_config.DB_HOST,
        port=bd_config.DB_PORT)
        
    # Проверка подключения
    if ans:
        answer = await conn.fetch(command)
        await conn.close()
        return answer
    else:
        await conn.execute(command)
    await conn.close()

async def init_db():
    """Инициализировать таблицы в PostgreSQL"""
    # таблица с пользователями
    await run_command('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL UNIQUE,
                username VARCHAR(32) NOT NULL,
                email VARCHAR(254) NOT NULL,
                password VARCHAR(64) NOT NULL,
                isu INT NOT NULL,
                name VARCHAR(256) NOT NULL,
                login_error BOOLEAN,
                data TIMESTAMP NOT NULL DEFAULT now(),
                UNIQUE(user_id, email) ) ''')

    # Создаем индекс
    await run_command('CREATE INDEX IF NOT EXISTS idx_user_id ON users(user_id)')

    # таблица с днями
    await run_command('''CREATE TABLE IF NOT EXISTS days (
                    day_id SERIAL PRIMARY KEY,
                    name_day VARCHAR(16) NOT NULL UNIQUE)''')

    # таблица со временем
    await run_command('''CREATE TABLE IF NOT EXISTS time (
                    time_id SERIAL PRIMARY KEY,
                    name_time VARCHAR(8) NOT NULL UNIQUE)''')

    # таблица со местами
    await run_command('''CREATE TABLE IF NOT EXISTS locations (
                    location_id SERIAL PRIMARY KEY,
                    location_name VARCHAR(16) NOT NULL UNIQUE,
                    tag VARCHAR(16) NOT NULL)''')
    
    # таблица с секциями
    await run_command('''CREATE TABLE IF NOT EXISTS sections (
                    id SERIAL PRIMARY KEY,
                    section VARCHAR(256) NOT NULL,
                    coach VARCHAR(256) NOT NULL,
                    day_id INT NOT NULL REFERENCES days(day_id),
                    time_id INT NOT NULL REFERENCES time(time_id),
                    location_id INT NOT NULL REFERENCES locations(location_id),
                    is_parsing BOOLEAN NOT NULL,
                    UNIQUE(section, coach, day_id, time_id) ) ''')

    # таблица с записями
    await run_command('''CREATE TABLE IF NOT EXISTS records (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    section_id INT NOT NULL REFERENCES sections(id),
                    period INT NOT NULL)''')

     # таблица с видами банов
    await run_command('''CREATE TABLE IF NOT EXISTS reasons (
                    reason_id SERIAL PRIMARY KEY,
                    reason_name VARCHAR(128),
                    description VARCHAR(4096),
                    time_ban INT NOT NULL)''')
    
    # таблица с банами
    await run_command('''CREATE TABLE IF NOT EXISTS bans (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id),
                    reason_id BIGINT NOT NULL REFERENCES reasons(reason_id),
                    msg VARCHAR(4096) NOT NULL,
                    data TIMESTAMP NOT NULL DEFAULT now(),
                    valid BOOLEAN NOT NULL DEFAULT False)''')

    # таблица с админами
    await run_command('''CREATE TABLE IF NOT EXISTS admins (
                    id SERIAL PRIMARY KEY,
                    admin_id BIGINT NOT NULL UNIQUE,
                    username VARCHAR(32) NOT NULL,
                    email VARCHAR(254) NOT NULL UNIQUE,
                    name VARCHAR(256) NOT NULL,
                    data TIMESTAMP NOT NULL DEFAULT now())''')
    
    # таблица со статусами
    await run_command('''CREATE TABLE IF NOT EXISTS ticket_statuses (
                    status_id  SERIAL PRIMARY KEY,
                    status_name VARCHAR(128),
                    description VARCHAR(4096))''')
    
    # таблица с тикетами
    await run_command('''CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id SERIAL PRIMARY KEY,
                    admin_id BIGINT REFERENCES admins(admin_id),
                    user_id BIGINT NOT NULL REFERENCES users(user_id),
                    topic VARCHAR(64) NOT NULL,
                    status_id BIGINT NOT NULL REFERENCES ticket_statuses(status_id),
                    feedback_score INT,
                    feedback VARCHAR(4096),
                    data TIMESTAMP NOT NULL DEFAULT now())''')
    
    # таблица с сообщениями 
    await run_command('''CREATE TABLE IF NOT EXISTS ticket_msg (
                    id SERIAL PRIMARY KEY,
                    ticket_id BIGINT NOT NULL REFERENCES tickets(ticket_id),
                    msg VARCHAR(4096) NOT NULL,
                    is_send BOOLEAN NOT NULL DEFAULT False,
                    is_from_admin BOOLEAN NOT NULL,
                    data TIMESTAMP NOT NULL DEFAULT now())''')

    # Вставляем дни
    ans = await run_command("SELECT COUNT(*) FROM days", ans = True)
    if ans[0]['count'] == 0:
        await run_command('''INSERT INTO days (day_id, name_day) VALUES
                            (1, 'Понедельник'),
                            (2, 'Вторник'),
                            (3, 'Среда'),
                            (4, 'Четверг'),
                            (5, 'Пятница'),
                            (6, 'Суббота'),
                            (7, 'Воскресенье')''')
    # Вставляем время
    ans = await run_command("SELECT COUNT(*) FROM time", ans = True)
    if ans[0]['count'] == 0:
        await run_command('''INSERT INTO time (time_id, name_time) VALUES
                            (1, '8-9'),
                            (2, '9-11'),
                            (3, '11-13'),
                            (4, '13-15'),
                            (5, '15-17'),
                            (6, '17-19'),
                            (7, '19-21'),
                            (8, '21-23')''')

    # Вставляем места
    ans = await run_command("SELECT COUNT(*) FROM locations", ans = True)
    if ans[0]['count'] == 0:
        await run_command('''INSERT INTO locations (location_id, location_name, tag) VALUES
                            (1, 'онлайн', 'null-0'),
                            (2, 'Ломо', 'null-1'),
                            (3, 'Вяземский', 'null-2'),
                            (4, 'Другие', 'null-3')''')
    
    # Вставляем виды банов
    ans = await run_command("SELECT COUNT(*) FROM reasons", ans = True)
    if ans[0]['count'] == 0:
        await run_command('''INSERT INTO reasons (reason_id, reason_name, description, time_ban) VALUES
                            (1, 'Спам', 'Отправка большого количества сообщений', 30),
                            (2, 'Спам', 'Многократная отправка большого количества сообщений', 31536000),
                            (3, 'SQL-инъекция', 'Отправка сообщения c sql командой, выдаётся автоматически', 172800),
                            (4, 'SQL-инъекция', 'Выдаётся в ручную', 31536000)''')

    # Вставляем статусы
    ans = await run_command("SELECT COUNT(*) FROM ticket_statuses", ans = True)
    if ans[0]['count'] == 0:
        await run_command('''INSERT INTO ticket_statuses (status_id, status_name, description) VALUES
                            (1, 'Отправлено', 'Пользователь отправил обращение, пока никто из администраторов не взял тикет в работу'),
                            (2, 'В работе', 'Администратор взял на себя тиктет, и отвечает на сообщение.'),
                            (3, 'Закрыто', 'Обращение пользователя обработано'),
                            (4, 'Возобновлено', 'Пользователь возобновил обращение'),
                            (5, 'Закрыто', 'Закрыто после возобновления'),
                            (6, 'Закрыто окончательно', 'Закрыто без права пользователя на возобновлие тикета')''')
    
    logger.info("PostgreSQL база данных инициализирована")


async def get_command(command: str):
    try:
        rows = await run_command(command, ans = True)
        return [dict(row) for row in rows]
                
    except Exception as e:
        logger.error(f"Команда: {command}\nОшибка при получении данных: {e}")
        return []
    
async def add_command(command: str):
    try:
        await run_command(command)
        return True
      
    except Exception as e:
        logger.error(f"Команда: {command}\nОшибка при получении данных: {e}")
        return False

async def del_command(command: str):
    try:
        await run_command(command)
        return True
      
    except Exception as e:
        logger.error(f"Команда: {command}\nОшибка при удалении данных: {e}")
        return False


# таблица USERS
async def add_user_data(user_id: int, email: str, password: str, username: str, isu: int, name: str) -> bool:
    """Добавить данные пользователя"""
    return await add_command(f"INSERT INTO users (user_id, email, password, username, isu, name, login_error) VALUES ({user_id}, '{email}', '{password}', '{username}', {isu}, '{name}', False)")

async def login_error(user_id: int):
    try:
        await run_command(f"UPDATE users SET login_error = True WHERE user_id = {user_id}")
    except:
        logger.error(f"Ошибка пометки ошибки входа: {user_id}")

async def reset_login_error(user_id: int):
    try:
        await run_command(f"UPDATE users SET login_error = False WHERE user_id = {user_id}")
    except:
        logger.error(f"Ошибка сброса ошибки входа: {user_id}")

async def get_for_records_user_data(period: int, day_id: int):
    """Получить все данные пользователя"""
    return await get_command(f'SELECT * FROM records r JOIN sections s ON s.id = r.section_id WHERE (period in (2, {period})) and (day_id = {day_id});')

async def get_user_data(user_id: int):
    """Получить все данные пользователя"""
    data = await get_command(f'SELECT * FROM users WHERE user_id = {user_id}')
    if data ==  []:
        return []
    return data[0]

async def get_random_user_data():
    """Получить все данные пользователя"""
    data = await get_command(f'SELECT * FROM users where login_error = false')
    return data[random.randint(0, (len(data) - 1))]


async def del_user_data(user_id: int):
    """Удалить все данные пользователя"""
    return await del_command(f'DELETE FROM users WHERE user_id = {user_id}')


# таблица RECORDS
async def add_record_data(user_id: int, section_id: str, period: int):
    """Добавить данные пользователя"""
    return await add_command(f"INSERT INTO records (user_id, section_id, period) VALUES ({user_id}, {section_id}, {period})")

async def get_record_data(user_id: int):
    """Добавить данные пользователя"""
    return await get_command(f"SELECT section_id, period from records WHERE user_id={user_id}")

async def get_record_section_data(user_id: int):
    """Добавить данные пользователя"""
    return await get_command(f"""SELECT r.section_id, s.section, d.name_day, t.name_time FROM records r
                             JOIN sections s ON r.section_id = s.id
                             JOIN days d ON s.day_id = d.day_id
                             JOIN time t ON s.time_id = t.time_id
                             WHERE user_id={user_id}""")

async def del_all_user_record(user_id: int):
    """Добавить данные пользователя"""
    return await del_command(f"DELETE FROM records WHERE (user_id = {user_id})")

async def del_user_record(user_id: int, section_id: int):
    """Добавить данные пользователя"""
    return await del_command(f"DELETE FROM records WHERE (user_id = {user_id}) and (section_id = {section_id})")


# таблица SECTIONS
async def add_section_data(section: str, coach: str, day_id: int, time_id: int, location_id:int, is_parsing: bool = False):
    """Добавить данные пользователя"""
    return await add_command(f"INSERT INTO sections (section, coach, day_id, time_id, location_id, is_parsing) VALUES ('{section}', '{coach}', {day_id}, {time_id}, {location_id}, {is_parsing})")

async def add_get_section_data_return_id(section: str, coach: str, day_id: int, time_id: int, location_id:int, is_parsing: bool = False):
    """Добавить данные пользователя"""
    return await get_command(f"INSERT INTO sections (section, coach, day_id, time_id, location_id, is_parsing) VALUES ('{section}', '{coach}', {day_id}, {time_id}, {location_id}, {is_parsing}) RETURNING id")

async def get_section_data(day_id: int, time_id: int, location_id:int):
    """Добавить данные пользователя"""
    return await get_command(f"SELECT * FROM sections WHERE (day_id = {day_id}) and (time_id = {time_id}) and (location_id = {location_id}) and (is_parsing = True)")

async def get_section(section: str, coach: str, day_id: int, time_id: int, location_id:int):
    """Добавить данные пользователя"""
    return await get_command(f"SELECT * FROM sections WHERE (day_id = {day_id}) and (time_id = {time_id}) and (location_id = {location_id}) and (section = 'section') and (coach = 'coach')")

async def del_all_section_data() -> bool:
    """Удалить данные о секциях"""
    return await del_command(f"DELETE FROM records; DELETE FROM sections")


# таблица BANS
async def add_ban_user(user_id: int, msg: str, reason_id: int):
    """Добавить данные пользователя"""
    return await get_command(f"INSERT INTO bans (user_id, msg, reason_id) VALUES ('{user_id}', '{msg}', {reason_id})")

async def get_ban_user(reason_id: int):
    """Добавить данные пользователя"""
    return await get_command(f"SELECT * FROM bans WHERE (reason_id = {reason_id}) and (valid = False)")


# таблица TICKETS
async def get_id_add_ticket(user_id: int, topic: str):
    """Добавить данные пользователя"""
    return await get_command(f"INSERT INTO tickets (user_id, topic, status_id) VALUES ({user_id}, '{topic}', 1) RETURNING ticket_id")

async def update_status_ticket(ticket_id: int, status_id: int):
    """Добавить данные пользователя"""
    return await add_command(f"UPDATE tickets SET status_id = {status_id} WHERE ticket_id = {ticket_id}")

async def update_feedback_score_ticket(ticket_id: int, feedback_score: int):
    """Добавить данные пользователя"""
    return await add_command(f"UPDATE tickets SET feedback_score = {feedback_score} WHERE ticket_id = {ticket_id}")

async def update_feedback_ticket(ticket_id: int, feedback: str):
    """Добавить данные пользователя"""
    return await add_command(f"UPDATE tickets SET feedback = '{feedback}' WHERE ticket_id = {ticket_id}")

async def get_user_ticket(user_id: int):
    """Добавить данные пользователя"""
    return await get_command(f"SELECT ticket_id, topic, status_id FROM tickets WHERE user_id = {user_id} and (status_id in (1, 2, 4))")

async def update_tickets_issue_admin(admin_id: int, lim: int = 10):
    """Добавить данные пользователя"""
    return await add_command(f"UPDATE tickets set status_id = 2, admin_id = {admin_id} WHERE status_id = 1 ORDER BY data LIMIT {lim}")

async def get_admin_tickets(admin_id: int, lim: int = 15):
    """Добавить данные пользователя"""
    return await get_command(f"SELECT * FROM tickets (status_id in (2, 4)) and (admin_id = {admin_id}) ORDER BY data LIMIT {lim}")


# таблица TICKET_MSG
async def add_ticket_msg(ticket_id: int, msg: str, is_from_admin: bool):
    """Добавить данные пользователя"""
    return await add_command(f"INSERT INTO ticket_msg (ticket_id, msg, is_from_admin) VALUES ({ticket_id}, '{msg}',{is_from_admin})")

async def get_ticket_msg(ticket_id: int):
    """Добавить данные пользователя"""
    return await get_command(f"SELECT msg, is_from_admin FROM ticket_msg WHERE ticket_id = {ticket_id} ORDER BY id")

async def get_not_send_ticket_msg():
    """Добавить данные пользователя"""
    return await get_command(f"SELECT * FROM ticket_msg WHERE is_send = False")

async def update_is_seng_ticket_msg(ticket_id: int):
    """Добавить данные пользователя"""
    return await add_command(f"UPDATE ticket_msg SET is_seng = True WHERE ticket_id = {ticket_id}")


