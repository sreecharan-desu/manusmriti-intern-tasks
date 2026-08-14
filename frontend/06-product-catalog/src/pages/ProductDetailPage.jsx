import { Link, useParams } from "react-router-dom";
import { useCart } from "../cart/CartContext.jsx";
import { CATEGORY_COLOR, PRODUCTS, formatPrice } from "../data/products.js";

export function ProductDetailPage() {
  const { id } = useParams();
  const { add } = useCart();
  const product = PRODUCTS.find((item) => String(item.id) === id);

  if (!product) {
    return (
      <main className="page">
        <h1>product not found</h1>
        <Link to="/products">back to catalog</Link>
      </main>
    );
  }

  return (
    <main className="page detail">
      <span className="swatch wide" style={{ background: CATEGORY_COLOR[product.category] }} />
      <p className="crumb">
        <Link to="/products">catalog</Link>
        <span aria-hidden="true"> / </span>
        {product.title}
      </p>
      <p className="eyebrow">{product.category}</p>
      <h1>{product.title}</h1>
      <p className="lede">{product.description}</p>
      <p className="price">{formatPrice(product.price)}</p>
      <button type="button" className="button" onClick={() => add(product)}>
        add to cart
      </button>
    </main>
  );
}
