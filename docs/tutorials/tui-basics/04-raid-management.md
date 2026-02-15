# RAID Management (TUI + REST)

The current TUI has no `raid` group. Manage RAID through REST endpoints.

## List RAID items

```bash
curl -s http://localhost:8000/projects/TODO-001/raid | jq .
```

## Create RAID item

```bash
curl -s -X POST http://localhost:8000/projects/TODO-001/raid \
  -H "Content-Type: application/json" \
  -d '{
    "type": "risk",
    "title": "Supplier delay impacts sprint",
    "description": "External dependency may slip by 1 week",
    "priority": "high",
    "status": "open",
    "owner": "PM"
  }' | jq .
```

## Update RAID item

```bash
curl -s -X PUT http://localhost:8000/projects/TODO-001/raid/<raid_id> \
  -H "Content-Type: application/json" \
  -d '{"status": "mitigated"}' | jq .
```

## Delete RAID item

```bash
curl -s -X DELETE http://localhost:8000/projects/TODO-001/raid/<raid_id> | jq .
```

## Versioned route equivalents
- `/api/v1/projects/TODO-001/raid`

---

**Last Updated:** 2026-02-16
