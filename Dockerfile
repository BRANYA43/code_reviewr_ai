FROM python:3.12-slim

RUN apt-get update; \
    apt-get install -y --no-install-recommends build-essential libpq-dev gcc curl; \
    rm -rf /var/lib/apt/lists/*; \
    python -m venv /opt/.venv

ENV PATH="/opt/venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /opt/src/

COPY pyproject.toml .

RUN pip install --upgrade pip; \
    pip install poetry; \
    poetry config virtualenvs.create false; \
    poetry install

COPY src/ .
