from services.postgre_db import add_ban_user, get_ban_user

import aiofiles
import asyncio
import json
from pathlib import Path
from typing import List, Dict
import time

class BanStorage:
    def __init__(self, filepath: str):
        self.cache_update = 60
        self.time_last_update = time.time() - self.cache_update
        self.filepath = Path(filepath)
        # создаём папки, если их нет
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        # внутри процесса блокировка, чтобы не читать/писать одновременно
        self._lock = asyncio.Lock()

    async def _read_all(self) -> Dict[str, List[str]]:
        async with self._lock:
            if not self.filepath.exists():
                return {}
            async with aiofiles.open(self.filepath, 'r', encoding='utf-8') as f:
                text = await f.read()
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return {}

    async def write_all(self, data: Dict[str, List[str]]):
        """Записать весь словарь в файл."""
        async with self._lock:
            async with aiofiles.open(self.filepath, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))


    async def ban_user(self, user_id: str, msg: str, reason_id: int):
        current_time = time.time()
        data = await self._read_all()
        data[user_id] = current_time + self.cache_update * 2
        await self.write_all(data)
        await add_ban_user(user_id, msg, reason_id)
        
    async def update(self):
        current_time = time.time()
        if current_time - self.cache_update > self.time_last_update:
            ban_user = await get_ban_user()
            data =  {}
            for i in ban_user:
                data[i['user_id']] = current_time + self.cache_update * 2
            self.time_last_update = time.time()
            await self.write_all(data)

