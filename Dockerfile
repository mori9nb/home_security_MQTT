# Base image
FROM python:3.10-slim

# ست کردن دایرکتوری کاری در داخل کانتینر
WORKDIR /app

# کپی و نصب وابستگی‌ها
COPY python_app/requirement.txt ./requirement.txt
RUN pip install --no-cache-dir -r requirement.txt

# کپی کل کد پایتون
COPY python_app/ ./python_app
COPY python_app/Subscriber.py ./Subscriber.py
COPY simulate_sensor.py ./simulate_sensor.py

# اگر importها به صورت from python_app.config باشند:
ENV PYTHONPATH="/app/python_app:${PYTHONPATH}"

# پیش‌فرض اجرای Subscriber؛ با docker-compose می‌توانید این CMD را با
# command: ["python", "simulate_sensor.py"]
# برای شبیه‌ساز سنسورها بازنویسی کنید.
CMD ["python", "Subscriber.py"]
