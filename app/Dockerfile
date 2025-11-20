# Stage 1: Build Stage (to fetch the Docker binary without cluttering the final image)
FROM python:3.11-slim AS builder

# Install curl and ca-certificates (needed to download the binary)
RUN apt-get update && \
    apt-get install -y curl ca-certificates --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Download the static Docker CLI binary and place it in a temporary path
# We download the correct architecture (linux/amd64 is standard for most Docker hosts)
RUN curl -sL https://download.docker.com/linux/static/stable/x86_64/docker-26.0.0.tgz | tar -xz && \
    mv docker/docker /usr/local/bin/docker && \
    rm -r docker

# ----------------------------------------------------------------------------------

# Stage 2: Final Image Stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# We ONLY install the packages needed for Python/PostgreSQL (gcc, libpq-dev)
RUN apt-get update && apt-get install -y gcc libpq-dev --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

ENV PASSLIB_BCRYPT_NO_CHECK=1

# Copy the Docker CLI binary from the builder stage
COPY --from=builder /usr/local/bin/docker /usr/local/bin/docker

# Copy necessary certificates (needed for Docker to talk to the daemon)
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Copy dependencies and application files
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app/app

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]