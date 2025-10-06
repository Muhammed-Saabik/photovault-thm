# Base image
FROM python:3.12-slim

WORKDIR /app

# Copy code
COPY ./web /app/web
COPY ./internal /app/internal

# Install Python dependencies
RUN pip install flask requests mysql-connector-python

# Expose port
EXPOSE 5000

# Run internal + web
CMD python /app/internal/app.py & python /app/web/app.py
