from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, SubmitField, URLField
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    Regexp,
    URL
)

from yacut.constants import ALLOWED_RE, SHORT_MAX_LEN
from yacut.models import URLMap


ERR_URL_REQUIRED = "Длинная ссылка обязательна"
ERR_URL_INVALID = "Некорректный URL"
ERR_CUSTOM_INVALID = "Указано недопустимое имя для короткой ссылки"
ERR_CUSTOM_EXISTS = "Предложенный вариант короткой ссылки уже существует"
ERR_FILES_REQUIRED = "Выберите хотя бы один файл"
SUBMIT_CREATE_LABEL = "Создать"


class URLForm(FlaskForm):
    """Форма для создания короткой ссылки."""

    original_link = URLField(
        "Длинная ссылка",
        validators=[
            DataRequired(message=ERR_URL_REQUIRED),
            URL(message=ERR_URL_INVALID),
            Length(
                max=URLMap.original.type.length,
                message=f"Максимум {URLMap.original.type.length} символов",
            ),
        ],
    )
    custom_id = StringField(
        "Ваш вариант короткой ссылки",
        validators=[
            Optional(),
            Length(
                max=SHORT_MAX_LEN,
                message=f"Максимум {SHORT_MAX_LEN} символов"
            ),
            Regexp(ALLOWED_RE, message=ERR_CUSTOM_INVALID),
        ],
    )
    submit = SubmitField(SUBMIT_CREATE_LABEL)


class FilesForm(FlaskForm):
    """Форма для загрузки нескольких файлов."""

    files = MultipleFileField(
        "Файлы",
        validators=[DataRequired(message=ERR_FILES_REQUIRED)],
    )
