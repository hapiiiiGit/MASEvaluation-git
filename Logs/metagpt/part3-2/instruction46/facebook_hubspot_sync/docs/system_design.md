## Implementation approach

We will use a modular Python backend (FastAPI for REST API, requests-oauthlib for OAuth 2.0, APScheduler for sync routines, SQLAlchemy for data storage, and logging for error handling). The backend will securely connect to Facebook Marketing API and HubSpot API, handle OAuth 2.0 authentication, map ad metrics to HubSpot contacts/deals, and expose endpoints for the React dashboard. The frontend will use Vite, React, MUI, and Tailwind CSS for a lightweight, responsive dashboard with filtering, segmentation, and visualization features.

Open-source libraries:
- Backend: FastAPI, requests-oauthlib, APScheduler, SQLAlchemy, python-dotenv, logging
- Frontend: React, MUI, Tailwind CSS, axios

## File list

- backend/
    - main.py
    - auth/
        - facebook_oauth.py
        - hubspot_oauth.py
    - sync/
        - scheduler.py
        - mapping.py
    - models/
        - contact.py
        - deal.py
        - ad_metric.py
    - api/
        - endpoints.py
    - utils/
        - logger.py
        - notifier.py
    - config.py
    - requirements.txt
- frontend/
    - src/
        - App.jsx
        - components/
            - Dashboard.jsx
            - FilterPanel.jsx
            - DataTable.jsx
            - ChartPanel.jsx
            - SegmentationSidebar.jsx
            - SyncStatusBar.jsx
            - ExportButton.jsx
        - api/
            - api.js
        - styles/
            - tailwind.css
    - index.html
    - package.json
    - vite.config.js
- docs/
    - system_design.md
    - system_design-sequence-diagram.mermaid
    - system_design-sequence-diagram.mermaid-class-diagram

## Data structures and interfaces:

```mermaid
classDiagram
    class FacebookOAuth {
        +__init__(client_id: str, client_secret: str, redirect_uri: str)
        +get_auth_url() str
        +fetch_token(code: str) dict
        +refresh_token(refresh_token: str) dict
    }
    class HubSpotOAuth {
        +__init__(client_id: str, client_secret: str, redirect_uri: str)
        +get_auth_url() str
        +fetch_token(code: str) dict
        +refresh_token(refresh_token: str) dict
    }
    class AdMetric {
        +id: int
        +campaign_id: str
        +ad_id: str
        +date: date
        +clicks: int
        +impressions: int
        +spend: float
        +conversions: int
        +fetch_from_facebook(token: str, params: dict) list[AdMetric]
    }
    class Contact {
        +id: int
        +email: str
        +name: str
        +facebook_id: str
        +update_from_metric(metric: AdMetric)
    }
    class Deal {
        +id: int
        +contact_id: int
        +amount: float
        +stage: str
        +update_from_metric(metric: AdMetric)
    }
    class Mapping {
        +map_metrics_to_contacts(metrics: list[AdMetric]) list[Contact]
        +map_metrics_to_deals(metrics: list[AdMetric]) list[Deal]
    }
    class Scheduler {
        +__init__(interval: int)
        +start()
        +run_sync()
        +adjust_interval(new_interval: int)
    }
    class Logger {
        +log_error(msg: str)
        +log_info(msg: str)
    }
    class Notifier {
        +notify_error(msg: str)
        +notify_success(msg: str)
    }
    class API {
        +get_metrics(filter: dict) list[AdMetric]
        +get_contacts(filter: dict) list[Contact]
        +get_deals(filter: dict) list[Deal]
        +trigger_manual_sync()
        +get_sync_status() str
    }
    FacebookOAuth <.. API
    HubSpotOAuth <.. API
    AdMetric <.. Mapping
    Contact <.. Mapping
    Deal <.. Mapping
    Scheduler <.. API
    Logger <.. Scheduler
    Notifier <.. Scheduler
```

## Program call flow:

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant API as API
    participant FB as FacebookOAuth
    participant HS as HubSpotOAuth
    participant S as Scheduler
    participant M as Mapping
    participant AM as AdMetric
    participant C as Contact
    participant D as Deal
    participant L as Logger
    participant N as Notifier

    U->>FE: Login & authorize Facebook/HubSpot
    FE->>API: /auth/facebook, /auth/hubspot
    API->>FB: get_auth_url()
    FB-->>API: auth_url
    API-->>FE: redirect to auth_url
    FE->>API: /auth/callback (with code)
    API->>FB: fetch_token(code)
    FB-->>API: access_token
    API->>HS: fetch_token(code)
    HS-->>API: access_token
    API-->>FE: Auth success

    U->>FE: Set sync interval, mapping rules
    FE->>API: /settings (interval, rules)
    API->>S: adjust_interval(new_interval)

    S->>API: run_sync()
    API->>FB: fetch ad metrics
    FB-->>API: metrics
    API->>M: map_metrics_to_contacts(metrics)
    M->>C: update_from_metric(metric)
    API->>M: map_metrics_to_deals(metrics)
    M->>D: update_from_metric(metric)
    API->>HS: update contacts/deals
    HS-->>API: update status
    API->>L: log_info("Sync completed")
    API->>N: notify_success("Sync completed")

    FE->>API: /metrics, /contacts, /deals (with filters)
    API->>AM: get_metrics(filter)
    API->>C: get_contacts(filter)
    API->>D: get_deals(filter)
    API-->>FE: filtered data

    FE->>U: Display dashboard (table, charts, segmentation)

    S->>L: log_error(msg) on failure
    S->>N: notify_error(msg) on failure
```

## Anything UNCLEAR

- Specific Facebook ad metrics required for mapping (e.g., clicks, impressions, spend, conversions?)
- Should sync routine support real-time updates or only scheduled intervals?
- What user roles and permissions are needed for dashboard access?
- Any compliance/data privacy requirements?
- Preferred notification channel for sync errors?
