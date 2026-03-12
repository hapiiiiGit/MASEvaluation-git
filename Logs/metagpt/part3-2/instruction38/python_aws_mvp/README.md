# python_aws_mvp

A modern, modular MVP platform with a Python FastAPI backend, AWS infrastructure (provisioned via Terraform), secure authentication, S3 presigned upload flows, Stripe metered billing, strong observability, and a responsive Next.js/React frontend.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [Infrastructure (Terraform)](#infrastructure-terraform)
- [Environment Configuration](#environment-configuration)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Multi-Environment Support](#multi-environment-support)
- [Observability](#observability)
- [Billing](#billing)
- [File Uploads](#file-uploads)
- [Contributing](#contributing)
- [License](#license)

---

## Architecture Overview

- **Backend:** Python (FastAPI), modularized for authentication, storage, billing, observability.
- **Frontend:** Next.js & React, fully responsive, integrates with backend APIs and Stripe.
- **Infrastructure:** AWS (EC2, S3, IAM, CloudWatch), provisioned via Terraform with multi-environment support (dev, staging, prod).
- **Authentication:** OAuth2/JWT.
- **Storage:** S3 presigned upload flows.
- **Billing:** Stripe metered billing and subscriptions.
- **Observability:** AWS CloudWatch (logs, metrics), Sentry (error tracking).
- **Documentation:** OpenAPI (Swagger UI), Markdown guides.

---

## Features

- **Multi-environment AWS deployment (dev, staging, prod)**
- **Secure authentication (OAuth2/JWT)**
- **Direct S3 file uploads via presigned URLs**
- **Stripe metered billing and subscriptions**
- **Responsive Next.js/React frontend**
- **Logging, monitoring, and error tracking**
- **Comprehensive documentation**

---

## Tech Stack

- **Backend:** Python 3.9+, FastAPI, boto3, stripe, passlib, jose, pydantic
- **Frontend:** Next.js 13+, React 18+, Stripe.js
- **Infrastructure:** Terraform 1.3+, AWS (EC2, S3, IAM, CloudWatch)
- **Observability:** CloudWatch, Sentry
- **Documentation:** OpenAPI, Markdown

---

## Setup & Installation

### Backend

1. **Install dependencies:**
   ```bash
   cd backend/app
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   - Copy `.env.example` to `.env` and fill in values (see [Environment Configuration](#environment-configuration)).

3. **Run locally:**
   ```bash
   uvicorn backend.app.main:app --reload
   ```
   - Access API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

### Frontend

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure API base URL:**
   - Set `NEXT_PUBLIC_API_BASE_URL` in `.env.local` (e.g., `http://localhost:8000`).

3. **Run locally:**
   ```bash
   npm run dev
   ```
   - Access frontend at [http://localhost:3000](http://localhost:3000)

### Infrastructure (Terraform)

1. **Install Terraform:**  
   [Terraform Installation Guide](https://learn.hashicorp.com/tutorials/terraform/install-cli)

2. **Configure environment variables:**  
   - Edit `terraform/env/dev.tfvars`, `terraform/env/staging.tfvars`, `terraform/env/prod.tfvars` with your AWS credentials, S3 bucket names, Stripe keys, etc.

3. **Provision AWS resources:**
   ```bash
   cd terraform
   terraform init
   terraform apply -var-file=env/dev.tfvars
   # For staging/prod, use the respective tfvars file
   ```

---

## Environment Configuration

All sensitive settings are managed via environment variables and `.env` files.

**Backend `.env` example:**