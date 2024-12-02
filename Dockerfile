# Dockerfile for Backend
FROM python:3.10-slim
WORKDIR /app

# Встановлення залежностей
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання коду
COPY . .

# Експортуємо порт
EXPOSE 8000

# Запуск міграцій і серверу
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
