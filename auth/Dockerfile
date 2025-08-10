# Dockerfile

FROM python:3.11-slim

# 1. Объявляем аргумент сборки с дефолтным значением 'production'
ARG APP_ENV=production

WORKDIR /app

RUN pip install --upgrade pip

COPY ./auth/pytest.ini .
COPY ./auth/pyproject.toml .
COPY ./auth/main.py .

RUN if [ "$APP_ENV" = "dev" ] ; then \
        pip install .[dev] ; \
    else \
        pip install . ; \
    fi

COPY ./lib/ ./lib/
COPY ./auth/ ./auth/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
