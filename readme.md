# Electronics Store

[![CI](https://github.com/Oksana-Bachish/backend/actions/workflows/tests.yml/badge.svg)](https://github.com/Oksana-Bachish/backend/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/oksana-bachish/backend/graph/badge.svg?token=FDA59YE3BN)](https://codecov.io/gh/oksana-bachish/backend)

# Интернет магазин Electronics_store
Это полноценный проект интернет-магазина, разработанный на Django. Выполнен как учебный проект в процессе самообучения. 

### 🔧 Функциональность

- Админ-панель Django
- Кастомная регистрация и личный кабинет пользователя
- **Асинхронное восстановление пароля через email**: интеграция Celery и RabbitMQ для выноса отправки писем (SMTP Yandex) в фоновые задачи без блокировки основного потока приложения.
- **Высокоскоростное кэширование каталога**: интеграция Redis для оптимизации производительности.
- Фильтрация, сортировка и поиск товаров
- Корзина с динамическим обновлением (AJAX)
- Оформление заказов с оплатой через Stripe (тестовая интеграция)
- Перевод на Class-Based Views
- Автоматическое тестирование с покрытием кода (Pytest + Codecov)  
- CI через GitHub Actions
- Подключение микросервиса через Django REST Framework.
- **Интеграция внешнего асинхронного микросервиса рекомендаций товаров**, построенного на FastAPI и PostgreSQL.
- **Интеграция LLM-агента**: асинхронный микросервис на FastAPI для контекстного подбора техники из каталога на базе моделей OpenAI.
- Развёртывание в Docker с использованием Nginx
- Деплой на VPS-сервер
- Зарегистрировано доменное имя: `electronics24.store`
- Подключен SSL-сертификат для HTTPS

### 🛠️ Стек технологий

- Python 3.10 / 3.11 
- Django / FastAPI 
- OpenAI SDK (`AsyncOpenAI`) / Pydantic v2
- PostgreSQL (Asyncpg) /  Redis
- Django ORM  
- Django REST Framework  
- Celery / RabbitMQ 
- Docker + Docker Compose  
- Nginx  
- Stripe API  
- SMTP Yandex  
- Pytest
- GitHub Actions
- Codecov

### 📸 Скриншоты

**Главная страница**  
![Main page](https://github.com/Oksana-Bachish/backend/blob/main/png_for_readme/main.png)

**Панель администратора**  
![Admin panel](https://github.com/Oksana-Bachish/backend/blob/main/png_for_readme/admin_panel.png)

**Личный кабинет пользователя**  
![Profile](https://github.com/Oksana-Bachish/backend/blob/main/png_for_readme/profile.png)

**Фильтры и поиск**  
![Filters](https://github.com/Oksana-Bachish/backend/blob/main/png_for_readme/filters.png)

**Корзина**  
![Basket](https://github.com/Oksana-Bachish/backend/blob/main/png_for_readme/backet.png)

**Оплата через Stripe**  
![Payment](https://github.com/Oksana-Bachish/backend/blob/main/png_for_readme/payment.png)

**Микросервис API**  
![Api](https://github.com/Oksana-Bachish/backend/blob/main/png_for_readme/api.png)


### ⚙️ Установка проекта

Откройте терминал и выполните следующие шаги:

1. Выберите папку, куда будете клонировать Git-репозиторий:
```bash
cd <имя_папки>
```

2. Клонируйте репозиторий:
```bash
git clone https://github.com/Oksana-Bachish/backend.git
```

3. Перейдите в директорию проекта:
```bash
cd backend
```

4. Создайте файл `.env.dev` в папке `electronics_store`:
```bash
touch electronics_store/.env.dev
```
   
5. Добавьте в `.env.dev` следующие переменные:
```env
# Django
SECRET_KEY=your_secret_key

# База данных PostgreSQL
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_PORT=5432

# Stripe (платежная система)
STRIPE_PUBLISHABLE_KEY=your_publishable_key
STRIPE_SECRET_KEY=your_secret_key
STRIPE_API_VERSION=your_api_version
STRIPE_WEBHOOK_SECRET=your_webhook_secret

# Почта для восстановления пароля
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_PORT=587
EMAIL_USE_TLS=True

# Очереди задач Celery и брокер RabbitMQ
RABBITMQ_DEFAULT_USER=your_rabbitmq_user
RABBITMQ_DEFAULT_PASS=your_rabbitmq_password
CELERY_BROKER_URL=amqp://your_rabbitmq_user:your_rabbitmq_password@rabbitmq:5672//

```

6. Создайте файл `.env.dev` в папке API-микросервиса:
```bash
touch api/.env.dev
```

7. Добавьте в него переменные окружения:
```env
# Общие настройки
DEBUG=False
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=localhost 127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8001

# База данных PostgreSQL
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=your_db_name
POSTGRES_PORT=5432
```

8. Убедитесь, что установлен Docker:
```bash
docker --version
```
Если Docker не установлен — следуйте официальной [инструкции по установке](https://docs.docker.com/).

9. Запустите проект в фоновом режиме:
```bash
docker compose up -d --build
```

10. Откройте сайт в браузере:  
- Веб-интерфейс: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
- API: [http://127.0.0.1:9000/api/v1/products/](http://127.0.0.1:9000/api/v1/products/)
    
11. Проект покрыт автоматическими тестами на **Pytest**. Для запуска проверок выполните:
```bash
docker compose exec web pytest
```


### 🌐 Деплой проекта

Проект развёрнут на VPS-сервере. Настроено проксирование, а также сервировка статических и медиафайлов через Nginx. Созданы Docker-тома для хранения данных.

**Сайт:** https://electronics24.store  
**API**: https://electronics24.store/api/v1/products/

### 👩‍💻 Автор:
*Оксана Бачиш*  
https://github.com/Oksana-Bachish?tab=repositories

