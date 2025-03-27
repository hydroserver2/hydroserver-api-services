FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .

EXPOSE 8000

ENV WORKERS=3

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:8000 --workers ${WORKERS} hydroserver.wsgi:application"]