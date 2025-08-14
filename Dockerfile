FROM python:3.11-slim

WORKDIR /app

# install curl (برای healthcheck) و پاکسازی کش apt
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# در Dockerfile: (ex)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# (بدون --reload)
