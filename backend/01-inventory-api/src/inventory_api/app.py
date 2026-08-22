from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlite3 import IntegrityError

from inventory_api.db import db, row_to_product
from inventory_api.schemas import ProductIn, ProductList, ProductOut
from inventory_api.settings import CORS_ORIGIN_REGEX, CORS_ORIGINS

app = FastAPI(
    title="Inventory API",
    description="CRUD inventory with unique SKUs, non-negative prices, and pagination.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=CORS_ORIGIN_REGEX,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def no_store(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("Cache-Control", "no-store")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    return response


@app.get("/health")
def health() -> dict:
    with db() as connection:
        connection.execute("SELECT 1").fetchone()
    return {"ok": True}


@app.get("/products", response_model=ProductList)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> ProductList:
    offset = (page - 1) * page_size
    with db() as connection:
        total = connection.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        rows = connection.execute(
            "SELECT * FROM products ORDER BY id LIMIT ? OFFSET ?",
            (page_size, offset),
        ).fetchall()
    return ProductList(
        page=page,
        page_size=page_size,
        total=total,
        items=[ProductOut.model_validate(row_to_product(row)) for row in rows],
    )


@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int) -> ProductOut:
    with db() as connection:
        row = connection.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductOut.model_validate(row_to_product(row))


@app.post("/products", status_code=status.HTTP_201_CREATED, response_model=ProductOut)
def create_product(body: ProductIn) -> ProductOut:
    with db() as connection:
        try:
            cursor = connection.execute(
                """
                INSERT INTO products (product_name, sku, price, stock_quantity, category)
                VALUES (?, ?, ?, ?, ?)
                """,
                (body.product_name, body.sku, body.price, body.stock_quantity, body.category),
            )
        except IntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SKU must be unique") from exc
        row = connection.execute("SELECT * FROM products WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return ProductOut.model_validate(row_to_product(row))


@app.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, body: ProductIn) -> ProductOut:
    with db() as connection:
        existing = connection.execute("SELECT id FROM products WHERE id = ?", (product_id,)).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Product not found")
        try:
            connection.execute(
                """
                UPDATE products
                SET product_name = ?, sku = ?, price = ?, stock_quantity = ?, category = ?
                WHERE id = ?
                """,
                (body.product_name, body.sku, body.price, body.stock_quantity, body.category, product_id),
            )
        except IntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SKU must be unique") from exc
        row = connection.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    return ProductOut.model_validate(row_to_product(row))


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int) -> None:
    with db() as connection:
        cursor = connection.execute("DELETE FROM products WHERE id = ?", (product_id,))
        deleted = cursor.rowcount
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Product not found")
