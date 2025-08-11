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
- [ ] Сделать API. 75% Сделано

### База данных:
- [x] Подключена через Tortoise ORM ✅ 2025-07-28
- [x] Сделать миграцию в SQLAlchemy? ✅ 2025-07-28
- [x] Сделать миграцию в PostgresSQL? - потом, sqlite пойдет ✅ 2025-07-28
- [x] Продуманная структура моделей ✅ 2025-07-30
- [x] Инициализация, миграция ✅ 2025-07-30
- [x] Связи между таблицами ✅ 2025-07-30
- [ ] Начальные фикстуры (админ-пользователь)

### Мониторинг и метрики:
- [x] Sentry - отслеживание ошибок ✅ 2025-07-28
- [x] Prometheus - метрики ✅ 2025-07-28
- [x] Логирование (stdout + ротация логов)
- [ ] Healthcheck (/health, /readiness, /liveness)

### Документация:
- [x] Swagger/OpenAPI ✅ 2025-07-28
- [ ] ReDoc
- [ ] README.md документация
- [ ] Автоматическая генерация client SDK (openapi-generator)

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
- [ ] API-тесты ✅ 2025-08-10
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
DATABASE_URL=sqlite+aiosqlite:///./test.db
SECRET_KEY=supersecret
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
REDIS_URL=redis://localhost:6379
```

### Установка зависимостей

Poetry:
```bash
poetry install
```



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

## 🐳 Запуск через Docker

### 1. Сборка контейнера
```bash
docker build -t fastapi-app .
```
### Запуск контейнера
```bash
docker compose up --build
```

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
