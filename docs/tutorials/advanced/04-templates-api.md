# Templates API (Advanced)

Manage reusable artifact templates through the versioned API.

## Endpoint summary

- `POST /api/v1/templates`
- `GET /api/v1/templates`
- `GET /api/v1/templates/{template_id}`
- `PUT /api/v1/templates/{template_id}`
- `DELETE /api/v1/templates/{template_id}`

Legacy equivalents are also available under `/templates/*`, but new integrations should prefer `/api/v1/*`.

## 1) Create a template

```bash
curl -s -X POST http://localhost:8000/api/v1/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Project Charter Template",
    "description": "Baseline charter structure for early planning.",
    "schema": {
      "type": "object",
      "properties": {
        "project_name": { "type": "string" },
        "sponsor": { "type": "string" }
      },
      "required": ["project_name", "sponsor"]
    },
    "markdown_template": "# {{ project_name }}\\n\\nSponsor: {{ sponsor }}",
    "artifact_type": "pmp",
    "version": "1.0.0"
  }' | jq .
```

## 2) List templates

```bash
curl -s http://localhost:8000/api/v1/templates | jq .
```

## 3) Get template by ID

```bash
curl -s http://localhost:8000/api/v1/templates/<template-id> | jq .
```

## 4) Update template

```bash
curl -s -X PUT http://localhost:8000/api/v1/templates/<template-id> \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated charter template for gated planning reviews.",
    "version": "1.1.0"
  }' | jq .
```

## 5) Delete template

```bash
curl -i -X DELETE http://localhost:8000/api/v1/templates/<template-id>
```

Expected success status: `204 No Content`.

## Notes

- Allowed `artifact_type` values are: `pmp`, `raid`, `blueprint`, `proposal`, `report`.
- `schema` must include at least a top-level `type` key.

---

**Last Updated:** 2026-02-17
