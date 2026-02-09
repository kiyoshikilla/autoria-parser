# Autoria Scraper

Асинхронний Python-скрапер для auto.ria.com з контейнеризацією (Docker), PostgreSQL, Playwright, APScheduler та автоматичним дампом БД.

## Можливості
- Асинхронний парсинг оголошень з auto.ria.com (з підтримкою пагінації)
- Збереження даних у PostgreSQL з унікальністю по `ria_id` (відсутність дублів)
- Автоматичний щоденний дамп БД у папку `dumps` о 12:00 (APScheduler + pg_dump)
- Запуск через Docker Compose

## Швидкий старт


1. **Клонувати репозиторій**
2. **Створити .env** (приклад для Docker):
	```env
	POSTGRES_DB=exampledb
	POSTGRES_USER=exampleuser
	POSTGRES_PASSWORD=examplepass
	DATABASE_URL=postgresql+asyncpg://exampleuser:examplepass@db:5432/exampledb
	```
3. **Запустити через Docker Compose**
	```bash
	docker-compose up --build
	```
4. **Перевірити дампи**
	- Дампи БД зберігаються у папці `dumps/` у корені проєкту

## Структура проєкту

- `src/main.py` — основний запуск скрапера
- `src/scraper.py` — логіка парсингу (пошук, деталі, пагінація, images_count, phone_number)
- `src/models.py` — SQLAlchemy моделі (див. опис полів нижче)
- `src/database.py` — робота з БД (upsert, engine)
- `src/dumper.py` — автоматичний дамп БД (APScheduler + pg_dump)
- `docker-compose.yml` — запуск застосунку та БД
- `dumps/` — папка для дампів

## Опис полів у БД

- url — посилання на оголошення
- title — назва авто
- price_usd — ціна в доларах
- odometer — пробіг у кілометрах (число)
- username — ім'я продавця
- phone_number — телефон у форматі 380XXXXXXXXX (тільки цифри, якщо є)
- image_url — посилання на головне фото
- images_count — кількість фото
- car_number — номер авто (якщо є)
- car_vin — VIN-код (якщо є)
- datetime_found — дата/час збереження в базу

## Залежності
- Python 3.11+
- Playwright
- asyncpg, SQLAlchemy
- APScheduler
- PostgreSQL
- Docker, Docker Compose

## Корисні команди

### Встановити Playwright браузери (локально)
```
playwright install
```

### Ручний дамп БД
```
python -m src.dumper
```
