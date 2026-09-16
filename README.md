# Отметка прихода в офис

Локальный сайт: сотрудник заходит с телефона/ноута из офисного Wi-Fi,
регистрируется, входит и жмёт «Пришёл в офис» — в PostgreSQL сохраняется
кто и во сколько пришёл.

## Стек

- **Фронт** — Vue 3 + Vite, отдаётся nginx (он же проксирует `/api` на бэкенд)
- **Бэкенд** — FastAPI + SQLAlchemy (async), JWT, пароли под bcrypt
- **БД** — PostgreSQL 17
- Всё в `docker compose`

## Запуск

```bash
cp .env.example .env
docker compose up -d --build
```

Сайт: `http://<ip-машины>:8080` — этот адрес и раздаёшь коллегам,
они открывают его с офисного Wi-Fi.

IP машины:

```bash
ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v 127.0.0.1
```

Если стоит firewall, открой порт:

```bash
sudo ufw allow 8080/tcp          # ufw
sudo firewall-cmd --add-port=8080/tcp --permanent && sudo firewall-cmd --reload   # firewalld
```

## Таблицы

`employees` — `id`, `name` (уникальное), `password_hash`, `created_at`
`checkins`  — `id`, `employee_id` → employees, `arrived_at`

Создаются сами при первом старте бэкенда.

## API

| Метод | Путь | Что делает |
|---|---|---|
| POST | `/api/auth/register` | регистрация, отдаёт JWT |
| POST | `/api/auth/login` | вход, отдаёт JWT |
| GET  | `/api/auth/me` | кто я |
| POST | `/api/checkins` | отметиться (раз в сутки) |
| GET  | `/api/checkins/me` | отметился ли я сегодня |
| GET  | `/api/checkins/today` | кто в офисе сегодня |
| GET  | `/api/checkins/history` | мои последние отметки |

Swagger-доки: прокинь порт бэкенда и открой `/docs`.

## Посмотреть данные руками

```bash
docker compose exec db psql -U office -d office -c \
  "select e.name, c.arrived_at from checkins c join employees e on e.id=c.employee_id order by c.arrived_at desc limit 20;"
```

## Разработка без докера

```bash
# бэкенд
cd backend && pip install -r requirements.txt
DATABASE_URL=postgresql+asyncpg://office:office@localhost:5432/office uvicorn app.main:app --reload

# фронт
cd frontend && npm install && npm run dev
```
