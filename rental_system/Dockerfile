# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy dependency file first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose Flask/Gunicorn port
EXPOSE 5000

# Run with Gunicorn (production)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
