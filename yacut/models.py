import random
import re
from datetime import datetime, timezone

from yacut import db
from yacut.constants import (
    ALLOWED_RE,
    MAX_GENERATION_ATTEMPTS,
    ORIGINAL_MAX_LEN,
    RESERVED_IDS,
    SHORT_ID_ALPHABET,
    SHORT_ID_LENGTH,
    SHORT_MAX_LEN,
)


class URLMap(db.Model):
    """Модель для хранения оригинальных и коротких URL."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(ORIGINAL_MAX_LEN), nullable=False)
    short = db.Column(db.String(SHORT_MAX_LEN), unique=True, nullable=False)
    timestamp = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    @staticmethod
    def is_valid_custom_id(custom_id: str) -> bool:
        """Проверка корректности пользовательского короткого идентификатора."""
        if not custom_id:
            return False
        candidate = custom_id.strip()
        return (
            candidate.isalnum()
            and len(candidate) <= SHORT_MAX_LEN
            and candidate.lower() not in RESERVED_IDS
        )

    @classmethod
    def generate_unique_short_id(cls):
        for _ in range(MAX_GENERATION_ATTEMPTS):
            candidate = "".join(random.choices(
                SHORT_ID_ALPHABET, k=SHORT_ID_LENGTH
            ))
            if (
                not cls.query.filter_by(short=candidate).first()
                and candidate not in RESERVED_IDS
            ):
                return candidate
        raise ValueError(
            "Не удалось сгенерировать уникальный короткий идентификатор"
        )

    @classmethod
    def create_with_custom_or_generated(cls, original, custom=None):
        if custom:
            candidate = custom
            if (
                candidate.lower() in RESERVED_IDS
                or cls.query.filter_by(short=candidate).first()
            ):
                raise ValueError(
                    "Предложенный вариант короткой ссылки уже существует."
                )
            if not re.match(ALLOWED_RE, candidate):
                raise ValueError(
                    "Указано недопустимое имя для короткой ссылки"
                )
            if len(candidate) > SHORT_MAX_LEN:
                raise ValueError(
                    "Указано недопустимое имя для короткой ссылки"
                )
            short_id = candidate
        else:
            short_id = cls.generate_unique_short_id()

        mapping = cls(original=original, short=short_id)
        db.session.add(mapping)
        db.session.commit()
        return mapping

    def short_link_url(self, host_url):
        return f"{host_url}{self.short}"

    def short_link_url(self, host_url: str) -> str:
        """Возвращает полный URL короткой ссылки для этого экземпляра."""
        return f"{host_url.rstrip('/')}/{self.short}"
