FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure python output is sent straight to terminal
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run the application
# Use gunicorn with uvicorn workers for production
# Render will set the PORT environment variable
CMD sh -c "gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:${PORT:-8000}"
