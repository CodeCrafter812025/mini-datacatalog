# Mini Data Catalog - پروژه کامل

## وضعیت فعلی
✅ سیستم مدیریت کاتالوگ داده با موفقیت پیاده‌سازی شده است
✅ تمام کانتینرها در حال اجرا و سالم هستند
✅ API endpoints اصلی در دسترس هستند

## ویژگی‌های پیاده‌سازی شده

### 1. مدیریت منابع داده
- ثبت مسیر فایل‌های CSV/Dump
- پشتیبانی از آپلود فایل
- ارتباط با فرآیندهای ETL

### 2. مدیریت متادیتا
- ذخیره schema و table name
- ذخیره توضیحات جداول
- ایجاد روابط بین جداول

### 3. مدیریت ETL
- نمایش لیست فرآیندهای ETL
- نمایش جداول مرتبط با هر ETL
- اجرای فرآیندهای ETL

### 4. مدیریت اتصالات دیتابیس
- ثبت اتصالات به دیتابیس‌های خارجی
- پشتیبانی از PostgreSQL

### 5. احراز هویت
- سیستم مبتنی بر JWT
- کاربران ثبت شده در دیتابیس

## نحوه استفاده

### دریافت توکن
\\\ash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
\\\

### استفاده از API
\\\ash
# دریافت منابع داده
curl -H "Authorization: Bearer YOUR_TOKEN" "http://localhost:8000/meta/datasources"

# دریافت نام‌های ETL
curl -H "Authorization: Bearer YOUR_TOKEN" "http://localhost:8000/etl/names"

# دریافت جداول یک ETL
curl -H "Authorization: Bearer YOUR_TOKEN" "http://localhost:8000/etl/etl1/tables"

# ایجاد اتصال دیتابیس
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test DB","host":"localhost","port":5432,"username":"admin","password":"admin123","database_name":"testdb","connection_type":"postgresql"}' \
  "http://localhost:8000/db/connections"
\\\

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
├── init.sql               # اسکریپت مقداردهی اولیه دیتابیس
├── create-db.sh           # اسکریپت ایجاد دیتابیس
├── create-tables.sh       # اسکریپت ایجاد جداول
└── README.md              # مستندات
\\\

## دسترسی به سیستم
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- MailHog: http://localhost:8000/8025

## توسعه‌های آینده
- افزودن پشتیبانی از انواع دیگر دیتابیس (MySQL, SQLite)
- افزودن قابلیت زمان‌بندی اجرای فرآیندهای ETL
- افزودن رابط کاربری وب
- افزودن قابلیت گزارش‌گیری
