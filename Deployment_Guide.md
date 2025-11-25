Here is your document fully converted to clean, structured **Markdown**, with **no content changed**—only formatting:

---

# DigitalOcean Swarm Deployment and Local Setup Guide

This document outlines the complete workflow for the Inventory Management System (IMS), covering image preparation, local development/testing, and final deployment to a DigitalOcean Docker Swarm cluster.

---

## 1. Local Development and Testing (Docker Compose)

Use the `docker-compose.yml` file to run the entire stack on a single machine, ideal for development.

### 1.1. Prerequisites

Ensure the `.env` file is present in the root directory with all required backend variables defined:

```
POSTGRES_DB=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...
ADMIN_USERNAME=...
ADMIN_PASSWORD=...
SERVERLESS_EMAIL_URL=...
EMAIL_API_KEY=...
# REACT_APP_API_URL is NOT required in the .env file.
```

---

### 1.2. Execution Commands

The build argument is necessary here to point the frontend to the local API endpoint.

| Action          | Command                                                                                                                     |
| --------------- | --------------------------------------------------------------------------------------------------------------------------- |
| **Build & Run** | `docker compose build --build-arg REACT_APP_API_URL=http://localhost:8000`<br>`docker compose up -d`                        |
| **Access**      | Frontend: [http://localhost:3000](http://localhost:3000)<br>API: [http://localhost:8000](http://localhost:8000)             |
| **Cleanup**     | `docker compose down` (stops containers)<br>`docker compose down -v` (stops containers and removes persistent local volume) |

---

## 2. Image Build and Registry Push (Prerequisite for Swarm mode)

Before any deployment, all component images must be built and pushed to the Docker Hub registry (`tksdock/ece1779`) using the correct tags for both local and cloud environments.
This not required for docker compose testing in local since images will be built locally. However, for swarm mode deployment both in local and cloud, this step is a prerequisite.

---

### 2.1. Core Service Images

These images use standard tags (`v1.0`) for local Swarm and cloud deployment.

| Service         | Build Command                                                                                          | Push Command                                   |
| --------------- | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------- |
| **Database**    | `docker build -t ims-db:v1 ./infra/db`<br>`docker tag ims-db:v1 tksdock/ece1779:ims-db-v1.0`           | `docker push tksdock/ece1779:ims-db-v1.0`      |
| **Backend API** | `docker build -t ims-backend:v1 ./app`<br>`docker tag ims-backend:v1 tksdock/ece1779:ims-backend-v1.0` | `docker push tksdock/ece1779:ims-backend-v1.0` |

---

### 2.2. Frontend Image Building (API URL is Baked In)

The frontend requires two separate builds to hardcode the API endpoint at build time using the `--build-arg` option.

| Environment          | Build Command                                                                                                                                                                            | Push Command                                          |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| **Local Testing**    | `docker build -t ims-frontend:v1 --build-arg REACT_APP_API_URL=http://localhost:8000 ./frontend`<br>`docker tag ims-frontend:v1 tksdock/ece1779:ims-frontend-v1.0`                       | `docker push tksdock/ece1779:ims-frontend-v1.0`       |
| **Cloud Production** | `docker build -t ims-frontend:cloud-v1 --build-arg REACT_APP_API_URL=http://159.203.33.61:8000 ./frontend`<br>`docker tag ims-frontend:cloud-v1 tksdock/ece1779:ims-frontend-cloud-v1.0` | `docker push tksdock/ece1779:ims-frontend-cloud-v1.0` |

---

## 3. Local Swarm Mode Testing

Use the `docker-stack-local.yml` file to simulate a Swarm deployment locally.

### 3.1. Prerequisites

* Ensure the local image tags (`ims-db-v1.0`, `ims-backend-v1.0`, `ims-frontend-v1.0`) are pushed and available.
* Ensure the `.env` file is present (same as section 1.1).

---

### 3.2. Execution Commands

| Action               | Command                                                                                                         |
| -------------------- | --------------------------------------------------------------------------------------------------------------- |
| **Initialize Swarm** | `docker swarm init`                                                                                             |
| **Deploy Stack**     | `docker stack deploy -c docker-stack-local.yml ims_stack`                                                       |
| **Verify Services**  | `docker service ls` (see services)<br>`docker service ps ims_stack_api` (check container tasks)                 |
| **Scaling Example**  | `docker service scale ims_stack_api=3`                                                                          |
| **Access**           | Frontend: [http://localhost:3000](http://localhost:3000)<br>API: [http://localhost:8000](http://localhost:8000) |
| **Cleanup**          | `docker stack rm ims_stack`                                                                                     |

---

## 4. Cloud Production Deployment (DigitalOcean Swarm)

This uses the dedicated `docker-stack.yml` file for the clustered, persistent deployment environment.

---

### 4.1. Infrastructure Setup (Manual)

#### **Droplet Creation**

Create three Droplets:

* `ims-swarm-manager`
* `ims-swarm-worker-1`
* `ims-swarm-worker-2`

#### **Swarm Setup**

* **Manager Node:** Run `setup_manager.sh` to install Docker and initialize Swarm.
* **Worker Nodes:** Run `setup_worker.sh`, then manually run the `docker swarm join ...` command provided by the manager.

#### **Persistent Volume**

1. Create a DigitalOcean Block Storage Volume called `imsdbdata`.
2. Attach the volume to the `ims-swarm-manager` Droplet.
3. Make sure the volume is mounted to the droplet in the path below:

```
/mnt/imsdbdata
```

(as referenced in `docker-stack.yml`)

---

### 4.2. Deployment Commands

Perform these steps on the `ims-swarm-manager` Droplet.

#### **Prepare Environment**

```bash
# Clone the repository
git clone https://github.com/maahtami/ece1779.git
cd ece1779

# Copy/transfer the .env file to the root directory
# Ensure all cloud variables are set correctly for the production environment.
```

---

#### Deployment Steps

| Action              | Command                                              |
| ------------------- | ---------------------------------------------------- |
| **Deploy Stack**    | `docker stack deploy -c docker-stack.yml ims_stack`  |
| **Verify Services** | `docker service ls`<br>`docker service ps ims_stack` |

#### Access and Monitoring

* Frontend: `http://159.203.33.61:3000`
* API (testing): `http://159.203.33.61:8000`

---

### Cleanup

| Action            | Command                                                                                  |
| ----------------- | ---------------------------------------------------------------------------------------- |
| **Remove Stack**  | `docker stack rm ims_stack`                                                              |
| **Drain Manager** | `docker node update --availability drain ims-swarm-manager` *(Optional for maintenance)* |

---

## 5. Serverless Function Deployment (DigitalOcean Functions)

This section covers deploying the email notification serverless function to DigitalOcean Functions.

---

### 5.1. Prerequisites

Ensure the `.env` file is present in the `serverless` directory with the following variables:

```
SENDGRID_API_KEY=...
API_KEY=...
SENDER_EMAIL=...
TO_EMAIL=...
```

**Note:** The `project.yml` file references these environment variables.

---

### 5.2. Installation and Setup

#### **Install `doctl` CLI**

Follow the official DigitalOcean instructions to install `doctl` for your operating system:
[https://docs.digitalocean.com/reference/doctl/how-to/install/](https://docs.digitalocean.com/reference/doctl/how-to/install/)

#### **Generate API Token**

1. Log in to your DigitalOcean account.
2. Navigate to **API** → **Tokens/Keys** → **Generate New Token**.
3. Select **Functions** scope and generate the token.
4. Copy the token for the next step.

#### **Authenticate `doctl`**

```bash
doctl auth init
```

Enter the API token when prompted.

---

### 5.3. Install Dependencies

Navigate to the function directory and install the required Node.js packages:

```bash
cd serverless/packages/serverless-fn/send-email/
npm install @sendgrid/mail
cd ../../../../
```

---

### 5.4. Deploy the Function

Deploy the serverless function from the repository root:

```bash
doctl serverless deploy serverless
```

---

### 5.5. Verify Deployment

After deployment, `doctl` will output the function URL. You can test it using:

```bash
curl -X POST <FUNCTION_URL> \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <API_KEY>" \
  -d '{
    "subject": "Test Email",
    "text": "This is a test email.",
    "html": "<p>This is a <b>test</b> email.</p>"
  }'
```

Replace `<FUNCTION_URL>` with the deployed function URL and `<API_KEY>` with your `API_KEY` from the `.env` file.

---
