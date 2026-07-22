

# CQSTS Backend API Documentation

**Base URL (Docker):** `http://localhost/api/v1`  
**Base URL (Dev):** `http://localhost:8000/api/v1`  
**Swagger UI:** `http://localhost/api/docs/`  
**Auth:** Bearer JWT token in every request header except login

---

## Authentication

### Login
```
POST /auth/login/
```
**Body:**
```json
{
  "email": "admin@qcsts.com",
  "password": "yourpassword"
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "access": "<JWT access token — valid 15 min>",
    "refresh": "<JWT refresh token — valid 8 hours>",
    "user": {
      "id": "uuid",
      "email": "admin@qcsts.com",
      "full_name": "Admin",
      "role": "admin",
      "is_active": true,
      "created_at": "2026-01-01T00:00:00Z"
    }
  }
}
```
**Store:** `localStorage.setItem("qc_access_token", data.access)`  
**Store:** `localStorage.setItem("qc_refresh_token", data.refresh)`

---

### Refresh Token
```
POST /auth/token/refresh/
```
**Body:**
```json
{ "refresh": "<refresh token>" }
```
**Response:**
```json
{ "access": "<new access token>" }
```
Call this automatically when any request returns 401.

---

### Logout
```
POST /auth/logout/
Header: Authorization: Bearer <access_token>
```
**Body:**
```json
{ "refresh": "<refresh token>" }
```

---

### Get Current User
```
GET /auth/me/
Header: Authorization: Bearer <access_token>
```
**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@qcsts.com",
    "full_name": "Ahmed Ali",
    "role": "analyst",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z"
  }
}
```

---

### User Management (Admin only)

**List all users:**
```
GET /auth/users/
```

**Create user:**
```
POST /auth/users/
```
```json
{
  "email": "analyst@qcsts.com",
  "full_name": "Ahmed Ali",
  "role": "analyst",
  "password": "SecurePass123!"
}
```
Roles: `admin` | `qa_manager` | `supervisor` | `analyst`

**Update user:**
```
PATCH /auth/users/<uuid>/
```

**Deactivate user:**
```
DELETE /auth/users/<uuid>/
```

**Change password:**
```
POST /auth/change-password/
```
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewPass123!"
}
```

---

## Products & Monographs

### Monographs

**List all:**
```
GET /products/monographs/
```
**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "BP Monograph – Antibiotics",
      "version": "2.1",
      "effective_date": "2024-01-01",
      "status": "approved",
      "approved_by": "uuid",
      "approved_by_name": "Dr. Karim",
      "approved_at": "2024-01-15T10:00:00Z",
      "tests": [
        {
          "id": "uuid",
          "name": "Assay",
          "method": "HPLC",
          "specification": "98.0 - 102.0",
          "unit": "%",
          "sequence": 1
        }
      ],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**Create monograph:**
```
POST /products/monographs/
```
```json
{
  "name": "BP Monograph – Antibiotics",
  "version": "2.1",
  "effective_date": "2024-01-01",
  "status": "draft"
}
```

**Get single:**
```
GET /products/monographs/<uuid>/
```

**Update (only if draft):**
```
PATCH /products/monographs/<uuid>/
```

**Approve (QA Manager only):**
```
POST /products/monographs/<uuid>/approve/
```
No body needed. Once approved, monograph is locked — no further edits.

---

### Monograph Tests

**List tests for a monograph:**
```
GET /products/monographs/<uuid>/tests/
```

**Add test (only if monograph is draft):**
```
POST /products/monographs/<uuid>/tests/
```
```json
{
  "name": "Assay",
  "method": "HPLC Method A",
  "specification": "98.0 - 102.0",
  "unit": "%",
  "sequence": 1
}
```
Specification formats supported:
- Range: `"98.0 - 102.0"` or `"98.0% - 102.0%"`
- Not Less Than: `"NLT 75"`
- Not More Than: `"NMT 5.0"`
- Exact: `"7.0"`

---

### Products

**List all:**
```
GET /products/
```
**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Amoxicillin Capsules",
      "strength": "500 mg",
      "dosage_form": "capsule",
      "description": "Broad-spectrum antibiotic",
      "monograph": "uuid",
      "monograph_name": "BP Monograph – Antibiotics v2.1",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**Create product:**
```
POST /products/
```
```json
{
  "name": "Amoxicillin Capsules",
  "strength": "500 mg",
  "dosage_form": "capsule",
  "description": "Broad-spectrum antibiotic",
  "monograph": "<monograph_uuid>"
}
```
Dosage forms: `tablet` | `capsule` | `syrup` | `injection` | `cream` | `ointment` | `gel` | `suppository` | `suspension` | `solution`

**Get / Update:**
```
GET  /products/<uuid>/
PATCH /products/<uuid>/
```

---

## Batches

### Create Batch (auto-generates test schedule)
```
POST /batches/
```
```json
{
  "product": "<product_uuid>",
  "batch_number": "AMX-2024-001",
  "mfg_date": "2024-01-10",
  "expiry_date": "2027-01-10",
  "incubation_date": "2024-02-01",
  "study_type": "long_term",
  "shelf": "S1",
  "rack": "R2",
  "position": "P1",
  "qty_placed": 60
}
```
Study types: `long_term` | `accelerated`

**Response includes test_points array — auto-generated by system:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "batch_number": "AMX-2024-001",
    "product_name": "Amoxicillin Capsules 500 mg",
    "study_type": "long_term",
    "status": "active",
    "location": "S1/R2/P1",
    "qty_placed": 60,
    "qty_remaining": 60,
    "test_points": [
      {
        "id": "uuid",
        "month": 0,
        "scheduled_date": "2024-02-01",
        "status": "pending",
        "completed_at": null
      },
      {
        "id": "uuid",
        "month": 3,
        "scheduled_date": "2024-05-01",
        "status": "pending",
        "completed_at": null
      }
    ]
  }
}
```

**Validation rules:**
- `incubation_date` must be >= `mfg_date`
- Product must have an approved monograph
- `batch_number` must be globally unique
- Chamber location (shelf+rack+position) must be unique

**List batches:**
```
GET /batches/
GET /batches/?status=active
GET /batches/?study_type=long_term
GET /batches/?product=<uuid>
```

**Get single:**
```
GET /batches/<uuid>/
```

---

## Test Points (Schedule)

Test points are **never created manually** — they are generated automatically when a batch is created.

**List:**
```
GET /test-points/
GET /test-points/?batch=<uuid>
GET /test-points/?status=pending
GET /test-points/?status=overdue
GET /test-points/?status=completed
GET /test-points/?status=failed
GET /test-points/?upcoming=true   ← due in next 30 days
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "batch": "uuid",
      "batch_number": "AMX-2024-001",
      "product_name": "Amoxicillin Capsules",
      "month": 3,
      "scheduled_date": "2024-05-01",
      "status": "pending",
      "completed_at": null,
      "created_at": "2024-02-01T00:00:00Z"
    }
  ]
}
```

**Statuses:**
- `pending` — not yet due or not yet tested
- `overdue` — past scheduled date, not tested (set automatically at 6AM daily)
- `completed` — all tests submitted and passed
- `failed` — all tests submitted, at least one failed

---

## Chamber

### View Chamber Inventory
```
GET /chamber/
GET /chamber/?study_type=long_term
```
Returns all active batches with location and quantity.

### Record Sample Pull
```
POST /chamber/pulls/
```
```json
{
  "batch": "<batch_uuid>",
  "test_point": "<test_point_uuid>",
  "qty_pulled": 5,
  "notes": "Pull for month 3 testing"
}
```
This automatically reduces `qty_remaining` on the batch.

**List pulls:**
```
GET /chamber/pulls/
GET /chamber/pulls/?batch=<uuid>
```

### Move Batch to New Location
```
POST /chamber/move/
```
```json
{
  "batch": "<batch_uuid>",
  "new_shelf": "S2",
  "new_rack": "R1",
  "new_position": "P3",
  "reason": "Reorganization"
}
```

### Location History
```
GET /chamber/locations/<batch_uuid>/
```

---

## Results (Electronic Signature Required)

### Step 1 — Get Signature Token
```
POST /results/signature/verify/
```
```json
{ "password": "your_password" }
```
**Response:**
```json
{
  "success": true,
  "data": { "signature_token": "uuid-token-here" },
  "message": "Signature verified. Token valid for 5 minutes."
}
```
Token expires in **5 minutes**. Store it temporarily.

### Step 2 — Submit Result
```
POST /results/
Header: X-Signature-Token: <signature_token>
```
```json
{
  "test_point": "<test_point_uuid>",
  "monograph_test": "<monograph_test_uuid>",
  "value": "99.5",
  "unit": "%",
  "notes": "Within specification"
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "test_name": "Assay",
    "value": "99.5",
    "unit": "%",
    "specification_snapshot": "98.0 - 102.0",
    "pass_fail": "pass",
    "analyst_name": "Ahmed Ali",
    "submitted_at": "2024-05-01T10:30:00Z"
  }
}
```
`pass_fail` is calculated automatically by the system.

When **all tests** for a test point are submitted, the test point status updates automatically:
- All pass → `completed`
- Any fail → `failed`

**List results:**
```
GET /results/
GET /results/?test_point=<uuid>
GET /results/?pass_fail=pass
GET /results/?pass_fail=fail
```

---

## Dashboard / Reports

```
GET /reports/dashboard/
```
**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_products": 5,
      "active_batches": 12,
      "overdue_tests": 3,
      "upcoming_tests": 7
    },
    "overdue_test_points": [
      {
        "id": "uuid",
        "batch_number": "AMX-2024-001",
        "product_name": "Amoxicillin Capsules",
        "month": 3,
        "scheduled_date": "2024-05-01",
        "status": "overdue"
      }
    ],
    "upcoming_test_points": [...],
    "failed_batches": [...],
    "active_batches": [
      {
        "id": "uuid",
        "batch_number": "AMX-2024-001",
        "product_name": "Amoxicillin Capsules",
        "study_type": "long_term",
        "location": "S1/R2/P1",
        "qty_remaining": 55
      }
    ]
  }
}
```

---

## Audit Trail (QA Manager / Admin only)

```
GET /audit/
GET /audit/?model_name=Batch
GET /audit/?action=UPDATE
GET /audit/?performed_by=<user_uuid>
GET /audit/?date_from=2024-01-01&date_to=2024-12-31
GET /audit/<uuid>/
```

---

## Standard Response Format

Every response follows this shape:

**Success:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

**Error:**
```json
{
  "success": false,
  "errors": {
    "field_name": ["Error message"],
    "non_field_errors": ["General error"]
  },
  "message": "Error description"
}
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Validation error |
| 401 | Not authenticated / token expired |
| 403 | No permission for this action |
| 404 | Record not found |
| 409 | Conflict (duplicate, already approved, etc.) |
| 422 | Business rule violation (e.g. insufficient quantity) |

---

## Role Permissions Summary

| Action | Analyst | Supervisor | QA Manager | Admin |
|--------|---------|------------|------------|-------|
| Login | ✅ | ✅ | ✅ | ✅ |
| View products/batches | ✅ | ✅ | ✅ | ✅ |
| Create product/batch | ✅ | ✅ | ✅ | ✅ |
| Submit results | ✅ | ✅ | ✅ | ✅ |
| Approve monograph | ❌ | ❌ | ✅ | ✅ |
| View audit trail | ❌ | ❌ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ❌ | ✅ |

---

## Quick Start for Frontend Developer

1. Start backend: `docker compose -f docker/docker-compose.yml up -d`
2. migrate the data base : `docker compose exec web python manage.py migrate`
3. create the admin user (frist user):`docker compose exec web python manage.py createsuperuser` # Use email: admin@qcsts.com, password: (your choice)
4. API available at: `http://localhost/api/v1/`
5. Swagger docs: `http://localhost/api/docs/`
6. Login with: `admin@qcsts.com` / `admin`
7. Use the access token in all subsequent requests:
   ``` 
   Authorization: Bearer <access_token>
   ```
8. When token expires (401), POST to `/auth/token/refresh/` with the refresh token
