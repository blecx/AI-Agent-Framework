# Blueprints API (Advanced)

Manage blueprint definitions that group required/optional templates and workflow requirements.

## Endpoint summary

- `POST /api/v1/blueprints`
- `GET /api/v1/blueprints`
- `GET /api/v1/blueprints/{blueprint_id}`
- `PUT /api/v1/blueprints/{blueprint_id}`
- `DELETE /api/v1/blueprints/{blueprint_id}`

Legacy equivalents also exist under `/blueprints/*`, but `/api/v1/*` is preferred for new automation.

## 1) Create a blueprint

```bash
curl -s -X POST http://localhost:8000/api/v1/blueprints \
  -H "Content-Type: application/json" \
  -d '{
    "id": "iso-core-v1",
    "name": "ISO Core Blueprint",
    "description": "Core planning + control artifact set.",
    "required_templates": ["project-charter", "project-plan"],
    "optional_templates": ["risk-register"],
    "workflow_requirements": ["initiating", "planning", "executing"]
  }' | jq .
```

## 2) List blueprints

```bash
curl -s http://localhost:8000/api/v1/blueprints | jq .
```

## 3) Get blueprint by ID

```bash
curl -s http://localhost:8000/api/v1/blueprints/iso-core-v1 | jq .
```

## 4) Update blueprint

```bash
curl -s -X PUT http://localhost:8000/api/v1/blueprints/iso-core-v1 \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Core planning + control artifact set (updated).",
    "optional_templates": ["risk-register", "decision-log"]
  }' | jq .
```

## 5) Delete blueprint

```bash
curl -i -X DELETE http://localhost:8000/api/v1/blueprints/iso-core-v1
```

Expected success status: `204 No Content`.

## Notes

- Blueprint IDs are client-provided at creation time.
- Use template IDs in `required_templates` and `optional_templates`.

---

**Last Updated:** 2026-02-17
