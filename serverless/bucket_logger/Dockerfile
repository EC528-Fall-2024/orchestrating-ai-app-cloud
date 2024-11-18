FROM python:3.9-slim

# Install dependencies for mysql-connector-python
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make sure the entrypoint script is executable
ENV PORT 8080
ENV PYTHONUNBUFFERED True

# Command to run the application
CMD exec python main.py