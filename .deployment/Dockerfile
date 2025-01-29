# FROM python:3.13.1-slim-bullseye as base

# ENV PYTHONUNBUFFERED 1
# ENV PYTHONDONTWRITEBYTECODE 1
# WORKDIR /app

# # Install packages
# RUN apt-get -y update \
#     && apt-get install -y --no-install-recommends \
#     build-essential \
#     libpq-dev curl \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# # Install and configure poetry
# RUN curl -sSL https://install.python-poetry.org | python3 -
# ENV PATH="/root/.local/bin:$PATH"
# RUN poetry config virtualenvs.create false

# # Install project packages
# COPY poetry.lock pyproject.toml ./
# RUN poetry install --no-root

# COPY . /app


FROM python:3.13.1-alpine as builder

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    build-base \
    postgresql-dev \
    curl

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
RUN poetry config virtualenvs.create false

# Install Python dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root

COPY . /app

# Final stage: Use a minimal Alpine image
FROM python:3.13.1-alpine

WORKDIR /app
COPY --from=builder /app /app
COPY --from=builder /root/.local /root/.local
ENV PATH="/root/.local/bin:$PATH"
