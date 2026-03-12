## Implementation approach

We will redesign the Odoo Online customer portal UI using Odoo's QWeb templating system for frontend structure, SCSS for modern styling, and JavaScript for interactive elements. For legal compliance, we will add a Terms & Conditions checkbox to relevant forms, store customer consent in the backend (PostgreSQL via Odoo ORM), and provide admin tools for consent management and audit trails. The architecture will leverage Odoo's modularity, using custom modules and extending existing models/views. Open-source libraries such as Bootstrap (for SCSS), vanilla JS, and Odoo's built-in ORM will be used for simplicity and maintainability.

## File list

- odoo_online_customer_portal/
  - __init__.py
  - __manifest__.py
  - models/
    - customer_consent.py
  - views/
    - portal_templates.xml (QWeb)
    - admin_consent_templates.xml (QWeb)
  - static/
    - src/
      - scss/
        - portal.scss
      - js/
        - portal.js
  - controllers/
    - main.py
  - security/
    - ir.model.access.csv
  - docs/
    - system_design.md
    - system_design-sequence-diagram.mermaid
    - system_design-sequence-diagram.mermaid-class-diagram

## Data structures and interfaces:

```mermaid
classDiagram
    class ResUsers {
        +id: int
        +name: str
        +email: str
        +consent_ids: list[CustomerConsent]
    }
    class CustomerConsent {
        +id: int
        +user_id: int
        +consent_given: bool
        +consent_date: datetime
        +terms_version: str
        +jurisdiction: str
        +audit_log: list[ConsentAudit]
        +__init__(user_id: int, consent_given: bool, terms_version: str, jurisdiction: str)
    }
    class ConsentAudit {
        +id: int
        +consent_id: int
        +action: str
        +timestamp: datetime
        +performed_by: int
        +__init__(consent_id: int, action: str, performed_by: int)
    }
    class PortalController {
        +show_portal()
        +submit_consent(user_id: int, consent_given: bool, terms_version: str, jurisdiction: str)
        +get_consent_status(user_id: int) -> CustomerConsent
    }
    class AdminConsentController {
        +list_consents()
        +view_consent(consent_id: int)
        +update_consent(consent_id: int, consent_given: bool)
        +get_audit_trail(consent_id: int) -> list[ConsentAudit]
    }
    ResUsers "1" -- "*" CustomerConsent : has
    CustomerConsent "1" -- "*" ConsentAudit : logs
    PortalController ..> CustomerConsent : manages
    AdminConsentController ..> CustomerConsent : manages
    AdminConsentController ..> ConsentAudit : audits
```

## Program call flow:

```mermaid
sequenceDiagram
    participant U as User
    participant PC as PortalController
    participant CC as CustomerConsent
    participant AC as AdminConsentController
    participant CA as ConsentAudit
    participant DB as Database

    U->>PC: Access portal (show_portal)
    PC->>DB: Fetch user profile
    PC->>CC: get_consent_status(user_id)
    CC-->>PC: Return consent status
    PC-->>U: Display dashboard/profile with consent info

    U->>PC: Submit registration with T&C checkbox
    PC->>CC: submit_consent(user_id, consent_given, terms_version, jurisdiction)
    CC->>DB: Store consent record
    CC->>CA: Log audit entry (action="consent_given")
    CA->>DB: Store audit log
    CC-->>PC: Confirmation
    PC-->>U: Show success message

    participant Admin as Admin
    Admin->>AC: list_consents()
    AC->>DB: Query all consent records
    DB-->>AC: Return consent list
    AC-->>Admin: Display consent management panel

    Admin->>AC: view_consent(consent_id)
    AC->>CC: Fetch consent record
    CC-->>AC: Return consent details
    AC->>CA: get_audit_trail(consent_id)
    CA->>DB: Query audit logs
    DB-->>CA: Return audit trail
    CA-->>AC: Return audit trail
    AC-->>Admin: Display consent + audit info

    Admin->>AC: update_consent(consent_id, consent_given)
    AC->>CC: Update consent record
    CC->>DB: Update consent
    CC->>CA: Log audit entry (action="consent_updated")
    CA->>DB: Store audit log
    AC-->>Admin: Confirmation
```

## Anything UNCLEAR

- Legal jurisdictions to support (GDPR, CCPA, etc.) need clarification.
- Should consent be versioned if Terms & Conditions change?
- What reporting features are required for compliance audits?
- Is multi-language support required for Terms & Conditions?
