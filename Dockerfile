# Base image
FROM python:3.12-slim

# Install MySQL server and dependencies
RUN apt-get update && apt-get install -y mysql-server curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY ./web /app/web
COPY ./internal /app/internal
COPY ./db/init.sql /app/db/init.sql

# Install Python dependencies
RUN pip install flask requests mysql-connector-python

# Setup MySQL
RUN service mysql start && \
    mysql -e "CREATE DATABASE IF NOT EXISTS photovault;" && \
    mysql -e "CREATE USER IF NOT EXISTS 'pvuser'@'%' IDENTIFIED BY 'pvpass';" && \
    mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'pvuser'@'%' WITH GRANT OPTION;" && \
    mysql -e "FLUSH PRIVILEGES;"

# Copy init.sql into database
RUN service mysql start && \
    mysql -u root -e "USE photovault; SOURCE /app/db/init.sql;"

# Expose port
EXPOSE 5000

# Run all services (MySQL, internal & web)
CMD service mysql start && \
    python /app/internal/app.py & \
    python /app/web/app.py
