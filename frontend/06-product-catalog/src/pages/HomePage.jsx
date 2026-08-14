import { Link } from "react-router-dom";
import { PRODUCTS, formatPrice } from "../data/products.js";

export function HomePage() {
  const featured = PRODUCTS.slice(0, 3);
  return (
    <main className="page">
      <section className="hero">
        <p className="eyebrow">Local catalog</p>
        <h1>Twelve products. One cart. Routes that keep state.</h1>
        <p className="lede">
          Filter by category, sort by price, open a product, add it to a cart that survives navigation and
          refresh.
        </p>
        <Link className="button" to="/products">
          Browse the catalog
        </Link>
      </section>
      <ul className="grid">
        {featured.map((product) => (
          <li key={product.id} className="card">
            <p className="eyebrow">{product.category}</p>
            <h2>
              <Link to={`/products/${product.id}`}>{product.title}</Link>
            </h2>
            <p>{formatPrice(product.price)}</p>
          </li>
        ))}
      </ul>
    </main>
  );
}
