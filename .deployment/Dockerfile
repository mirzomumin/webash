# FROM python:3.13.1-alpine as builder
FROM python:3.13.1-slim-bullseye as builder

WORKDIR /app

# Install system dependencies
RUN get-apt add --no-cache \
    libpq-dev curl \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
RUN poetry config virtualenvs.create false

# Install Python dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root

COPY . /app

# Final stage: Use a minimal Alpine image
# FROM python:3.13.1-alpine
FROM python:3.13.1-slim-bullseye

WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app
