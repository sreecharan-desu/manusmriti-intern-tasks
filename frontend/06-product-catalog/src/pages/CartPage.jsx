import { Link } from "react-router-dom";
import { useCart } from "../cart/CartContext.jsx";
import { formatPrice } from "../data/products.js";

export function CartPage() {
  const { lines, total, setQuantity, clear } = useCart();

  return (
    <main className="page">
      <header className="page-head">
        <div>
          <p className="mono">checkout</p>
          <h1>cart</h1>
        </div>
        {lines.length > 0 ? (
          <button type="button" className="ghost" onClick={clear}>
            clear
          </button>
        ) : null}
      </header>
      {lines.length === 0 ? (
        <p className="lede">
          cart is empty. <Link to="/products">browse products</Link>
        </p>
      ) : (
        <>
          <ul className="cart-list">
            {lines.map((line) => (
              <li key={line.product.id}>
                <div>
                  <Link to={`/products/${line.product.id}`}>{line.product.title}</Link>
                  <p className="lede tight">{formatPrice(line.product.price)} each</p>
                </div>
                <label>
                  qty
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
          <p className="total">total {formatPrice(total)}</p>
        </>
      )}
    </main>
  );
}
