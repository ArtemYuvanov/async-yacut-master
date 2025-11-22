import re
import string
import os

ORIGINAL_MAX_LEN = 2048
SHORT_MAX_LEN = 16
RESERVED_IDS = {"files"}
SHORT_ID_ALPHABET = string.ascii_letters + string.digits
SHORT_ID_LENGTH = 6
MAX_GENERATION_ATTEMPTS = 1000
ALLOWED_RE = rf"^[{re.escape(SHORT_ID_ALPHABET)}]+$"

YADISK_API_BASE = "https://cloud-api.yandex.net/v1/disk/resources"

YADISK_TOKEN = os.getenv("DISK_TOKEN")
YADISK_HEADERS_TEMPLATE = {"Authorization": f"OAuth {YADISK_TOKEN}"}
