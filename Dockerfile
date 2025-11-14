FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Disable passlib bcrypt wrap-bug testing
ENV PASSLIB_BCRYPT_NO_CHECK=1

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy ENTIRE project (not only /app/app)
COPY . /app

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", 8080]