# ───────────── Stage 1: Builder ─────────────
FROM python:3.11-alpine AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    build-base \
    postgresql-dev \
    python3-dev \
    jpeg-dev \
    zlib-dev \
    tzdata

# Set workdir
WORKDIR /app

# Copy requirement file and install packages to custom directory
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# ───────────── Stage 2: Final ─────────────
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Install only runtime dependencies
RUN apk add --no-cache \
    libpq \
    libffi \
    jpeg \
    zlib \
    tzdata

# Add non-root user
RUN adduser -D myuser

# Set workdir
WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy project files
COPY . .

# Collect static files (if needed)
#RUN python manage.py collectstatic --noinput

# Change ownership and switch user
RUN chown -R myuser /app
USER myuser

# Expose port and run server
EXPOSE 8000
CMD ["gunicorn", "avjar.wsgi:application", "--bind", "0.0.0.0:8000"]
