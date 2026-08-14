# File upload API

Multipart JPEG/PNG uploads to local disk. 5MB cap. Type is sniffed from magic bytes so a renamed `.png` PDF is rejected.

```bash
uv sync --dev
uv run pytest -q
uv run upload-api
```

`POST /uploads` with form field `file` → metadata + `/files/{uuid}.png`.

| Status | When |
| --- | --- |
| `201` | stored |
| `400` | empty file |
| `413` | over 5MB |
| `415` | not JPEG/PNG |
| `404` | unknown id |

Env: `UPLOAD_DB_PATH`, `UPLOAD_STORAGE_DIR`.
