FROM python:3.12.3-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=2.1.3
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

# Install poetry separated from system python
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

# Copy only dependency files first
COPY pyproject.toml poetry.lock* ./

# Configure poetry
RUN poetry config virtualenvs.create false

# Copy the rest of the application
COPY . .

# Install dependencies and the project itself
RUN poetry install --no-interaction --no-ansi

# Create data directory for persistent storage
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=counter.entrypoints.webapp
ENV PYTHONDONTWRITEBYTECODE=1


# Command to run the application using Flask directly
#CMD ["poetry", "run", "python", "-m", "flask", "run", "--host=0.0.0.0"]
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]

