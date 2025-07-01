FROM python:3.12-slim-buster
WORKDIR /app
COPY requirement.txt
RUN pip install --no-cache-dir -r requirement.txt
COPY ../.venv/python_app .
CMD ["python","main_collector.py"]
