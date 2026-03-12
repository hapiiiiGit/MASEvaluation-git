## Implementation approach

We will use FastAPI (Python) for the backend due to its speed, async support, and built-in OpenAPI documentation. React will be used for the frontend, leveraging MUI for UI components and Chart.js (with react-chartjs-2) for radar charts and heatmaps. For PDF/CSV export, we will use open-source libraries (e.g., ReportLab for PDF, pandas for CSV). Authentication will be handled via JWT with email/password. The backend will expose RESTful APIs for survey CRUD, response submission, analytics, and report generation. Integration points include:
- Frontend <-> Backend via REST APIs
- Backend <-> Database (PostgreSQL)
- Backend <-> File system (for PDF/CSV export)

## File list

- public/index.html
- src/App.jsx
- src/components/SurveyBuilder.jsx
- src/components/SurveyList.jsx
- src/components/SurveyAnalytics.jsx
- src/components/ChartRadar.jsx
- src/components/ChartHeatmap.jsx
- src/components/ExportButtons.jsx
- src/api/index.js
- src/pages/Login.jsx
- src/pages/Dashboard.jsx
- backend/main.py
- backend/models.py
- backend/schemas.py
- backend/api/survey.py
- backend/api/response.py
- backend/api/analytics.py
- backend/api/report.py
- backend/api/auth.py
- backend/utils/pdf_export.py
- backend/utils/csv_export.py
- backend/database.py
- backend/config.py

## Data structures and interfaces:

```mermaid
classDiagram
    class User {
        +id: int
        +email: str
        +password_hash: str
        +role: str
        +created_at: datetime
    }
    class Survey {
        +id: int
        +title: str
        +description: str
        +questions: list[Question]
        +created_by: int
        +created_at: datetime
    }
    class Question {
        +id: int
        +survey_id: int
        +text: str
        +type: str
        +options: list[str]
    }
    class Response {
        +id: int
        +survey_id: int
        +user_id: int
        +answers: dict[int, str|int|float]
        +submitted_at: datetime
    }
    class AnalyticsService {
        +get_radar_data(survey_id: int) -> dict
        +get_heatmap_data(survey_id: int) -> dict
    }
    class ReportService {
        +generate_pdf(survey_id: int) -> bytes
        +generate_csv(survey_id: int) -> bytes
    }
    class AuthService {
        +login(email: str, password: str) -> str
        +register(email: str, password: str) -> User
        +verify_token(token: str) -> User
    }
    User "1" -- "*" Survey: creates
    Survey "1" -- "*" Question: contains
    Survey "1" -- "*" Response: receives
    User "1" -- "*" Response: submits
    Survey "1" -- "1" AnalyticsService: analyzed by
    Survey "1" -- "1" ReportService: reported by
```

## Program call flow:

```mermaid
sequenceDiagram
    participant F as Frontend
    participant A as AuthService
    participant S as SurveyAPI
    participant Q as QuestionAPI
    participant R as ResponseAPI
    participant AN as AnalyticsService
    participant RP as ReportService
    participant DB as Database

    F->>A: POST /api/auth/login (email, password)
    A->>DB: verify credentials
    A-->>F: JWT token

    F->>S: POST /api/survey (token, survey data)
    S->>DB: create survey
    S-->>F: survey id

    F->>Q: POST /api/survey/{id}/question (token, question data)
    Q->>DB: add question
    Q-->>F: question id

    F->>R: POST /api/survey/{id}/response (token, answers)
    R->>DB: save response
    R-->>F: response id

    F->>AN: GET /api/survey/{id}/analytics/radar (token)
    AN->>DB: fetch responses
    AN-->>F: radar chart data

    F->>AN: GET /api/survey/{id}/analytics/heatmap (token)
    AN->>DB: fetch responses
    AN-->>F: heatmap data

    F->>RP: GET /api/survey/{id}/report/pdf (token)
    RP->>DB: fetch survey & responses
    RP->>RP: generate PDF
    RP-->>F: PDF file

    F->>RP: GET /api/survey/{id}/report/csv (token)
    RP->>DB: fetch survey & responses
    RP->>RP: generate CSV
    RP-->>F: CSV file
```

## Anything UNCLEAR

- Preferred backend framework: FastAPI, Flask, or Express? (Default: FastAPI)
- Should authentication support OAuth/social login or just email/password? (Default: email/password)
- Expected scale (users/surveys/responses)?
- Compliance/data privacy requirements?
- Multi-tenancy support needed?
