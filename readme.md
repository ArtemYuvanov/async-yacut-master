# YaCut — сервис коротких ссылок

YaCut — это веб-приложение на Flask, позволяющее создавать короткие ссылки для любых URL-адресов.  
Пользователь может сгенерировать случайный идентификатор или задать свой вариант короткого имени.

---

## Возможности

- Создание коротких ссылок через веб-интерфейс  
- Создание коротких ссылок через API  
- Проверка пользовательских идентификаторов на корректность и уникальность  
- Перенаправление по короткому идентификатору на исходный URL  
- Простая и надёжная работа с базой данных SQLite

---

## Технологии

- Python 3.9+
- Flask
- Flask-SQLAlchemy
- Flask-WTF
- Jinja2
- SQLite (по умолчанию)

---

## Установка и запуск

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/ArtemYuvanov/ASYNC-YACUT-MAIN.git
   ```
2. Установите и активируйте виртуальное окружение:
   ```
   python -m venv venv
   source venv/Scripts/activate      # Windows
   source venv/bin/activate          # macOS/Linux
   ```
3. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
4. Создайте файл .env и добавьте настройки:
   ```
   FLASK_APP=yacut
   FLASK_ENV=development
   SECRET_KEY=super_secret_key
   DATABASE_URI=sqlite:///db.sqlite3
   ```
5. Инициализируйте базу данных:
   ```
   flask shell
   >>> from yacut import db
   >>> db.create_all()
   >>> exit()
   ```
6. Запустите сервер:
   ```
   flask run
   ```

Приложение будет доступно по адресу:
http://127.0.0.1:5000

## Использование API

1. Создание короткой ссылки

POST /api/id/
Пример запроса:
```
{
  "url": "https://www.python.org/",
  "custom_id": "python"
}
```
Пример ответа (201):
```
{
  "url": "https://www.python.org/",
  "short_link": "http://127.0.0.1:5000/python"
}
```
Ошибки (400):
```
{"message": "Указано недопустимое имя для короткой ссылки"}

{"message": "Предложенный вариант короткой ссылки уже существует."}

{"message": "\"url\" является обязательным полем!"}

{"message": "Отсутствует тело запроса"}
```
2. Получение оригинальной ссылки

GET /api/id/<short_id>/

Пример ответа (200):
```
{"url": "https://www.python.org/"}
```
Ошибки (404):
```
{"message": "Указанный id не найден"}
```
## Структура проекта

yacut/
├── __init__.py
├── api_views.py         # API эндпоинты
├── error_handlers.py    # Кастомные обработчики ошибок API
├── forms.py             # Flask-WTF формы
├── models.py            # SQLAlchemy модель URLMap
├── static/              # Статические файлы (CSS, JS)
├── templates/           # HTML-шаблоны (index.html и др.)
├── utils.py             # Утилиты (генерация коротких id)
└── views.py             # Основные маршруты сайта


## Примеры коротких ссылок

Исходная ссылка Короткая ссылка
https://python.org http://127.0.0.1:5000/python
https://peps.python.org/pep-0008/ http://127.0.0.1:5000/pep8

## Автор

Артём Юванов
Проект создан в рамках учебного курса Flask + API
