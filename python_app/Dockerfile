FROM python:3.9-slim-buster
WORKDIR /app
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt
COPY . .
CMD ["python","main_collector.py"]
