# Use official Python slim image for smaller size
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Environment variables (will be overridden at runtime)
ENV PREFECT_API_URL=http://127.0.0.1:4200/api

# Default command: run your flow once (for testing)
CMD ["python", "etl_weather.py"]