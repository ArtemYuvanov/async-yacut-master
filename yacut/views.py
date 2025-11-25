from flask import flash, redirect, render_template

from yacut import app
from yacut.async_upload import upload_files_sync
from yacut.forms import FilesForm, URLForm
from yacut.models import URLMap


@app.route("/", methods=["GET", "POST"])
def index():
    """Главная страница с формой для создания короткой ссылки."""
    form = URLForm()

    if not form.validate_on_submit():
        return render_template("index.html", form=form)

    try:
        short_url = URLMap.create(
            original=form.original_link.data,
            short=form.custom_id.data
        ).short_url()
    except ValueError as exc:
        flash(str(exc), "danger")
        return render_template("index.html", form=form, error=str(exc))

    return render_template("index.html", form=form, short_url=short_url)


@app.route("/<string:short>")
def redirect_short(short):
    """Перенаправление по короткой ссылке на оригинальный адрес."""
    mapping = URLMap.get_or_404(short)
    return redirect(mapping.original)


@app.route("/files", methods=["GET", "POST"])
def files():
    """Загрузка и отображение списка файлов."""
    form = FilesForm()

    if not form.validate_on_submit():
        return render_template("files.html", form=form)

    try:
        results = upload_files_sync(form.files.data)
    except Exception as exc:
        error = f"Ошибка загрузки файлов: {exc}"
        return render_template("files.html", form=form, error=error)

    uploaded_files = []
    for f, url in zip(form.files.data, results):
        try:
            short_url = URLMap.create(original=url).short_url()
            uploaded_files.append(
                {"filename": f.filename, "short_url": short_url}
            )
        except Exception as exc:
            uploaded_files.append(
                {"filename": f.filename, "error": str(exc)}
            )

    return render_template(
        "files.html", form=form, uploaded_files=uploaded_files
    )
