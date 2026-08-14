import { Link } from "react-router-dom";
import { useCart } from "../cart/CartContext.jsx";
import { formatPrice } from "../data/products.js";

export function CartPage() {
  const { lines, total, setQuantity, clear } = useCart();

  return (
    <main className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">Checkout</p>
          <h1>Cart</h1>
        </div>
        {lines.length > 0 ? (
          <button type="button" className="ghost" onClick={clear}>
            Clear
          </button>
        ) : null}
      </header>
      {lines.length === 0 ? (
        <p className="muted">
          Cart is empty. <Link to="/products">Browse products</Link>
        </p>
      ) : (
        <>
          <ul className="cart-list">
            {lines.map((line) => (
              <li key={line.product.id}>
                <div>
                  <Link to={`/products/${line.product.id}`}>{line.product.title}</Link>
                  <p className="muted">{formatPrice(line.product.price)} each</p>
                </div>
                <label>
                  Qty
                  <input
                    type="number"
                    min="0"
                    max="99"
                    value={line.quantity}
                    onChange={(event) => setQuantity(line.product.id, Number(event.target.value))}
                  />
                </label>
                <strong>{formatPrice(line.product.price * line.quantity)}</strong>
              </li>
            ))}
          </ul>
          <p className="total">Total {formatPrice(total)}</p>
        </>
      )}
    </main>
  );
}
