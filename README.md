# 📘 Backend API: Задачник с ролями, историей и рекомендациями

## ✅ Прогресс по проекту

### API-функциональность:
- [x] Auth: регистрация, логин, роли ✅ 2025-07-28
- [x] Tasks: CRUD, связка с пользователями ✅ 2025-07-28
- [x] Users: профили, роли ✅ 2025-07-28
- [x] Model-интерфейс: предсказания ✅ 2025-07-28
- [x] История решений пользователя ✅ 2025-07-30
- [x] CRUD для учителей (создание задач), модерация ✅ 2025-07-30
- [x] Админ-функции (бан, удаление пользователей, задач) ✅ 2025-07-30
- [x] Сделать API. ✅ 2025-08-02 

### База данных:
- [x] Подключена через Tortoise ORM ✅ 2025-07-28
- [x] Сделать миграцию в SQLAlchemy? ✅ 2025-07-28
- [x] Сделать миграцию в PostgresSQL? - потом, sqlite пойдет ✅ 2025-07-28
- [x] Продуманная структура моделей ✅ 2025-07-30
- [x] Инициализация, миграция ✅ 2025-07-30
- [x] Связи между таблицами ✅ 2025-07-30
- [x] Начальные фикстуры (админ-пользователь)

### Мониторинг и метрики:
- [x] Sentry - отслеживание ошибок ✅ 2025-07-28
- [x] Prometheus - метрики ✅ 2025-07-28
- [x] Логирование (stdout + ротация логов) ✅ 2025-08-11 
- [x] Healthcheck (/health) ✅ 2025-08-11 

### Документация:
- [x] Swagger/OpenAPI ✅ 2025-07-28
- [x] README.md документация

### Docker и продакшн:
- [x] Dockerfile ✅ 2025-07-28
- [x] docker-compose.yml ✅ 2025-08-11 
- [x] продакшн-режим ✅ 2025-08-11
- [x] .env файлы ✅ 2025-08-01

### Безопасность:
- [x] JWT-аутентификация ✅ 2025-07-28
- [x] Ограничение доступа по ролям ✅ 2025-07-28 

### Тесты:
- [x] Unit-тесты на логику ✅ 2025-08-07
- [x] API-тесты ✅ 2025-08-10
- [ ] Тесты миграций
- [ ] Интеграционные тесты

---

# 🚀 Инструкция по запуску проекта

### ✅ Предусловия

- Python 3.11+
- SQLite
- Redis (для logout токенов)
- Установлен `poetry` или `pip`
- Создан `.env` файл

### 📄 Пример `.env`

```env
SECRET_KEY=supersecretkey
ACCESS_TOKEN_EXPIRE_MINUTES=10
SQL_URL=sqlite+aiosqlite:///./app.db
ALGORITHM=HS256
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your-redis-password
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@admin.com
ADMIN_PASSWORD=admin-password
```

### Установка зависимостей

Poetry:
```bash
poetry install
```


---
#### Данные команды запускают только api, без метрик и redis (нужен для logout), для полноценного запуска смотреть инструкцию для docker
### Запуск приложения

Запуск через Uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Запуск через `__main__` блок:
```bash
python app/main.py
```

### Swagger UI

```
http://localhost:8000/docs
```
--- 
## 🐳 Запуск через Docker

### 1. Сборка и запуск контейнера
```bash
docker compose up -d --build
```
### 2. Проверить статус контейнеров
```bash
docker compose ps
```
### 3. Логи (по необходимости)
```bash
# все сервисы
docker compose logs -f
# отдельно по сервисам
docker compose logs -f app
docker compose logs -f node-exporter
docker compose logs -f cadvisor
docker compose logs -f prometheus
docker compose logs -f grafana
```
### 4. Остановка и удаление
```bash
docker compose down
```
## 🔗 Полезные адреса (по умолчанию)

- API (Swagger): `http://localhost:8000/docs`
- Экспорт метрик приложения: `http://localhost:8000/metrics`
- Node Exporter: `http://localhost:9100/metrics`
- cAdvisor UI: `http://localhost:8080/`
---
# Реализованные маршруты (Routers)

## Auth (`/auth`)
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/auth/register` | Регистрация пользователя |
| `POST` | `/auth/login` | Логин и выдача JWT |
| `POST` | `/auth/logout` | Logout с блокировкой токена |

## Users (`/users`)
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/users/` | Получить список пользователей |
| `GET` | `/users/me` | Профиль текущего пользователя |
| `GET` | `/users/{user_id}` | Получить пользователя по ID |
| `PUT` | `/users/{user_id}` | Обновить профиль пользователя |
| `PATCH` | `/users/{user_id}/role` | Обновить роль |
| `PATCH` | `/users/{user_id}/promote/moderator` | Повысить до модератора |
| `PATCH` | `/users/{user_id}/promote/admin` | Повысить до админа |
| `PATCH` | `/users/{user_id}/demote` | Понизить до студента |
| `DELETE` | `/users/{user_id}` | Удалить пользователя |

## Tasks (`/tasks`)
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/tasks/` | Создать задачу |
| `GET` | `/tasks/` | Получить задачи с фильтрацией |
| `GET` | `/tasks/my_tasks` | Получить свои задачи |
| `GET` | `/tasks/moderation` | Задачи на модерацию |
| `GET` | `/tasks/{task_id}` | Получить задачу по ID |
| `PUT` | `/tasks/{task_id}` | Обновить задачу |
| `PATCH` | `/tasks/{task_id}/approve` | Одобрить задачу |
| `PATCH` | `/tasks/{task_id}/reject` | Отклонить задачу |
| `DELETE` | `/tasks/{task_id}` | Удалить задачу |

## Task History (`/task-history`)
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/task-history/` | Лог попытки решения |
| `GET` | `/task-history/my` | Получить свою историю |
| `GET` | `/task-history/my/by-status` | История по статусу |
| `GET` | `/task-history/my/task/{task_id}` | История по задаче |
| `GET` | `/task-history/my/task/{task_id}/latest` | Последняя попытка |
| `GET` | `/task-history/my/range` | История за период |


## Health (`/health`)
| Метод | Эндпоинт   | Описание                    |
|-------|------------|-----------------------------|
| `GET` | `/health/` | Проверить работоспособность |