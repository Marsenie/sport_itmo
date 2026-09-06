import asyncio
import time
from typing import Any

from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.methods import TelegramMethod


class RotatingProxySession(AiohttpSession):
    def __init__(
        self,
        get_proxy_func,
        refresh_interval: int = 600,
    ):
        self.get_proxy_func = get_proxy_func
        self.refresh_interval = refresh_interval

        self.proxies: list[str] = []
        self.proxy_index = 0
        self.last_refresh = 0.0

        self._proxy_lock = asyncio.Lock()

        super().__init__()

    @property
    def current_proxy(self) -> str | None:
        if not self.proxies:
            return None

        return self.proxies[self.proxy_index]

    def _normalize_proxies(self, proxies):
        return [
            proxy.replace("socks5://", "").strip()
            for proxy in proxies
            if proxy
        ]

    async def _load_proxies(self, force=False):
        now = time.monotonic()

        if not force and now - self.last_refresh < self.refresh_interval:
            return False

        async with self._proxy_lock:
            now = time.monotonic()

            if not force and now - self.last_refresh < self.refresh_interval:
                return False

            # print("Получаем новый список proxy...")

            proxies = self.get_proxy_func()
            proxies = self._normalize_proxies(proxies)

            if not proxies:
                raise RuntimeError(
                    "get_proxy_list() вернул пустой список"
                )

            self.proxies = proxies
            self.proxy_index = 0
            self.last_refresh = time.monotonic()

            self._proxy = f"socks5://{self.current_proxy}"

            # print(f"Получено proxy: {len(self.proxies)}")
            # print(f"Используем proxy: {self.current_proxy}")

            return True

    async def _switch_proxy(self):
        async with self._proxy_lock:

            # Есть следующий proxy
            if self.proxy_index + 1 < len(self.proxies):
                self.proxy_index += 1

                self._proxy = f"socks5://{self.current_proxy}"

                # print(f"Переключаем proxy {self.proxy_index + 1}/{len(self.proxies)}: {self.current_proxy}")

                return True

            # Дошли до конца списка
            # print("Список proxy закончился.")

            now = time.monotonic()

            # Прошло 10 минут — можно получить новый список
            if now - self.last_refresh >= self.refresh_interval:
                await self.__load_proxies()
                return True

            # 10 минут ещё не прошло.
            await asyncio.sleep(30)
            await self._switch_proxy()


    async def make_request(
        self,
        bot,
        method: TelegramMethod[Any],
        timeout: int | None = 2,
    ):
        # Первый запрос
        if not self.proxies:
            await self._load_proxies(force=True)

        # Сохраняем количество proxy
        attempts = len(self.proxies)

        for attempt in range(attempts):

            try:
                print(f"Telegram API → {self.current_proxy}")

                return await super().make_request(
                    bot,
                    method,
                    timeout=timeout,
                )

            except Exception as e:

                print(f"Proxy {self.current_proxy} не отвечает: {type(e).__name__}: {e}")
                await self._switch_proxy()

        raise RuntimeError("Не удалось выполнить Telegram API запрос")
