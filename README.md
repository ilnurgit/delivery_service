# Delivery Service — микросервис международной доставки

Сервис принимает данные о посылках и рассчитывает стоимость доставки.
Стек: **Python 3.12+, FastAPI (async), SQLAlchemy (async), PostgreSQL, Redis, Celery, RabbitMQ, Alembic, pytest, uv**.

---

## Что реализовано по ТЗ

### Роуты (API v1)

1) **Регистрация посылки**
- `POST /api/v1/parcels/`
- Поля: `title`, `weight_kg`, `parcel_type_code`, `content_usd`
- Валидация входных данных (Pydantic)
- Возвращает `id` посылки (UUID), который **доступен только в рамках текущей сессии**

2) **Получить список типов посылок**
- `GET /api/v1/parcel-types/`

3) **Получить список своих посылок**
- `GET /api/v1/parcels/?limit=...&offset=...`
- Фильтры:
  - `parcel_type_code=...`
  - `has_cost=true|false`
- Выводит: все поля + имя типа + стоимость доставки (или “Не рассчитано”)

4) **Получить посылку по id**
- `GET /api/v1/parcels/{parcel_id}`

### Периодические задачи (Celery)

- Раз в **1 минуту** обновляет курс **USD/RUB** (ЦБ РФ) и кеширует в Redis.
- Раз в **5 минут** выставляет всем необработанным посылкам `delivery_cost_rub` по формуле ТЗ:
  ```
  cost_rub = (weight_kg * 0.5 + content_usd * 0.01) * usd_rub_rate
  ```

### Ручной запуск задач (для отладки)

- `POST /api/v1/fx/refresh` — инициировать обновление курса
- `POST /api/v1/parcels/refresh-costs?batch_size=500` — инициировать перерасчёт стоимости посылок

### Мини UI

- `GET /ui` — простая HTML-страница:
  - создать тип посылки
  - создать посылку
  - кнопка “Рассчитать стоимость”
  - таблица “Мои посылки”

---

## Важное про сессию (без авторизации)

Авторизации нет по ТЗ. Пользователь определяется по cookie:

- Cookie: `delivery_session_id`
- Выставляется middleware при первом запросе (например, на `/health`)
- Во всех запросах к посылкам используется `request.state.session_id`

Гарантия: **посылки видны только внутри своей сессии** (покрыто тестами).

---

## Типы посылок и соответствие ТЗ

В ТЗ перечислены типы: **«одежда», «электроника», «разное»**.
В реализации типы сделаны **расширяемыми** и хранятся в таблице `parcel_types` (как требует ТЗ), а тариф вынесен в поля:

- `base_price_usd`
- `price_per_kg_usd`

Это позволяет добавлять/изменять типы **без изменения кода**.

Проект содержит **сид-миграцию** с примерами типов (`DOC`, `BOX`).
При необходимости типы из ТЗ можно создать через API/UI, например:
- `CLOTHES` (Одежда)
- `ELECTRONICS` (Электроника)
- `OTHER` (Разное)

---

## Про расчёт стоимости: 2 модели в проекте (это нормально)

1) **Расчёт delivery_cost_rub (строго по ТЗ)**
Используется периодической задачей/ручным refresh:
```
cost_rub = (weight_kg * 0.5 + content_usd * 0.01) * usd_rub_rate
```

2) **Калькулятор /pricing (тарифная модель по типам)**
- `POST /api/v1/pricing/calculate`
- Формула:
```
amount_usd = base_price_usd + price_per_kg_usd * weight_kg
```
- Если `currency=RUB`, конвертирует через FX (кешируется в Redis)

Это сделано так, чтобы:
- delivery_cost_rub проставлялся “как в ТЗ” (фоновой задачей)
- при этом был отдельный “калькулятор тарифа” по типам

---

## Запуск проекта

### 1) Поднять инфраструктуру (Postgres / Redis / RabbitMQ)

```bash
docker compose up -d
```

### 2) Настроить окружение

Файл `.env` (пример — см. структуру проекта). Нужны переменные:

- `database_url`
- `redis_url`
- `rabbitmq_url`

Также в docker-compose используются:
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`
- `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS`

### 3) Миграции

```bash
uv run alembic upgrade head
```

### 4) Запуск API

```bash
uv run uvicorn delivery.main:app --reload
```

Открой:
- Swagger: `http://127.0.0.1:8000/docs`
- UI: `http://127.0.0.1:8000/ui`
- Health: `http://127.0.0.1:8000/health`

---

## Запуск Celery

В разных терминалах:

### Worker
```bash
uv run celery -A delivery.core.celery_app:celery_app worker -l INFO
```

### Beat
```bash
uv run celery -A delivery.core.celery_app:celery_app beat -l INFO
```

---

## Быстрые примеры запросов (curl)

### Создать тип
```bash
curl -X POST http://127.0.0.1:8000/api/v1/parcel-types/ \
  -H "Content-Type: application/json" \
  -d '{"code":"DOC","name":"Documents","base_price_usd":"5.00","price_per_kg_usd":"2.50"}'
```

### Создать посылку
```bash
curl -X POST http://127.0.0.1:8000/api/v1/parcels/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Passport","parcel_type_code":"DOC","weight_kg":2,"content_usd":"100.00"}'
```

### Список посылок (пагинация)
```bash
curl "http://127.0.0.1:8000/api/v1/parcels/?limit=50&offset=0"
```

### Перерасчёт delivery_cost_rub вручную
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/parcels/refresh-costs?batch_size=500"
```

---

## Ошибки и формат ответов

Единый envelope для ошибок:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": [],
    "trace_id": "..."
  }
}
```

Также на каждый запрос выставляется:
- Header: `X-Trace-Id`
- Логи access-log с `trace_id`

---

## Тесты

```bash
uv run pytest -q
```

Есть:
- unit
- integration (ASGI in-process + DB/Redis)
- e2e

---

## Известные предупреждения

- `SAWarning: transaction already deassociated from connection` — допускается (не блокирует сдачу), можно не устранять по договорённости.
