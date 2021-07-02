FROM python:3.8-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    cmake \
    build-essential \
    gcc \
    g++ \
    curl

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD gunicorn --bind 0.0.0.0:$PORT wsgi -t 900
