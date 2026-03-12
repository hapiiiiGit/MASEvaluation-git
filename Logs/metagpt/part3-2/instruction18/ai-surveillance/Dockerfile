# syntax=docker/dockerfile:1

# --- Stage 1: Build React Frontend ---
FROM node:18 AS frontend-builder

WORKDIR /app/frontend

# Copy only frontend files
COPY src/web/dashboard/package.json src/web/dashboard/package-lock.json ./ 
RUN npm install

COPY src/web/dashboard ./ 
RUN npm run build

# --- Stage 2: Build Python Backend ---
FROM python:3.10-slim AS backend

# System dependencies for OpenCV and others
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        libsm6 \
        libxext6 \
        libgl1-mesa-glx \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY src ./src
COPY model ./model

# Copy config if exists
COPY src/config.py ./src/config.py

# --- Stage 3: Final Image Assembly ---
FROM python:3.10-slim

WORKDIR /app

# System dependencies for OpenCV and others
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        libsm6 \
        libxext6 \
        libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from backend build
COPY --from=backend /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=backend /usr/local/bin /usr/local/bin

# Copy backend code and model
COPY --from=backend /app/src ./src
COPY --from=backend /app/model ./model
COPY --from=backend /app/requirements.txt ./requirements.txt

# Copy built frontend from builder
COPY --from=frontend-builder /app/frontend/build ./src/web/dashboard/build

# Expose FastAPI port
EXPOSE 8000

# Set environment variables for production
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Entrypoint to run FastAPI backend
CMD ["uvicorn", "src.web.api:app", "--host", "0.0.0.0", "--port", "8000"]