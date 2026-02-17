FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir Flask==3.0.0 Werkzeug==3.0.1 python-dotenv==1.0.0

RUN mkdir -p /app/data /app/templates

EXPOSE 5000

CMD ["python", "app.py"]
