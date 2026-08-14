# Job board

Debounced search (500ms), 10 jobs per page, bookmarks in `localStorage`. Fifty local listings — no API.

```bash
npm install
npm run dev
```

http://127.0.0.1:5174

`useDebouncedValue` waits until typing stops. `filterJobs` is a pure function. Pagination clamps the current page when the result set shrinks.
