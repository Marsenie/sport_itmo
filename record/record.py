from record.week.week import get_this_week_num
from services.postgre_db import add_section_data, get_random_user_data, get_for_records_user_data, get_user_data, login_error, del_user_record, add_section_data_by_df
from services.buckup_db import create_backup
from alerts.alerts import *
from services.crypto import decrypt_password

import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import time
import datetime

place = {
    #"1": "null-0",#онлайн
    "2": "null-1", #Ломо
    "3": "null-2",#Вяземский
    #"4": "null-3",#Другие
}

def create_df():
 return pd.DataFrame(columns=["Название", "Преподаватель", "День", "Время", "location", "id"])
    
async def create_browser():
    """Создание браузера и контекста"""
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    return playwright, browser, context, page

async def close_browser(playwright, browser):
    """Закрытие браузера"""
    await browser.close()
    await playwright.stop()

async def open_site(page, url):
    """Открытие сайта"""
    await page.goto(url)
    await page.wait_for_load_state('networkidle')

async def login(page, email, password):
    """Авторизация"""
    password = decrypt_password(password)
    await page.fill("#username", email)
    await page.fill("#password", password)
    await page.click("#kc-login")
    await asyncio.sleep(1)
    #await page.wait_for_load_state('networkidle')

async def exit_account(page):
    """Выход из аккауета"""
    await page.click(".nav-link.dropdown-toggle")
    await page.click(".bi-logout.dd-icon.b-icon.bi.text-danger")
    
async def flipping_through(page, direction="forward", times=2):
    """Перелистывание страниц"""
    if direction == "forward":
        selector = '.uil.uil-angle-right-b'
    else:
        selector = '.uil.uil-angle-left-b'
    
    for _ in range(times):
        await page.click(selector)

async def choose_a_location(page, location):
    """Выбор локации"""
    await page.click(".multiselect__tags")
    await page.click(f"#{place[location]}")

async def get_data_from_page(page, df, location: str):
    """Парсинг данных"""
    # Получаем все элементы расписания
    items = await page.query_selector_all('.el-calendar-row')
    for time in range(1, len(items)):  # время       
        items_in_str = await items[time].query_selector_all('.el-calendar-cell-content')
        for day in range(len(items_in_str)):  # день
            items_in_cell = await items_in_str[day].query_selector_all('.section-block')
            for item in items_in_cell: # ячейка
                selectors = ['sport-item cant-sign', '.sport-item']
                for selector in selectors:
                    try:
                        sport_item = await item.query_selector(selector)
                        style = await sport_item.get_attribute('style')
                        if style == 'border-color: rgb(91, 198, 33);':
                            # Получаем название секции
                            name_element = await item.query_selector('.d-flex.justify-content-between.align-items-center')
                            name_sports_section = await name_element.inner_text() if name_element else ""
                            name_sports_section = name_sports_section.strip()
                            # Получаем имя тренера
                            coach_element = await item.query_selector('.text-sm.text-gray-80')
                            coach = await coach_element.inner_text() if coach_element else ""
                            coach = coach.strip()
                            # Получаем ID
                            identifier = await item.get_attribute('id') or ""
                            df.loc[len(df)] = {"Название": name_sports_section, "Преподаватель": coach, "День": day, "Время": time, "location": location, "id": identifier}
                    except:
                        pass
    
    return df

async def start_parsing(email, password, last_week=False):
    playwright, browser, context, page = await create_browser()
    try:
        await open_site(page, "https://my.itmo.ru/sport/sign")
        await login(page, email, password)
        df = create_df()
        for location in place:
            await choose_a_location(page, location)
            await flipping_through(page, times = 2)
            for _ in range(2):
                df = pd.concat([df, await get_data_from_page(page, create_df(), location)], ignore_index=True)
                # Пролистываем неделю
                await flipping_through(page, times = 1, direction="back")
                if last_week:
                    await flipping_through(page, times = 1, direction="back")
                    break
            await asyncio.sleep(12)
        return df
    
    finally:
        await close_browser(playwright, browser)
        
async def parsing_section(email, password):
    """Парсинг данных"""
    df = await start_parsing(email, password)
    df = df.drop('id', axis=1)
    df = df.drop_duplicates()
    await add_section_data_by_df(df, is_parsing = True)


async def get_isu_and_name(email, password):
    try:
        #вход
        playwright, browser, context, page = await create_browser()
        await open_site(page, "https://my.itmo.ru/sport/sign")
        await login(page, email, password)
                
        #сбор данных
        await page.wait_for_timeout(2500)
        isu_element = await page.query_selector('.text-muted.navbar-user-id')
        isu = await isu_element.inner_text() if isu_element else ""
        isu = isu.strip()
        name_element = await page.query_selector('.text-default.navbar-user-name')
        name = await name_element.inner_text() if name_element else ""
        name = name.strip()
        
    finally:
        await close_browser(playwright, browser)
        return isu, name

async def record(page, section_id):
    """Запись на занятие"""
    try:
        await page.click(f"#{section_id}")
        await page.click(".text-primary.font-weight-semibold.text-sm.cursor-pointer.mt-2")
        return True
    except:
        return False

class pars_cache():
    def __init__(self, cache_ttl: int = 20000):
        self.cache_ttl = cache_ttl
        self.time = time.time() - self.cache_ttl
        self.df = create_df()

    async def get_parsing(self, update: bool = False):
        if (time.time() - self.cache_ttl > self.time) or update:
            try:
                user_data = await get_random_user_data()
                email, password = user_data["email"], user_data["password"]
                self.df = await start_parsing(email, password, last_week=True)
                self.time = time.time()
                return self.df
            except:
                await login_error(user_data["user_id"])
                return await self.get_parsing(self, location)
        else:
            return self.df

pars = pars_cache()

async def records():
    try:
        df = await pars.get_parsing(update = True)
        playwright, browser, context, page = await create_browser()
        df = await pars.get_parsing()
        dt_records_user_data = await get_for_records_user_data(get_this_week_num(), datetime.date.today().weekday() + 1)
        for rec_dt in dt_records_user_data:
            user_dt = await get_user_data(rec_dt['user_id'])
            section_df = df[(df["Название"] == rec_dt['section'])* (df["Преподаватель"] == rec_dt['coach'])* (df["День"] == rec_dt['day_id'])* (df["Время"] == rec_dt['time_id'])* (df["location"] == str(rec_dt['location_id']))]
            if len(section_df) == 1:
                section_id = section_df.iloc[0].id
            else:
                #del_user_record(rec_dt['user_id'], rec_dt['section_id'])
                await send_err_record_to_user(user_dt['user_id'], rec_dt['section'], f"Найдено {len(section_df)} секций по заданным параметрам.")
                continue

            await open_site(page, "https://my.itmo.ru/sport/sign")
            await login(page, user_dt['email'], user_dt['password'])
            await flipping_through(page)
            await choose_a_location(page, str(rec_dt['location_id']))
            
            if await record(page, section_id):
                await send_success_record_to_user(user_dt['user_id'], rec_dt['section'])
            else:
                await send_err_record_to_user(user_dt['user_id'], rec_dt['section'])
            await exit_account(page)
            
    finally:
        await close_browser(playwright, browser)

async def record_main():
    """Функция для периодического вызова"""
    now = datetime.datetime.now()
    target_time = now.replace(hour=0, minute=0, second=20,microsecond=0)
    while True:
        now = datetime.datetime.now()
        if now >= target_time:
            target_time += datetime.timedelta(days=1)
        wait_seconds = (target_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        #бэкап бд
        create_backup()
        await records()

