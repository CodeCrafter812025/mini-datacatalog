# Mini DataCatalog

یک سرویس سبک Data Catalog با FastAPI که این قابلیت‌ها را فراهم می‌کند:
- احراز هویت مبتنی بر JWT
- پیش‌نمایش و لود CSV به Postgres
- لاگ آدیت (Database + JSON log) با ریت‌لیمیت و X-Request-ID
- UI سبک HTML/JS برای دمو
- ایمیل دیباگ با MailHog

## پیش‌نیازها
- [Docker Desktop](https://www.docker.com/) (روی ویندوز بهتر است WSL2 فعال باشد)
- Git

## شروع سریع (Quick Start)

```bash
git clone https://github.com/CodeCrafter812025/mini-datacatalog.git
cd mini-datacatalog
