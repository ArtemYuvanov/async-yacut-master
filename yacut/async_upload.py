import asyncio
from http import HTTPStatus

import aiohttp

from settings import Config

ERROR_UPLOAD = "Ошибка загрузки {file}: {status}"
ERROR_GET_HREF = "Не удалось получить публичную ссылку для {file}"
ERROR_GET_UPLOAD_LINK = "Ошибка получения ссылки для загрузки: {status} {data}"

YADISK_UPLOAD_URL = f"{Config.YADISK_API_BASE}/upload"
YADISK_DOWNLOAD_URL = f"{Config.YADISK_API_BASE}/download"
YADISK_HEADERS = {"Authorization": f"OAuth {Config.DISK_TOKEN}"}


async def upload_file_to_yadisk(session, file_obj):
    """Загрузка одного файла на Яндекс.Диск и получение публичной ссылки."""

    remote_path = f"app:/{file_obj.filename}"

    async with session.get(
        YADISK_UPLOAD_URL,
        headers=YADISK_HEADERS,
        params={"path": remote_path, "overwrite": "true"},
    ) as resp:
        data = await resp.json()
        if resp.status != HTTPStatus.OK or "href" not in data:
            raise RuntimeError(
                ERROR_GET_UPLOAD_LINK.format(status=resp.status, data=data)
            )
        upload_href = data["href"]

    file_obj.stream.seek(0)
    content = file_obj.read()

    async with session.put(upload_href, data=content) as resp:
        if resp.status not in (HTTPStatus.OK, HTTPStatus.CREATED):
            raise RuntimeError(
                ERROR_UPLOAD.format(
                    file=file_obj.filename, status=resp.status
                )
            )

    async with session.get(
        YADISK_DOWNLOAD_URL,
        headers=YADISK_HEADERS,
        params={"path": remote_path},
    ) as info_resp:
        public_url = (await info_resp.json()).get("href")
        if not public_url:
            raise RuntimeError(ERROR_GET_HREF.format(file=file_obj.filename))

    return public_url


async def upload_files(files):
    """Загрузка списка файлов на Яндекс.Диск."""
    async with aiohttp.ClientSession() as session:
        tasks = [upload_file_to_yadisk(session, f) for f in files]
        return await asyncio.gather(*tasks, return_exceptions=True)


def upload_files_sync(files):
    return asyncio.run(upload_files(files))
