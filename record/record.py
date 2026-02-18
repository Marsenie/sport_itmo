from record.week.week import get_this_week_num
from services.postgre_db import add_section_data, get_random_user_data, get_for_records_user_data, get_user_data, login_error
from alerts.alerts import *

import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import time
import datetime

place = {
    "онлайн": "null-0",
    "Ломо": "null-1", 
    "Вяземский": "null-2",
    "Другие": "null-3",
}

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
    await page.fill("#username", email)
    await page.fill("#password", password)
    await page.click("#kc-login")
    await page.wait_for_load_state('networkidle')

async def exit_account(page):
    """Авторизация"""
    try:
        await page.click(".nav-link.dropdown-toggle")
        await page.click(".bi-logout.dd-icon.b-icon.bi.text-danger")
        return True
    except:
        return False
    
async def flipping_through(page, direction="forward", times=2):
    """Перелистывание страниц"""
    if direction == "forward":
        selector = '//*[@id="__layout"]/div/div[1]/div/div[2]/div/div/div[4]/div/div/div[1]/div[1]/span/div/button[2]/span'
    else:
        selector = '//*[@id="__layout"]/div/div[1]/div/div[2]/div/div/div[4]/div/div/div[1]/div[1]/span/div/button[1]/span'
    
    for _ in range(times):
        await page.click(selector)

async def choose_a_location(page, location):
    """Выбор локации"""
    await page.click(".multiselect__tags")
    await page.click(f"#{place[location]}")

async def parsing(page, df, location: str):
    """Парсинг данных"""
    # Получаем все элементы расписания
    items = await page.query_selector_all('.el-calendar-row')
    for time in range(1, len(items)):  # время       
        items_in_str = await items[time].query_selector_all('.el-calendar-cell-lessons-container')
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
                            
                            df.loc[len(df)] = {
                                "Название": name_sports_section,
                                "Преподаватель": coach,
                                "День": day + 1,
                                "Время": time,
                                "id": identifier,
                                "location": location
                            }
                    except:
                        pass
    
    return df

async def parsing_section(email, password):
    """Парсинг данных"""
    playwright, browser, context, page = await create_browser()

    try:
        await open_site(page, "https://my.itmo.ru/sport/sign")
        await login(page, email, password)
        
        for location in place:
            await choose_a_location(page, location)
            # Получаем все элементы расписания
            items = await page.query_selector_all('.el-calendar-row')
            on_even_numbers = get_this_week_num()
            # Пролистываем неделю
            await flipping_through(page, times = 1)
            for time in range(1, 8):  # время
                if time >= len(items):
                    break
                     
                items_in_str = await items[time].query_selector_all('.el-calendar-cell-lessons-container')
                
                for day in range(len(items_in_str)):  # день
                    items_in_cell = await items_in_str[day].query_selector_all('.section-block')
                    
                    for item in items_in_cell:
                        selectors = ['sport-item-cant-sign', '.sport-item']
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
                                    #identifier = await item.get_attribute('id') or ""
                                    await add_section_data(name_sports_section, coach, day + 1, str(time), location, is_parsing = True)
                            except:
                                pass
                            
                
                on_even_numbers = (on_even_numbers + 1) % 2
            await flipping_through(page, times = 1, direction = "back")
            
        return True
    finally:
        await close_browser(playwright, browser)
                

async def check_records(df, email, password, location: str):
    """Проверка записей"""
    playwright, browser, context, page = await create_browser()
    
    try:
        await open_site(page, "https://my.itmo.ru/sport/sign")
        await login(page, email, password)
        
        if location != "Ломо":
            await choose_a_location(page, location)

        await flipping_through(page, times=1)
        return await parsing(page, df, location)
        
    finally:
        await close_browser(playwright, browser)

async def get_isu_and_name(email, password):
    try:
        #вход
        playwright, browser, context, page = await create_browser()
        await open_site(page, "https://my.itmo.ru/sport/sign")
        await login(page, email, password)

        #сбор данных
        isu_element = await page.query_selector('.text-muted.navbar-user-id')
        isu = await isu_element.inner_text() if isu_element else ""
        isu = isu.strip()
        name_element = await page.query_selector('.text-default.navbar-user-name')
        name = await name_element.inner_text() if name_element else ""
        name = name.strip()
        
    finally:
        await close_browser(playwright, browser)
        if isu != "":
            return isu, name
        return "", ""

async def record(page, section_id):
    """Запись на занятие"""
    try:
        await page.click(f"#{section_id}")
        await page.click(".text-primary.font-weight-semibold.text-sm.cursor-pointer.mt-2")
        return True
    except:
        return False
    

    
class pars_cache():
    def __init__(self, cache_ttl: int = 4000):
        self.cache_ttl = cache_ttl
        self.ls_time = place.copy()
        for i in self.ls_time:
            self.ls_time[i] = time.time() - self.cache_ttl
        self.df = pd.DataFrame(columns=["Название", "Преподаватель", "День", "Время", "id", "location"])

    async def get_parsing(self, location: str, update: bool = False):
        user_data = await get_random_user_data()
        email, password = user_data["email"], user_data["password"]
        if time.time() - self.cache_ttl > self.ls_time[location] or update:
            try:
                self.ls_time[location] = time.time()
                self.df = self.df[self.df.location != location]
                self.df = await check_records(self.df, email, password, location)
                return self.df
            except:
                # пометка об ошибке
                await login_error(user_data["user_id"])
                return await get_parsing(self, location)
        else:
            return self.df
pars = pars_cache()

async def records():
    try:
        playwright, browser, context, page = await create_browser()
        for i in place:
            await pars.get_parsing(location = i, update = True)
            dt_records_user_data = await get_for_records_user_data(get_this_week_num(), datetime.date.today().weekday() + 1)
            for rec_dt in dt_records_user_data:
                await open_site(page, "https://my.itmo.ru/sport/sign")
                user_dt = await get_user_data(rec_dt['user_id'])
                await login(page, user_dt['email'], user_dt['password'])
                await flipping_through(page)
                await choose_a_location(page, rec_dt['location'])
                df = await pars_cache.get_parsing(pars, location = rec_dt['location'])
                df = df[(df["Название"] == rec_dt['section'])* (df["Преподаватель"] == rec_dt['coach'])* (df["День"] == rec_dt['day_id'])* (df["Время"] == rec_dt['time_id'])* (df["location"] == rec_dt['location'])]
                if len(df) == 1:
                    section_id = df.iloc[0].id
                else:
                    await send_err_record_to_user(user_dt['user_id'], rec_dt['section'], f"Найдено {len(df)} секций по заданным параметрам.")
                    continue

                if await record(page, section_id):
                    await send_success_record_to_user(user_dt['user_id'], rec_dt['section'])
                else:
                    await send_err_record_to_user(user_dt['user_id'], rec_dt['section'])
                if await exit_account(page):
                    #Логирование
                    pass
    finally:
        await close_browser(playwright, browser)

async def periodic_task():
    """Функция для периодического вызова"""
    now = datetime.datetime.now()
    target_time = now.replace(hour=0, minute=1, second=0,microsecond=0)
    while True:
        
        # Ждем до 00:01
        if now >= target_time:
            target_time += datetime.timedelta(days=1)
        wait_seconds = (target_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        
        await records()
        await asyncio.sleep(60)
