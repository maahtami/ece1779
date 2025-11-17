# 🚀 Serverless Email Function API Documentation

This document details the architecture, local development guide, and deployment steps for a simple, authenticated email sending function built with Node.js, Express, and SendGrid, designed for deployment on Fly.io.

-----

## 1\. ⚙️ Architecture and Project Details

### Overview

The project is a minimal, Dockerized **API service** that handles sending emails using the **SendGrid** API. It is designed to be highly portable and easily deployed on container-based platforms like Fly.io.

### Key Technologies

  * **Runtime:** Node.js 22
  * **Web Framework:** Express.js
  * **Email Service:** `@sendgrid/mail`
  * **Containerization:** Docker
  * **Deployment Platform:** Fly.io

### API Endpoint & Functionality

| Method | Path | Description | Authentication Required |
| :---: | :---: | :---: | :---: |
| `GET` | `/` | Health check. Returns "Email function running." | Yes (via middleware) |
| `POST` | `/send-email` | Sends an email. Requires `subject` and `text` in the request body. The recipient (`to`) and sender (`from`) are hardcoded via environment variables. | Yes |

### Authentication

A custom `authMiddleware` is applied to all routes. To successfully call the API, the request must include an `Authorization` header:

`Authorization: Bearer <API_KEY>`

The server validates this token against the `process.env.API_KEY` environment variable.

### Configuration Variables

The service relies on four critical environment variables, listed in the `.env` file:

| Variable | Purpose |
| :---: | :---: |
| `API_KEY` | The secret key used for API authentication/authorization. |
| `SENDGRID_API_KEY` | Your personal API key for connecting to the SendGrid service. |
| `SENDER_EMAIL` | The verified email address used as the `from` address for all outgoing emails. |
| `TO_EMAIL` | The fixed recipient email address for all emails sent via the `/send-email` endpoint. |

-----

## 2\. 🖥️ Local Testing Guide (VS Code/Docker)

To run and test the application locally in your WSL environment using VS Code's integrated terminal:

### Prerequisites

1.  **Docker Desktop** (with WSL2 backend enabled).
2.  The repository files (`app.js`, `Dockerfile`, `package.json`, `.env`) in a local folder.

### Step 1: Configure Environment Variables

Open the `.env` file and populate it with placeholder values for local testing.

```
# .env file content
SENDGRID_API_KEY=SG.LOCAL_TEST_KEY_PLACEHOLDER
API_KEY=MY_LOCAL_SECRET_KEY
SENDER_EMAIL=test-sender@example.com
TO_EMAIL=test-recipient@example.com
```

### Step 2: Build the Docker Image

Navigate to the project root directory in your WSL terminal and run the build command.

```bash
docker build -t local-email-service .
```

### Step 3: Run the Container

Run the built image, exposing container port `3000` to local port `3000`, and injecting your environment variables.

```bash
docker run -d \
  --name email-service-local \
  --env-file .env \
  -p 3000:3000 \
  local-email-service
```

### Step 4: Test the API

Use a tool like `curl` to test the `/send-email` endpoint. Ensure you replace `MY_LOCAL_SECRET_KEY` with the value you set in your `.env` file.

```bash
curl -X POST http://localhost:3000/send-email \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer MY_LOCAL_SECRET_KEY" \
  -d '{
    "subject": "Test Email from Local Docker",
    "text": "This is a test body.",
    "html": "<p>This is a <b>test</b> body.</p>"
  }'
```

**Expected Response (Success):**

```json
{"success":true,"message":"Email sent"}
```

### Step 5: Stop and Clean Up

When finished, stop and remove the container.

```bash
# Stop the container
docker stop email-service-local

# Remove the container
docker rm email-service-local
```

-----

## 3\. ☁️ Deployment Steps to Fly.io

The project includes a pre-configured `fly.toml` file, which specifies the internal port (`3000`) and build configuration (`dockerfile = './Dockerfile'`).

### Prerequisites

1.  **`flyctl`** is installed and configured (run `fly auth login`).
2.  Your actual production SendGrid and API keys are ready.

### Step 1: Set Production Secrets

The environment variables used locally must be set as **secrets** on the Fly.io application. Replace the placeholder values with your actual production keys and emails.

```bash
fly secrets set \
  API_KEY="<YOUR_PRODUCTION_SECRET>" \
  SENDGRID_API_KEY="<YOUR_PRODUCTION_SENDGRID_KEY>" \
  SENDER_EMAIL="<YOUR_VERIFIED_SENDER_EMAIL>" \
  TO_EMAIL="<YOUR_PRIMARY_RECIPIENT_EMAIL>"
```

### Step 2: Deploy the Application

Run the deployment command from the project root. Fly.io will use the `fly.toml` file to find the application name (`serverless-emaildev`) and the `Dockerfile` to build and deploy the image.

```bash
fly deploy
```

### Step 3: Verify the Deployment

Once deployment is complete, you can check the status and logs:

```bash
# View the application status
fly status

# View the application logs
fly logs
```

The application will now be running and accessible via the public URL provided by `fly status`. You can test it remotely using the **production `API_KEY`**.