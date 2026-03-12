# Azure Chatbot Backend

This is the backend for a web-based chatbot, implemented in Python using FastAPI. It interfaces securely with the OpenAI API to provide conversational AI responses. The backend is designed to be deployed on a cost-effective Azure VM and communicates with a static frontend web app (HTML/JavaScript) hosted on Azure App Service Static Web Apps.

## Features

- FastAPI RESTful backend for chatbot communication
- Asynchronous calls to OpenAI API (GPT-3.5-turbo by default)
- Secure API key management via environment variables
- CORS configuration for safe frontend-backend communication
- Containerized with Docker for easy deployment
- Logging and input validation utilities

## File Structure
