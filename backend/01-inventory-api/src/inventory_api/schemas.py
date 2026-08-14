from pydantic import BaseModel, Field, field_validator


class ProductIn(BaseModel):
    product_name: str = Field(min_length=1, max_length=120)
    sku: str = Field(min_length=1, max_length=64)
    price: float = Field(ge=0)
    stock_quantity: int = Field(ge=0)
    category: str = Field(min_length=1, max_length=64)

    @field_validator("product_name", "category")
    @classmethod
    def strip_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned


class ProductOut(ProductIn):
    id: int


class ProductList(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[ProductOut]
