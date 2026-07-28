FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-dev.txt ./

RUN pip wheel --no-cache-dir --wheel-dir /app/wheels-prod -r requirements.txt
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels-all -r requirements-dev.txt

FROM python:3.12-slim AS development

WORKDIR /app

COPY --from=builder /app/wheels-all /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM python:3.12-slim AS production

WORKDIR /app

COPY --from=builder /app/wheels-prod /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
