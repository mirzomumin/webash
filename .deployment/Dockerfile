FROM python:3.13.1-slim-bullseye as base

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install packages
RUN apt-get -y update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install and configure poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
RUN poetry config virtualenvs.create false


FROM base AS builder
# Install project packages
WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root


FROM base AS production

WORKDIR /app

# Copy dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.*/site-packages /usr/local/lib/python3.*/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . /app
