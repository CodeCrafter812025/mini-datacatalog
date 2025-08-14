Set-Content -Path ".\README.md" -Value "# 📊 Mini Data Catalog

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![Docker](https://img.shields.io/badge/Docker-latest-blue.svg)

**یک کاتالوگ داده‌های مینی‌مال با قابلیت‌های ETL و مدیریت متادیتا**

[🔗 View Demo](#) • [📝 Report Bug](#) • [🚀 Request Feature](#)

</div>

## 📋 فهرست مطالب

- [درباره پروژه](#-درباره-پروژه)
- [ویژگی‌ها](#-ویژگیها)
- [نصب و راه‌اندازی](#-نصب-و-راهاندازی)
- [استفاده](#-استفاده)
- [نقشه راه](#-نقشه-راه)
- [مشارکت](#-مشارکت)
- [لایسنس](#-لایسنس)
- [تماس](#-تماس)

## 📖 درباره پروژه

**Mini Data Catalog** یک پروژه متن‌باز برای مدیریت کاتالوگ داده‌ها با قابلیت‌های زیر است:

- مدیریت منابع داده (Data Sources)
- ذخیره‌سازی متادیتای جداول
- پردازش فایل‌های CSV و استخراج اطلاعات
- رابط کاربری REST API با استفاده از FastAPI
- پشتیبانی از Docker برای استقرار آسان

این پروژه به عنوان یک نمونه آموزشی برای پیاده‌سازی سیستم‌های مدیریت داده‌ها طراحی شده است.

## ✨ ویژگی‌ها

- 🚀 **سریع و سبک**: ساخته شده با FastAPI و PostgreSQL
- 🐳 **پشتیبانی از Docker**: استقرار آسان با استفاده از Docker Compose
- 📊 **مدیریت متادیتا**: ذخیره‌سازی و بازیابی اطلاعات جداول
- 🔍 **جستجوی پیشرفته**: قابلیت جستجو در منابع داده و متادیتا
- 📤 **آپلود فایل**: پشتیبانی از آپلود فایل‌های CSV برای پردازش ETL
- 🔄 **مایگریشن‌ها**: مدیریت تغییرات ساختار دیتابیس با فایل‌های SQL

## 🛠️ نصب و راه‌اندازی

### پیش‌نیازها

- [Python 3.11+](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### نصب با Docker (روش پیشنهادی)

1. کلون کردن ریپازیتوری:
   ```bash
   git clone https://github.com/CodeCrafter812025/mini-datacatalog.git
   cd mini-datacatalog