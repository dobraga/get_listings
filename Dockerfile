FROM python:3.9.10-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    cmake \
    build-essential \
    gcc \
    g++ \
    curl \
    locales \
    locales-all

COPY ./.env /app/.env
COPY ./backend /app/backend
COPY ./dashboard /app/dashboard
COPY ./requirements.txt /app/
COPY ./settings.toml /app/
COPY ./wsgi.py /app/
COPY ./data /app/data

WORKDIR /app
RUN pip install -r requirements.txt --require-hashes

RUN export FLASK_APP=dashboard:create_server
RUN flask db init || flask db migrate || flask db upgrade || true

CMD gunicorn --bind 0.0.0.0:$PORT "wsgi:application" --log-level=info --timeout 0
