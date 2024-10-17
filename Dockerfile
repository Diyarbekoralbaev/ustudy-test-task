# Use official Python 3.11 image as the base image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files and to buffer outputs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install dependencies and system packages required for the app
RUN apt-get update \
    && apt-get install -y \
        libpq-dev \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install psycopg[pool]

# Copy the rest of the application code into the container
COPY . .
COPY .env .env

# Command to run the application (replace main_new.py with your main file)
CMD ["gunicorn --workers 3 --bind 0.0.0.0:8000 ustudy_test_task.wsgi:application"]
