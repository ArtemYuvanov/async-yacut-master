import asyncio
import aiohttp

from yacut.constants import YADISK_API_BASE, YADISK_HEADERS_TEMPLATE
from yacut.models import URLMap


async def upload_file_to_yadisk(session, token, file_obj):
    headers = {**YADISK_HEADERS_TEMPLATE, "Authorization": f"OAuth {token}"}
    unique_id = URLMap.generate_unique_short_id()
    remote_path = f"app:/{unique_id }_{file_obj.filename}"
    async with session.get(
        f"{YADISK_API_BASE}/upload",
        headers=headers,
        params={"path": remote_path, "overwrite": "true"},
    ) as resp:
        data = await resp.json()
        if resp.status != 200 or "href" not in data:
            raise RuntimeError(
                f"Ошибка получения ссылки для загрузки: {resp.status} {data}"
            )
        upload_href = data["href"]

    file_obj.stream.seek(0)
    content = file_obj.read()
    async with session.put(upload_href, data=content) as resp:
        if resp.status not in (200, 201):
            error_text = await resp.text()
            raise RuntimeError(
                f"Ошибка загрузки {file_obj.filename}: "
                f"{resp.status} {error_text}"
            )

    async with session.get(
        f"{YADISK_API_BASE}/download",
        headers=headers,
        params={"path": remote_path},
    ) as info_resp:
        info = await info_resp.json()
        public_url = info.get("href")
        if not public_url:
            raise RuntimeError(
                f"Не удалось получить публичную ссылку для {file_obj.filename}"
            )
        return public_url


async def upload_files(token, files):
    async with aiohttp.ClientSession() as session:
        tasks = [upload_file_to_yadisk(session, token, f) for f in files]
        return await asyncio.gather(*tasks, return_exceptions=True)
