FROM python:3.8-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    cmake \
    build-essential \
    gcc \
    g++ \
    curl

COPY ./listings /app/listings
COPY ./requirements.txt /app/
COPY ./production.env /app/
COPY ./settings.toml /app/

WORKDIR /app
RUN pip install -r requirements.txt --require-hashes

RUN flask db init || flask db migrate || flask db upgrade || true

CMD gunicorn --bind 0.0.0.0:$PORT "listings:create_app()" --log-level=info --timeout 0
