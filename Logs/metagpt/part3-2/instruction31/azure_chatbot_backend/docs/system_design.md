## Implementation approach

We will use FastAPI (Python) for the backend due to its speed, simplicity, and native async support, making it ideal for serving RESTful endpoints on a low-cost Azure VM. The backend will securely interface with the OpenAI API using environment variables for API keys. The frontend will be a static web app (HTML/JavaScript/CSS) deployed on Azure free web app, communicating with the backend via HTTP (fetch/AJAX). The UI will be clean and responsive, using vanilla JS and CSS for cost and simplicity. Security will be ensured by CORS configuration and not exposing sensitive keys to the frontend.

Deployment:
- Backend: Deploy FastAPI app on Azure VM (B1s or similar), using Gunicorn/Uvicorn and Nginx reverse proxy.
- Frontend: Deploy static files to Azure free web app (App Service Static Web Apps).
- API keys stored as environment variables on VM.
- CORS enabled for frontend-backend communication.

## File list

- backend/
    - main.py
    - requirements.txt
    - .env (not checked in)
    - utils.py
    - openai_client.py
    - Dockerfile
    - README.md
- frontend/
    - index.html
    - style.css
    - app.js
    - assets/
- docs/
    - system_design.md
    - system_design-sequence-diagram.mermaid
    - system_design-sequence-diagram.mermaid-class-diagram

## Data structures and interfaces:

See 'system_design-sequence-diagram.mermaid-class-diagram' for mermaid classDiagram.

## Program call flow:

See 'system_design-sequence-diagram.mermaid' for mermaid sequenceDiagram.

## Anything UNCLEAR

- Expected peak user load is not specified; may affect scaling and VM choice.
- No specific authentication method defined; basic auth or JWT can be added if required.
- Data privacy/compliance requirements are unclear.
- No file upload/multimedia support required per PRD.
- Branding elements for UI are not specified; will use generic branding unless clarified.