# python_aws_mvp Backend Documentation

## Overview

The `python_aws_mvp` backend is a modular FastAPI application designed for rapid deployment and scaling on AWS, supporting multi-environment setups (dev, staging, prod) via Terraform. It provides secure authentication, S3 presigned upload flows, Stripe metered billing, strong observability, and is fully documented with OpenAPI.

---

## Architecture

- **Framework:** FastAPI (Python)
- **Deployment:** AWS (EC2, S3, IAM, CloudWatch), provisioned via Terraform
- **Authentication:** OAuth2/JWT
- **Storage:** AWS S3 with presigned URLs
- **Billing:** Stripe metered billing and subscriptions
- **Observability:** AWS CloudWatch (logs, metrics), Sentry (error tracking)
- **Documentation:** OpenAPI (Swagger UI at `/docs`), Markdown guides

---

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/login`  
  Login with email and password. Returns JWT token.
- `POST /auth/register`  
  Register a new user. Returns JWT token.
- `GET /auth/me`  
  Get current user info (requires JWT).

### Storage (`/storage`)
- `POST /storage/presigned-url`  
  Request a presigned S3 URL for file upload. Requires JWT.
- `POST /storage/validate-upload`  
  Validate that a file was uploaded to S3. Requires JWT.

### Billing (`/billing`)
- `POST /billing/create-customer`  
  Create a Stripe customer for the user. Requires JWT.
- `POST /billing/create-subscription`  
  Create a Stripe subscription for the user. Requires JWT.
- `POST /billing/meter-usage`  
  Record metered usage for the user. Requires JWT.
- `GET /billing/invoice`  
  Get the latest Stripe invoice for the user. Requires JWT.

### Observability (`/observability`)
- `POST /observability/log-event`  
  Log an event to CloudWatch.
- `POST /observability/track-error`  
  Track an error in Sentry.
- `GET /observability/metrics`  
  Get service metrics from CloudWatch.

### Health
- `GET /health`  
  Health check endpoint.

---

## Authentication Flow

- Uses OAuth2 with JWT tokens.
- Passwords are hashed with bcrypt.
- JWT secret is configured via environment variable.
- Example login:
  ```
  POST /auth/login
  Content-Type: application/x-www-form-urlencoded
  Body: username, password
  Response: { "access_token": "...", "token_type": "bearer" }
  ```
- Protect endpoints by passing `Authorization: Bearer <token>` header.

---

## S3 Presigned Upload Flow

1. Request a presigned URL:
   ```
   POST /storage/presigned-url
   Body: { "filename": "example.pdf", "content_type": "application/pdf" }
   ```
2. Upload file directly to S3 using the returned URL.
3. Validate upload:
   ```
   POST /storage/validate-upload
   Body: { "file_id": "...", "filename": "...", "content_type": "...", "size": ... }
   ```

---

## Stripe Metered Billing

- Stripe API key is configured via environment variable.
- Create customer and subscription via API.
- Meter usage by posting usage data.
- Retrieve invoices for billing information.

---

## Observability

- **Logging:** All events and errors are logged locally and sent to AWS CloudWatch.
- **Error Tracking:** Errors are sent to Sentry if DSN is configured.
- **Metrics:** Custom metrics are available via CloudWatch.

---

## Environment Setup

### Configuration

All settings are managed via environment variables and `.env` file. Key variables:

- `APP_HOST`, `APP_PORT`, `APP_RELOAD`
- `ENVIRONMENT` (dev, staging, prod)
- `JWT_SECRET_KEY`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_S3_BUCKET`
- `STRIPE_API_KEY`
- `SENTRY_DSN`

See `config.py` for details.

### Running Locally

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Set environment variables or create `.env` file.
3. Start the backend:
   ```
   uvicorn backend.app.main:app --reload
   ```
4. Access API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

### Deployment

- Use Terraform to provision AWS resources:
  ```
  terraform init
  terraform apply -var-file=env/dev.tfvars
  ```
- Deploy backend to EC2 (user data script starts FastAPI app).
- Ensure environment variables are set on EC2 instance.

---

## Integration Points

- **Frontend:** Next.js/React app communicates via REST API.
- **AWS:** S3 for storage, EC2 for backend, IAM for roles, CloudWatch for logs/metrics.
- **Stripe:** Python SDK for billing.
- **Sentry:** Error tracking.

---

## OpenAPI Documentation

- Available at `/docs` (Swagger UI) and `/openapi.json`.
- All endpoints are documented with request/response models.

---

## File Structure

- `main.py` - FastAPI entry point
- `auth.py` - Authentication logic
- `storage.py` - S3 upload logic
- `billing.py` - Stripe billing logic
- `observability.py` - Logging, metrics, error tracking
- `models.py` - Data models
- `api.py` - API routers
- `config.py` - Configuration management

---

## Example Usage

### Register & Login
