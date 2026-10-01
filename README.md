# AutoRia Clone — Car Marketplace API

Навчальний REST API для платформи продажу автомобілів, розроблений на
**Django REST Framework**.

Проєкт реалізує реєстрацію та JWT-аутентифікацію, систему ролей і
permissions, створення та модерацію оголошень, Basic/Premium акаунти,
статистику, конвертацію валют, фонові задачі Celery та роботу з хмарною
MySQL базою даних.

> Проєкт створений у навчальних цілях.

------------------------------------------------------------------------

## Зміст

- [Стек технологій](#стек-технологій)
- [Архітектура](#архітектура)
- [Запуск проєкту](#запуск-проєкту)
- [Railway Cloud MySQL](#railway-cloud-mysql)
- [Fixtures та mock data](#fixtures-та-mock-data)
- [Ролі та permissions](#ролі-та-permissions)
- [Basic та Premium](#basic-та-premium)
- [Модерація](#модерація)
- [Курси валют](#курси-валют)
- [Celery](#celery)
- [API endpoints](#api-endpoints)
- [Фільтрація та пошук](#фільтрація-та-пошук)
- [API документація](#api-документація)
- [Postman Collection](#postman-collection)
- [Email](#email)
- [Docker](#docker)
- [Перевірка після клонування](#перевірка-після-клонування)
- [AWS / масштабування](#aws--масштабування)
- [Безпека](#безпека)

------------------------------------------------------------------------

## Стек технологій

### Backend

- **Python 3.12**
- **Django 6**
- **Django REST Framework**
- **Railway MySQL** — хмарна база даних
- **Redis** — broker для Celery
- **Celery**
- **Celery Beat**
- **Docker / Docker Compose**

### Authentication

- **JWT**
- **djangorestframework-simplejwt**

### API та інші бібліотеки

- **DRF-Spectacular** — OpenAPI / Swagger / ReDoc
- **django-filter** — фільтрація
- **django-celery-results** — результати Celery
- **Pillow** — робота із зображеннями
- **PrivatBank API** — отримання курсів валют

------------------------------------------------------------------------

## Архітектура

Проєкт розділений на окремі Django apps:

| App             | Призначення                                    |
|-----------------|------------------------------------------------|
| `users`         | користувачі, профілі, ролі та permissions      |
| `auth`          | реєстрація, login та JWT                       |
| `listing`       | оголошення та фотографії                       |
| `moderation`    | автоматична та ручна модерація                 |
| `cars`          | марки та моделі автомобілів                    |
| `listing_stats` | статистика оголошень                           |
| `payment`       | курси валют та перерахунок цін                 |
| `core`          | спільні permissions, сервіси та інфраструктура |

Для фонових задач використовується **Celery**, broker — **Redis**, а
періодичні задачі запускаються через **Celery Beat**.

Фінальна Docker-конфігурація містить чотири сервіси:

``` text
app
redis
celery
celery_beat
```

MySQL не запускається локальним Docker-контейнером. Проєкт використовує
**Railway Cloud MySQL**.

------------------------------------------------------------------------

# Запуск проєкту

## 1. Клонування репозиторію

``` bash
git clone https://github.com/VladTsiusmak/test_python.git
cd test_python
```

Основна гілка:

``` text
main
```

## 2. Створення `.env`

У корені проєкту знаходиться `.env.example`.

Створіть `.env` на його основі.

### Git Bash / Linux / macOS

``` bash
cp .env.example .env
```

### Windows PowerShell

``` powershell
Copy-Item .env.example .env
```

Заповніть `.env`:

``` env
# Railway MySQL
MYSQL_USER=root
MYSQL_PASSWORD=<RAILWAY_MYSQL_PASSWORD>
MYSQL_DATABASE=railway
MYSQL_HOST=<RAILWAY_PUBLIC_HOST>
MYSQL_PORT=<RAILWAY_PUBLIC_PORT>

# Email
EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_PORT=2525
MANAGERS_EMAIL=
```

Параметри підключення до MySQL беруться з Railway:

``` text
MySQL -> Connect -> Public Network
```

Railway connection string має формат:

``` text
mysql://USER:PASSWORD@HOST:PORT/DATABASE
```

> Реальні паролі та production credentials не повинні зберігатися у Git.
> Файл `.env` знаходиться у `.gitignore`.

## 3. Запуск Docker

``` bash
docker compose up -d --build
```

Після запуску перевірте контейнери:

``` bash
docker compose ps
```

Очікуються сервіси:

``` text
app           Up
redis         Up
celery        Up
celery_beat   Up
```

## 4. Django check

``` bash
docker compose exec app python manage.py check
```

Очікуваний результат:

``` text
System check identified no issues (0 silenced).
```

## 5. Міграції

Міграції запускаються автоматично під час старту контейнера `app`.

Перевірити їх можна командою:

``` bash
docker compose exec app python manage.py showmigrations
```

За необхідності запустити вручну:

``` bash
docker compose exec app python manage.py migrate
```

Не запускайте ручний `migrate` одночасно з першим стартом контейнера
`app`, оскільки контейнер уже виконує migrations автоматично.

## 6. Створення адміністратора

За необхідності:

``` bash
docker compose exec app python manage.py createsuperuser
```

------------------------------------------------------------------------

# Railway Cloud MySQL

Фінальна версія проєкту використовує **MySQL у Railway Cloud**.

Django отримує параметри підключення через environment variables:

``` text
MYSQL_USER
MYSQL_PASSWORD
MYSQL_DATABASE
MYSQL_HOST
MYSQL_PORT
```

Локальний MySQL-контейнер у фінальному `docker-compose.yml` відсутній.

Після запуску migrations у Railway створюються таблиці Django та
застосунку, зокрема:

``` text
user
profile
role
role_permissions
custom_permission
cars_brand
car_model
car_images
listing
listing_stats
listing_moderation
region
currency_rate
django_migrations
django_celery_results_*
token_blacklist_*
```

Data migration:

``` text
users.0002_seed_roles_and_permissions
```

створює базові ролі та permissions.

------------------------------------------------------------------------

# Fixtures та mock data

У проєкті передбачені fixtures для тестових даних.

Основні fixtures:

``` text
regions.json
brands.json
car_models.json
listings.json
```

Для чистої бази базові довідники можна завантажити командами:

``` bash
docker compose exec app python manage.py loaddata regions.json
docker compose exec app python manage.py loaddata brands.json
docker compose exec app python manage.py loaddata car_models.json
```

`listings.json` може залежати від конкретних користувачів, тому його
потрібно завантажувати лише після створення відповідних користувачів.

Premium-оплата у навчальній версії також реалізована як **mock**, без
реальної платіжної системи.

------------------------------------------------------------------------

# Ролі та permissions

У системі передбачені ролі:

| Роль        | Основні можливості                                    |
|-------------|-------------------------------------------------------|
| **Buyer**   | перегляд оголошень та створення першого оголошення    |
| **Seller**  | створення, редагування та видалення власних оголошень |
| **Manager** | модерація та управління користувачами                 |
| **Admin**   | повний адміністративний доступ та призначення Manager |

Основні правила:

- Buyer може перейти до Seller після створення оголошення.
- Basic Seller може мати лише одне активне/очікуюче оголошення.
- Premium Seller може створювати декілька оголошень.
- Manager може блокувати та розблоковувати користувачів.
- Тільки Admin може призначити користувачу роль Manager.
- Manager та Admin можуть працювати з оголошеннями, які потребують
  ручної модерації.
- Ролі та permissions винесені в окремі моделі, що дозволяє розширювати
  систему новими ролями.

------------------------------------------------------------------------

# Basic та Premium

За замовчуванням Seller має Basic-акаунт.

Для навчального тестування Premium використовується mock endpoint:

``` http
POST /api/users/me/premium/mock/
```

Premium надає:

- можливість створювати більше одного оголошення;
- загальну кількість переглядів;
- статистику за день;
- статистику за тиждень;
- статистику за місяць;
- середню ціну автомобіля у регіоні;
- середню ціну автомобіля по Україні.

------------------------------------------------------------------------

# Модерація

Після створення або редагування оголошення запускається асинхронна
перевірка.

Основний flow:

1.  оголошення створюється;
2.  запускається Celery moderation task;
3.  текст перевіряється на заборонені слова;
4.  коректне оголошення переходить у `active`;
5.  проблемне оголошення переходить у `rejected`;
6.  Seller може виправити оголошення;
7.  після вичерпання дозволених спроб оголошення переходить у
    `inactive`;
8.  Manager отримує службове повідомлення.

Manager/Admin також можуть виконувати ручну модерацію.

------------------------------------------------------------------------

# Курси валют

Підтримуються:

``` text
USD
EUR
UAH
```

Система зберігає:

- початкову ціну;
- початкову валюту;
- курс валют;
- конвертовані ціни.

Курси отримуються через **PrivatBank API** та зберігаються у БД.

Після оновлення курсу Celery запускає перерахунок цін оголошень.

------------------------------------------------------------------------

# Celery

Основні фонові задачі:

| Task                              | Призначення               |
|-----------------------------------|---------------------------|
| `fetch_currency_rates_task`       | отримання курсів валют    |
| `update_listings_prices_task`     | перерахунок цін оголошень |
| `moderation_listings_task`        | автоматична модерація     |
| `send_blocked_listing_email_task` | email при блокуванні      |

Celery Beat запускає оновлення курсів щодня о **09:00**.

Логи worker:

``` bash
docker compose logs -f celery
```

Логи Beat:

``` bash
docker compose logs -f celery_beat
```

------------------------------------------------------------------------

# API endpoints

## Auth

| Method | URL                   | Опис          |
|--------|-----------------------|---------------|
| POST   | `/api/auth/register/` | реєстрація    |
| POST   | `/api/auth/login/`    | login         |
| POST   | `/api/auth/refresh/`  | оновлення JWT |
| POST   | `/api/auth/logout/`   | logout        |

## Users

| Method | URL                           | Опис                       |
|--------|-------------------------------|----------------------------|
| GET    | `/api/users/`                 | список користувачів        |
| GET    | `/api/users/me/`              | поточний користувач        |
| PATCH  | `/api/users/me/update/`       | оновлення власного акаунта |
| DELETE | `/api/users/me/delete/`       | видалення власного акаунта |
| POST   | `/api/users/me/premium/mock/` | mock Premium               |
| PATCH  | `/api/users/<pk>/block/`      | блокування користувача     |
| PATCH  | `/api/users/<pk>/unblock/`    | розблокування користувача  |
| PATCH  | `/api/users/<pk>/manager/`    | призначення Manager        |

## Cars

| Method | URL                             | Опис                    |
|--------|---------------------------------|-------------------------|
| GET    | `/api/cars/brands/`             | список марок            |
| GET    | `/api/cars/models/`             | список моделей          |
| GET    | `/api/cars/brands/<pk>/models/` | моделі конкретної марки |
| POST   | `/api/cars/request-brand/`      | запит на нову марку     |
| POST   | `/api/cars/brands/`             | створення марки         |
| POST   | `/api/cars/models/`             | створення моделі        |

## Listings

| Method | URL                                  | Опис                 |
|--------|--------------------------------------|----------------------|
| GET    | `/api/listings/`                     | активні оголошення   |
| GET    | `/api/listings/<pk>/`                | деталі оголошення    |
| GET    | `/api/listings/regions/`             | регіони              |
| GET    | `/api/listings/my/`                  | власні оголошення    |
| POST   | `/api/listings/create/`              | створення оголошення |
| PATCH  | `/api/listings/update/<pk>/`         | редагування          |
| DELETE | `/api/listings/delete/<pk>/`         | зняття з продажу     |
| POST   | `/api/listings/<pk>/photos/`         | додавання фото       |
| DELETE | `/api/listings/photos/<pk>/`         | видалення фото       |
| POST   | `/api/listings/report-problem/<pk>/` | скарга               |
| GET    | `/api/listings/edit/`                | pending listings     |
| PATCH  | `/api/listings/moderation/<pk>/`     | ручна модерація      |
| GET    | `/api/listings/statistics/<pk>/`     | статистика           |

## Payment

| Method | URL                  | Опис                |
|--------|----------------------|---------------------|
| GET    | `/api/payment/rate/` | поточні курси валют |

------------------------------------------------------------------------

# Фільтрація та пошук

Основний endpoint:

``` text
/api/listings/
```

Приклади:

``` text
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

``` text
/api/listings/?fuel_type=electric&year_min=2020&price_usd_max=30000
```

------------------------------------------------------------------------

# API документація

Після запуску доступні:

| Інтерфейс      | URL                                 |
|----------------|-------------------------------------|
| Swagger UI     | `http://localhost:8000/api/docs/`   |
| ReDoc          | `http://localhost:8000/api/redoc/`  |
| OpenAPI schema | `http://localhost:8000/api/schema/` |

Swagger дозволяє переглядати endpoints, параметри та схеми
запитів/відповідей.

------------------------------------------------------------------------

# Postman Collection

У репозиторії знаходиться готова Postman Collection:

``` text
postman/AutoRia Clone API.postman_collection.json
```

Рекомендований flow перевірки:

``` text
1. Auth — Register / Login
2. Users — Profile / Roles / Premium
3. Cars — Brands / Models
4. Listings — Create / Read / Update / Photos
5. Moderation
6. Statistics
7. Payment
```

Основна змінна:

``` text
host = http://localhost:8000
```

JWT access/refresh tokens отримуються через Auth flow та
використовуються для авторизованих запитів.

------------------------------------------------------------------------

# Email

Для development можна використовувати Django console email backend.

У такому випадку email-повідомлення виводяться у logs замість реальної
відправки.

Логи Django:

``` bash
docker compose logs -f app
```

Логи Celery:

``` bash
docker compose logs -f celery
```

------------------------------------------------------------------------

# Docker

## Запуск

``` bash
docker compose up -d --build
```

## Статус

``` bash
docker compose ps
```

## Django check

``` bash
docker compose exec app python manage.py check
```

## Міграції

``` bash
docker compose exec app python manage.py migrate
```

## Логи Django

``` bash
docker compose logs -f app
```

## Логи Celery

``` bash
docker compose logs -f celery
```

## Усі логи

``` bash
docker compose logs -f
```

## Перезапуск

``` bash
docker compose restart app
```

## Зупинка

``` bash
docker compose down
```

------------------------------------------------------------------------

# Перевірка після клонування

Для перевірки проєкту з чистого середовища:

``` bash
git clone https://github.com/VladTsiusmak/test_python.git
cd test_python
cp .env.example .env
```

Заповніть Railway credentials у `.env`, після чого:

``` bash
docker compose up -d --build
docker compose ps
docker compose exec app python manage.py check
docker compose exec app python manage.py showmigrations
```

Очікуваний результат:

``` text
app           Up
redis         Up
celery        Up
celery_beat   Up
```

та:

``` text
System check identified no issues (0 silenced).
```

Swagger:

``` text
http://localhost:8000/api/docs/
```

------------------------------------------------------------------------

# AWS / масштабування

Поточна база даних винесена у Railway Cloud.

Для production-середовища проєкт можна перенести в AWS за такою схемою:

``` text
Internet
   |
Application Load Balancer
   |
Django REST API (ECS / Fargate)
   |
   +---- RDS MySQL
   +---- ElastiCache Redis
   +---- S3 Media

Celery Worker (ECS / Fargate)
Celery Beat   (ECS / Fargate)
```

Компоненти можна масштабувати незалежно:

- Django API;
- Celery workers;
- Redis;
- MySQL;
- media/static storage.

------------------------------------------------------------------------

# Безпека

- `.env` не комітиться у Git;
- Railway password не зберігається у README;
- `.env.example` містить лише шаблон;
- production credentials передаються через environment variables;
- JWT використовується для авторизації API.

------------------------------------------------------------------------

# Ліцензія

Проєкт створений у навчальних цілях.
