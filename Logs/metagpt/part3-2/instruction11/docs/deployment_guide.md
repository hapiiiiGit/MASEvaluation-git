# Django Web Application Deployment Guide

This guide provides step-by-step instructions for deploying the Django web application to production. It covers Docker setup, environment variables, database migrations, static/media file collection, security best practices, and production server configuration.

---

## 1. Prerequisites

- Docker and Docker Compose installed
- A production-ready server (e.g., Ubuntu 22.04+, AWS EC2, DigitalOcean, etc.)
- Domain name (optional, but recommended)
- SMTP credentials for email (optional, for password reset, etc.)

---

## 2. Environment Variables

Copy `.env.example` to `.env` and fill in the values:
