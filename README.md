# FastElectronik

Магазин электроники на FastAPI с использованием PostgreSQL, Redis и JWT аутентификацией.

## Технологии

- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- JWT аутентификация
- Docker
- Docker Compose

## Требования

- Docker
- Docker Compose

## Установка и запуск



1. Создайте файл .env на основе .env.example:
```bash
cp .env.example .env
```

2. Запустите проект с помощью Docker Compose:
```bash
docker-compose up --build
```

адрес: http://localhost:8000

## API Endpoints

### Аутентификация
- POST /register - Регистрация нового пользователя
- POST /token - Получение JWT токена

### Товары (требуется авторизация суперпользователя)
- POST /products/ - Создание нового товара
- DELETE /products/{product_id} - Удаление товара

### Заказы (требуется авторизация)
- POST /orders/ - Создание нового заказа

## Документация API
- Swagger UI: http://localhost:8000/docs