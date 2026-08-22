# Product catalog

React Router shop: home, listing, detail (`/products/:id`), category filter, price sort, cart that survives routes and refresh.

```bash
npm install
npm run dev
```

http://127.0.0.1:5175

Cart quantities are stored in `localStorage` as `{ id, quantity }` and rehydrated from the catalog so prices stay source-of-truth.
