# Mini Data Catalog

یک سیستم مدیریت کاتالوگ داده مبتنی بر FastAPI و PostgreSQL

## ویژگی‌ها

- مدیریت منابع داده (CSV/Dump)
- مدیریت متادیتای جداول
- مدیریت فرآیندهای ETL
- احراز هویت مبتنی بر JWT
- پشتیبانی از Docker
- API مستند با Swagger

## نصب و راه‌اندازی

### پیش‌نیازها
- Docker
- Docker Compose

### مراحل نصب
1. کلون کردن ریپازیتوری:
   \\\ash
   git clone https://github.com/CodeCrafter812025/mini-datacatalog.git
   cd mini-datacatalog
   \\\

2. اجرای پروژه:
   \\\ash
   docker compose up --build -d
   \\\

3. دسترسی به برنامه:
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - MailHog: http://localhost:8025

## استفاده از API

### احراز هویت
برای استفاده از API‌های محافظت شده، ابتدا توکن دریافت کنید:
\\\ash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
\\\

### Endpoints اصلی

#### مدیریت منابع داده
- \GET /meta/datasources\ - دریافت لیست منابع داده
- \POST /meta/datasources\ - ایجاد منبع داده جدید
- \POST /meta/datasources/upload\ - آپلود فایل منبع داده

#### مدیریت متادیتا
- \GET /meta/tables\ - دریافت لیست جداول
- \POST /meta/tables\ - ایجاد متادیتای جدول جدید

#### مدیریت ETL
- \GET /etl/names\ - دریافت لیست فرآیندهای ETL
- \GET /etl/{name}/tables\ - دریافت جداول مرتبط با ETL
- \POST /etl/{name}/execute\ - اجرای فرآیند ETL

#### مدیریت اتصال دیتابیس
- \POST /db/connections\ - ایجاد اتصال دیتابیس جدید
- \GET /db/connections\ - دریافت لیست اتصالات دیتابیس

## ساختار پروژه

\\\
mini-datacatalog/
├── app/
│   ├── __init__.py
│   ├── main.py              # نقطه ورود FastAPI
│   ├── models.py            # مدل‌های SQLAlchemy
│   ├── database.py          # تنظیمات دیتابیس
│   ├── auth.py              # منطق احراز هویت
│   └── routers/
│       ├── auth.py          # روتر احراز هویت
│       ├── meta.py          # روتر متادیتا
│       ├── etl.py           # روتر ETL
│       └── database.py      # روتر اتصال دیتابیس
├── data/
│   └── etl_names.csv        # لیست فرآیندهای ETL
├── docker-compose.yml       # پیکربندی داکر
├── Dockerfile              # دستورالعمل‌های ساخت ایمیج
├── requirements.txt        # وابستگی‌های پایتون
└── README.md              # مستندات
\\\

## تست

برای تست API‌ها می‌توانید از:
- Swagger UI: http://localhost:8000/docs
- فایل Postman collection: \Mini Data Catalog API.postman_collection.json\

## توسعه

### افزودن منبع داده جدید
\\\ash
curl -X POST "http://localhost:8000/meta/datasources" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Data Source",
    "path": "/path/to/data",
    "etl_name": "etl1"
  }'
\\\

### ایجاد متادیتای جدول
\\\ash
curl -X POST "http://localhost:8000/meta/tables" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "schema_name": "public",
    "table_name": "users",
    "description": "User information table",
    "source_id": 1
  }'
\\\

## مجوز

این پروژه تحت مجوز MIT منتشر شده است.
