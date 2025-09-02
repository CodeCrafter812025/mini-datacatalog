FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

# مهم: uvicorn ساده، نه uvicorn[standard]
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir uvicorn watchfiles

COPY . .

RUN mkdir -p logs samples

EXPOSE 8000
# در dev از --reload استفاده می‌کنیم (watchfiles نصب شده است)
CMD ["uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
