FROM python:3.11-slim

WORKDIR /app

# نصب وابستگی‌های سیستمی
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

# کپی و نصب وابستگی‌های پایتون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی فایل‌های پروژه
COPY . .

# ایجاد دایرکتوری برای لاگ‌ها
RUN mkdir -p logs

# افشای پورت
EXPOSE 5000

# دستور اجرای برنامه
CMD ["python", "run.py"]
