import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useCart } from "../cart/CartContext.jsx";
import { CATEGORIES, CATEGORY_COLOR, PRODUCTS, formatPrice } from "../data/products.js";

export function ProductsPage() {
  const { add } = useCart();
  const [category, setCategory] = useState("all");
  const [sort, setSort] = useState("price-asc");

  const visible = useMemo(() => {
    const filtered = PRODUCTS.filter((item) => category === "all" || item.category === category);
    return [...filtered].sort((a, b) => (sort === "price-asc" ? a.price - b.price : b.price - a.price));
  }, [category, sort]);

  return (
    <main className="page">
      <header className="page-head">
        <div>
          <p className="mono">Catalog</p>
          <h1>Products</h1>
        </div>
        <div className="controls">
          <label>
            Category
            <select value={category} onChange={(event) => setCategory(event.target.value)}>
              {CATEGORIES.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label>
            Sort
            <select value={sort} onChange={(event) => setSort(event.target.value)}>
              <option value="price-asc">Price · low to high</option>
              <option value="price-desc">Price · high to low</option>
            </select>
          </label>
        </div>
      </header>
      <ul className="grid">
        {visible.map((product) => (
          <li key={product.id} className="card">
            <span className="swatch" style={{ background: CATEGORY_COLOR[product.category] }} />
            <p className="eyebrow">{product.category}</p>
            <h2>
              <Link to={`/products/${product.id}`}>{product.title}</Link>
            </h2>
            <p className="lede tight">{product.description}</p>
            <div className="row">
              <strong>{formatPrice(product.price)}</strong>
              <button type="button" onClick={() => add(product)}>
                Add to cart
              </button>
            </div>
          </li>
        ))}
      </ul>
    </main>
  );
}
