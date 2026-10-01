# AutoRia Clone — Car Marketplace API

Навчальний REST API для платформи продажу автомобілів, побудований на **Django REST Framework**.

Проєкт демонструє роботу з:

- Django REST Framework
- JWT-аутентифікацією
- ролями та permissions
- Docker / Docker Compose
- MySQL
- Redis
- Celery та Celery Beat
- фільтрацією та пошуком
- асинхронними задачами
- email-сповіщеннями
- OpenAPI-документацією через DRF-Spectacular
- інтеграцією з PrivatBank API

> **Проєкт створений у навчальних цілях.**

---

# Зміст

- [Стек технологій](#стек-технологій)
- [Архітектура](#архітектура)
- [Запуск проєкту](#запуск-проєкту)
- [База даних](#база-даних)
- [Ролі та доступи](#ролі-та-доступи)
- [Преміум акаунт](#преміум-акаунт)
- [Основні API endpoints](#основні-api-endpoints)
- [Celery Tasks](#celery-tasks)
- [Фільтрація та пошук](#фільтрація-та-пошук)
- [Email сповіщення](#email-сповіщення)
- [Документація API](#документація-api)
- [Тестування через Postman](#тестування-через-postman)
- [Додавання нових ролей і permissions](#додавання-нових-ролей-і-permissions)
- [Docker](#docker)

---

# Стек технологій

## Backend

- **Python 3.12**
- **Django 6**
- **Django REST Framework**
- **MySQL 8.4** — основна база даних
- **Redis** — брокер повідомлень для Celery
- **Celery + Celery Beat** — асинхронні та періодичні задачі
- **Docker / Docker Compose** — контейнеризація

## Автентифікація

- **JWT**
- **djangorestframework-simplejwt**

## Документація API

- **DRF-Spectacular**
- **Swagger UI**
- **ReDoc**

## Інтеграції

- **PrivatBank API** — отримання курсів валют

## Інші бібліотеки

- **django-filter** — фільтрація оголошень
- **Pillow** — робота із зображеннями
- **django-celery-results** — збереження результатів Celery

---

# Архітектура

Проєкт розділений на Django apps відповідно до окремих доменів:

| App | Призначення |
|-----|-------------|
| `users` | користувачі, ролі, permissions, профілі |
| `auth` | реєстрація, логін, JWT |
| `listing` | оголошення та робота з ними |
| `moderation` | модерація оголошень |
| `cars` | бренди та моделі автомобілів |
| `listing_stats` | статистика оголошень |
| `payment` | курси валют та перерахунок цін |
| `core` | спільні permissions, сервіси та інша інфраструктура |

Для фонових задач використовується **Celery**, для брокера повідомлень — **Redis**, а для періодичного запуску задач — **Celery Beat**.

Архітектура ролей побудована через окремі `Role`, `CustomPermission` та зв'язки між ними. Це дозволяє надалі додавати нові ролі та права доступу без прив'язки всієї бізнес-логіки лише до чотирьох початкових ролей.

---

# Запуск проєкту

## 1. Клонування репозиторію

```bash
git clone <repository-url>
cd test_python
```

## 2. Створення `.env`

Створіть файл `.env` у корені проєкту:

```env
MYSQL_USER=autoria
MYSQL_PASSWORD=autoria
MYSQL_DATABASE=autoria
MYSQL_HOST=db
MYSQL_PORT=3306
```

Секретні ключі, паролі та production credentials не повинні зберігатися у Git.

## 3. Запуск Docker

```bash
docker compose up -d --build
```

Docker Compose запускає:

- Django application;
- MySQL 8.4;
- Redis;
- Celery worker;
- Celery Beat.

## 4. Перевірка контейнерів

```bash
docker compose ps
```

Для перегляду логів Django:

```bash
docker compose logs -f app
```

Для Celery:

```bash
docker compose logs -f celery
```

## 5. Міграції

Міграції застосовуються автоматично під час запуску контейнера `app`.

За необхідності:

```bash
docker compose exec app python manage.py migrate
```

## 6. Fixtures

Для чистої бази даних базові fixtures можна завантажити командами:

```bash
docker compose exec app python manage.py loaddata regions.json
docker compose exec app python manage.py loaddata brands.json
docker compose exec app python manage.py loaddata car_models.json
```

`listings.json`, якщо використовується, може залежати від конкретних користувачів, тому його потрібно завантажувати лише після створення відповідних користувачів.

## 7. Створення адміністратора

```bash
docker compose exec app python manage.py createsuperuser
```

---

# База даних

Проєкт використовує **MySQL 8.4**, що запускається як окремий Docker-контейнер.

Всередині Docker Compose Django підключається до:

```text
Host: db
Port: 3306
```

На локальній машині MySQL доступний через:

```text
Port: 3308
```

Дані MySQL зберігаються у Docker volume:

```text
mysql_data
```

Тому звичайний `docker compose down` не видаляє дані бази.

> Не використовуйте `docker compose down -v`, якщо потрібно зберегти локальну базу даних.

---

# Ролі та доступи

| Роль | Можливості |
|------|------------|
| **Buyer** | перегляд оголошень, створення першого оголошення |
| **Seller** | створення, редагування та видалення власних оголошень, робота з фото |
| **Manager** | модерація оголошень, управління користувачами, статистика |
| **Admin** | повний доступ до системи, створення Manager |

Додаткові правила:

- Buyer автоматично може перейти до ролі Seller після створення оголошення.
- Basic-акаунт може мати лише одне активне/очікуюче оголошення.
- Premium-акаунт може створювати декілька оголошень.
- Статистика оголошень доступна Premium-користувачам та адміністративним ролям відповідно до permissions.
- Manager може блокувати та розблоковувати користувачів.
- Тільки Admin може призначити користувачу роль Manager.
- Manager та Admin можуть працювати з оголошеннями, що очікують ручної модерації.

---

# Преміум акаунт

Оплата у навчальній версії реалізована як **mock-функціонал** без підключення реальної платіжної системи.

```http
POST /api/users/me/premium/mock/
```

Ендпоінт активує Premium-акаунт на тестовий період.

Premium надає:

- можливість створювати більше одного оголошення;
- перегляд статистики оголошень;
- кількість переглядів за день, тиждень та місяць;
- середню ціну автомобіля у регіоні;
- середню ціну автомобіля по Україні.

---

# Основні API endpoints

## Auth

| Метод | URL | Опис |
|------|-----|------|
| POST | `/api/auth/register/` | Реєстрація |
| POST | `/api/auth/login/` | Логін |
| POST | `/api/auth/refresh/` | Оновлення JWT |
| POST | `/api/auth/logout/` | Вихід |

## Users

| Метод | URL | Опис | Доступ |
|------|-----|------|--------|
| GET | `/api/users/` | Список користувачів | Admin / Manager |
| GET | `/api/users/me/` | Поточний користувач | Авторизований |
| PATCH | `/api/users/me/update/` | Оновити власний акаунт | Авторизований |
| DELETE | `/api/users/me/delete/` | Видалити власний акаунт | Авторизований |
| POST | `/api/users/me/premium/mock/` | Активувати Premium | Buyer / Seller |
| PATCH | `/api/users/<pk>/block/` | Заблокувати користувача | Admin / Manager |
| PATCH | `/api/users/<pk>/unblock/` | Розблокувати користувача | Admin / Manager |
| PATCH | `/api/users/<pk>/manager/` | Призначити Manager | Admin |

## Listings

| Метод | URL | Опис | Доступ |
|------|-----|------|--------|
| GET | `/api/listings/` | Список активних оголошень | Публічно |
| GET | `/api/listings/<pk>/` | Перегляд оголошення | Публічно |
| GET | `/api/listings/regions/` | Список регіонів | Публічно |
| GET | `/api/listings/my/` | Власні оголошення | Seller |
| POST | `/api/listings/create/` | Створити оголошення | Buyer / Seller |
| PATCH | `/api/listings/update/<pk>/` | Редагувати оголошення | Власник |
| DELETE | `/api/listings/delete/<pk>/` | Зняти оголошення з продажу | Власник |
| POST | `/api/listings/<pk>/photos/` | Завантажити фото | Власник |
| DELETE | `/api/listings/photos/<pk>/` | Видалити фото | Власник |
| POST | `/api/listings/report-problem/<pk>/` | Поскаржитися на оголошення | Авторизований |
| GET | `/api/listings/edit/` | Pending-оголошення | Admin / Manager |
| PATCH | `/api/listings/moderation/<pk>/` | Модерація оголошення | Admin / Manager |
| GET | `/api/listings/statistics/<pk>/` | Статистика оголошення | За permission |

## Cars

| Метод | URL | Опис |
|------|-----|------|
| GET | `/api/cars/brands/` | Список брендів |
| GET | `/api/cars/models/` | Список моделей |
| GET | `/api/cars/brands/<pk>/models/` | Моделі конкретного бренду |
| POST | `/api/cars/request-brand/` | Запит на нову марку |
| POST | `/api/cars/brands/` | Створення бренду |
| POST | `/api/cars/models/` | Створення моделі |

## Payment

| Метод | URL | Опис |
|------|-----|------|
| GET | `/api/payment/rate/` | Поточний курс валют |

---

# Модерація оголошень

Після створення або редагування оголошення запускається асинхронна перевірка тексту.

Основний процес:

1. оголошення створюється зі статусом `pending`;
2. Celery запускає задачу модерації;
3. текст перевіряється на заборонені слова;
4. чисте оголошення отримує статус `active`;
5. проблемне оголошення отримує статус `rejected`;
6. користувач може виправити оголошення;
7. після вичерпання дозволених спроб оголошення переводиться в `inactive`, а менеджеру надсилається повідомлення.

Manager/Admin також можуть працювати з pending-оголошеннями через окремий endpoint модерації.

---

# Курси валют

Оголошення підтримують:

- USD;
- EUR;
- UAH.

Система зберігає початкову валюту та початкову ціну оголошення.

Курси отримуються через **PrivatBank API**, після чого система розраховує ціни в інших підтримуваних валютах.

---

# Celery Tasks

| Task | Запуск | Опис |
|------|--------|------|
| `fetch_currency_rates_task` | щодня о 09:00 | Отримання курсів валют |
| `update_listings_prices_task` | після оновлення курсів | Перерахунок цін |
| `moderation_listings_task` | при створенні / редагуванні | Модерація оголошення |
| `send_blocked_listing_email_task` | при блокуванні оголошення | Email менеджеру |

Для ручного запуску оновлення курсів:

```bash
docker compose exec celery celery -A config call apps.payment.tasks.fetch_currency_rates_task
```

---

# Фільтрація та пошук

Основний endpoint:

```text
/api/listings/
```

Підтримує фільтрацію, пошук та сортування.

Приклади:

```text
?body_type=suv
?fuel_type=electric
?region=1
?condition_type=new
?price_usd_min=10000&price_usd_max=30000
?mileage_max=50000
?year_min=2019
?search=BMW
?ordering=price_usd
?ordering=-created_at
```

Параметри можна комбінувати:

```text
/api/listings/?fuel_type=electric&year_min=2020&price_usd_max=30000
```

---

# Email сповіщення

У поточній локальній конфігурації для розробки використовується:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Тому email-повідомлення виводяться у логи контейнера замість відправлення на реальну поштову адресу.

Система підтримує службові повідомлення:

- після блокування оголошення;
- при скарзі на оголошення;
- при запиті на додавання нової марки/моделі.

Для production можна налаштувати SMTP через змінні середовища.

---

# Документація API

Після запуску проєкту:

| Інтерфейс | URL |
|-----------|-----|
| Swagger UI | `http://localhost:8000/api/docs/` |
| ReDoc | `http://localhost:8000/api/redoc/` |
| OpenAPI schema | `http://localhost:8000/api/schema/` |

Swagger UI дозволяє переглядати endpoints, параметри, схеми запитів/відповідей та виконувати API-запити.

---

# Тестування через Postman

Для проєкту передбачена Postman Collection.

Рекомендовані Environment variables:

| Variable | Значення |
|----------|----------|
| `host` | `http://localhost:8000` |
| `access` | JWT access token |
| `refresh` | JWT refresh token |

Колекція повинна охоплювати основні сценарії Auth, Users, Cars, Listings, Statistics та Payment.

---

# Додавання нових ролей і permissions

Ролі та permissions є окремою частиною архітектури.

Для додавання нового permission можна створити data migration:

```bash
docker compose exec app python manage.py makemigrations users --empty --name add_new_permission
```

Після опису permission у міграції:

```bash
docker compose exec app python manage.py migrate
```

Такий підхід дозволяє надалі розширювати систему ролями для дилерських центрів, менеджерів, продавців, механіків та інших типів співробітників.

---

# Docker

Проєкт складається з п'яти основних сервісів:

```text
app
db
redis
celery
celery_beat
```

## Запуск

```bash
docker compose up -d --build
```

## Статус

```bash
docker compose ps
```

## Логи Django

```bash
docker compose logs -f app
```

## Логи Celery

```bash
docker compose logs -f celery
```

## Логи всіх сервісів

```bash
docker compose logs -f
```

## Перезапуск Django

```bash
docker compose restart app
```

## Зупинка

```bash
docker compose down
```

---

# Перевірка роботи

Після запуску:

```bash
curl http://localhost:8000/api/listings/
```

Swagger UI:

```text
http://localhost:8000/api/docs/
```

ReDoc:

```text
http://localhost:8000/api/redoc/
```

---

# Подальше розгортання

Проєкт контейнеризований, тому його можна адаптувати для розгортання у хмарній інфраструктурі.

Для AWS production-середовища логічне розділення компонентів:

- Django API — контейнерний сервіс;
- MySQL — керована база даних;
- Redis — керований Redis-сервіс;
- Celery worker — окремий контейнер;
- Celery Beat — окремий контейнер;
- media/static — об'єктне сховище;
- secrets — змінні середовища / secret storage.

Це дозволяє масштабувати API та фонові worker-и незалежно один від одного.

---

# AWS Deployment

Проєкт спроєктований з можливістю подальшого розгортання та масштабування в AWS.

Завдяки контейнеризації окремі компоненти системи можуть запускатися та масштабуватися незалежно.

## Архітектура AWS

```text
                    Internet
                       |
                       v
              Application Load Balancer
                       |
                       v
                 Django REST API
                  (ECS / Fargate)
                  /     |      \
                 /      |       \
                v       v        v
             RDS    ElastiCache   S3
            MySQL      Redis     Media
                       |
                  +----+----+
                  |         |
                  v         v
               Celery    Celery Beat
               Worker
```

### Application Load Balancer

Приймає HTTP/HTTPS-запити користувачів та розподіляє навантаження між контейнерами Django API.

### Amazon ECS / AWS Fargate

Docker-контейнери Django можуть бути запущені через Amazon ECS з AWS Fargate.

Це дозволяє запускати декілька екземплярів API та масштабувати їх залежно від навантаження.

Celery Worker та Celery Beat також можуть запускатися як окремі контейнерні сервіси.

### Amazon RDS

У production локальний контейнер MySQL може бути замінений на Amazon RDS for MySQL.

RDS відповідає за постійне зберігання:

- користувачів;
- автомобілів;
- оголошень;
- ролей та permissions;
- статистики;
- курсів валют;
- результатів модерації.

### Amazon ElastiCache

Redis використовується як broker для Celery.

У AWS локальний Redis-контейнер може бути замінений на Amazon ElastiCache for Redis.

### Amazon S3

Amazon S3 може використовуватися для зберігання фотографій автомобілів та інших media-файлів.

Це дозволяє не зберігати завантажені користувачами файли безпосередньо всередині контейнерів Django.

## Масштабування

Архітектура дозволяє незалежно масштабувати:

- Django REST API;
- Celery Workers;
- MySQL;
- Redis;
- файлове сховище.

Наприклад, при збільшенні кількості користувачів можна запустити декілька контейнерів Django API за Application Load Balancer та окремо збільшити кількість Celery Workers.

Таким чином архітектура підготовлена до збільшення навантаження та подальшого розширення функціональності платформи.

# Ліцензія

Цей проєкт створений у навчальних цілях.
