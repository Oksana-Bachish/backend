# Интернет магазин Electronics_store
Это полноценный проект интернет-магазина, разработанный на Django. Выполнен как учебный проект в процессе самообучения. 

### 🔧 Функциональность

- Админ-панель Django
- Кастомная регистрация и личный кабинет пользователя
- Восстановление пароля через email (SMTP Yandex)
- Фильтрация, сортировка и поиск товаров
- Корзина с динамическим обновлением (AJAX)
- Оформление заказов с оплатой через Stripe (тестовая интеграция)
- Перевод на Class-Based Views
- Подключение микросервиса через Django REST Framework.
- Развёртывание в Docker с использованием Nginx
- Деплой на VPS-сервер
- Зарегистрировано доменное имя: `electronics7.ru`
- Подключен SSL-сертификат для HTTPS

### 🛠️ Стек технологий

- Python 3.10  
- Django  
- PostgreSQL  
- Django ORM  
- Django REST Framework  
- Docker + Docker Compose  
- Nginx  
- Stripe API  
- SMTP Yandex  

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
SECRET_KEY=secret_key
POSTGRES_DB=db_name
POSTGRES_PASSWORD=password
POSTGRES_USER=login
POSTGRES_PORT=5432
```

6. Создайте файл `.env.dev` в папке API-микросервиса:
```bash
touch api/.env.dev
```

7. Добавьте в него переменные окружения:
```env
DEBUG=False
SECRET_KEY=secret_key
ALLOWED_HOSTS=localhost 127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8001
POSTGRES_USER=login
POSTGRES_PASSWORD=password
POSTGRES_DB=db_name
POSTGRES_PORT=5432
```

8. Убедитесь, что установлен Docker:
```bash
docker --version
```
Если Docker не установлен — следуйте официальной [инструкции по установке](https://docs.docker.com/).

9. Запустите проект:
```bash
docker compose up
```

10. Откройте сайт в браузере:  
[http://127.0.0.1:8000](http://127.0.0.1:8000)


### 🌐 Деплой проекта

Проект развёрнут на VPS-сервере. Настроено проксирование, а также сервировка статических и медиафайлов через Nginx. Созданы Docker-тома для хранения данных.

**Сайт:** https://electronics7.ru  
**API**: https://electronics7.ru/api/v1/products/

### 👩‍💻 Автор:
*Оксана Бачиш*
