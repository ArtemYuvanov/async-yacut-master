from flask import redirect, render_template, request
from settings import Config
from yacut import app
from yacut.forms import FilesForm, URLForm
from yacut.models import URLMap
from yacut.async_upload import upload_files
import asyncio


@app.route("/", methods=["GET", "POST"])
def index():
    """Главная страница с формой для создания короткой ссылки."""
    form = URLForm()

    if not form.validate_on_submit():
        return render_template("index.html", form=form)

    try:
        mapping = URLMap.create_with_custom_or_generated(
            original=form.original_link.data, custom=form.custom_id.data
        )
    except ValueError as exc:
        return render_template("index.html", form=form, error=str(exc))

    short_url = mapping.short_link_url(request.host_url)
    return render_template("index.html", form=form, short_url=short_url)


@app.route("/<string:short>")
def redirect_short(short):
    """Перенаправление по короткой ссылке на оригинальный адрес."""
    mapping = URLMap.query.filter_by(short=short).first_or_404()
    return redirect(mapping.original)


@app.route("/files", methods=["GET", "POST"])
def files():
    form = FilesForm()
    uploaded_files = []

    if not form.validate_on_submit():
        return render_template(
            "files.html",
            form=form,
            uploaded_files=uploaded_files
        )

    try:
        results = asyncio.run(
            upload_files(Config.DISK_TOKEN, form.files.data)
        )

        for file_obj, public_url in zip(form.files.data, results):
            if isinstance(public_url, Exception):
                uploaded_files.append(
                    {"filename": file_obj.filename, "error": str(public_url)}
                )
                continue

            mapping = URLMap.create_with_custom_or_generated(
                original=public_url
            )
            uploaded_files.append(
                {
                    "filename": file_obj.filename,
                    "short_url": mapping.short_link_url(request.host_url),
                }
            )

    except ValueError as exc:
        uploaded_files.append({"error": str(exc)})

    return render_template(
        "files.html", form=form, uploaded_files=uploaded_files
    )
