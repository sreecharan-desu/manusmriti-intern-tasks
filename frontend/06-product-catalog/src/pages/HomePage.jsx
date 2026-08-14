import { Link } from "react-router-dom";
import { CATEGORY_COLOR, PRODUCTS, formatPrice } from "../data/products.js";

export function HomePage() {
  const featured = PRODUCTS.slice(0, 3);
  return (
    <main className="page">
      <header className="hero">
        <p className="mono">Twelve products · local data</p>
        <h1>A small catalog with a cart that survives routes</h1>
        <p className="lede">
          Filter by category, sort by price, open a product, add it to the cart. Quantities persist after refresh.
        </p>
        <Link className="button" to="/products">
          Browse catalog
        </Link>
      </header>
      <ul className="grid">
        {featured.map((product) => (
          <li key={product.id} className="card">
            <span className="swatch" style={{ background: CATEGORY_COLOR[product.category] }} />
            <p className="eyebrow">{product.category}</p>
            <h2>
              <Link to={`/products/${product.id}`}>{product.title}</Link>
            </h2>
            <p className="price-line">{formatPrice(product.price)}</p>
          </li>
        ))}
      </ul>
    </main>
  );
}
