from http import HTTPStatus
from flask import jsonify, request

from yacut import app
from yacut.models import URLMap


ERR_CUSTOM_EXISTS = "Предложенный вариант короткой ссылки уже существует"


@app.route("/api/id/", methods=["POST"])
def api_create_id():
    """Создаёт короткую ссылку через API."""
    data = request.get_json(silent=True)
    if not data:
        return (
            jsonify({"message": "Отсутствует тело запроса"}),
            HTTPStatus.BAD_REQUEST
        )

    if "url" not in data or not data.get("url"):
        return (
            jsonify({"message": '"url" является обязательным полем!'}),
            HTTPStatus.BAD_REQUEST,
        )

    original_url = data["url"]
    custom = data.get("custom_id")

    try:
        mapping = URLMap.create_with_custom_or_generated(
            original=original_url, custom=custom
        )
    except ValueError as exc:
        return jsonify({"message": str(exc)}), HTTPStatus.BAD_REQUEST

    short_link = mapping.short_link_url(request.host_url)
    return (
        jsonify({"url": original_url, "short_link": short_link}),
        HTTPStatus.CREATED
    )


@app.route("/api/id/<string:short>/", methods=["GET"])
def api_get_url(short):
    """Возвращает исходный URL по короткому идентификатору."""
    mapping = URLMap.query.filter_by(short=short).first()
    if not mapping:
        return (
            jsonify({"message": "Указанный id не найден"}),
            HTTPStatus.NOT_FOUND
        )

    return jsonify({"url": mapping.original}), HTTPStatus.OK
