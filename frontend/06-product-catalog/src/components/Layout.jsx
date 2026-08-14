import { NavLink } from "react-router-dom";
import { useCart } from "../cart/CartContext.jsx";
import { formatPrice } from "../data/products.js";

export function Layout({ children }) {
  const { count, total } = useCart();
  return (
    <div className="shell">
      <header className="nav">
        <NavLink to="/" className="brand" end>
          Northwind
        </NavLink>
        <nav>
          <NavLink to="/products">Catalog</NavLink>
          <NavLink to="/cart">
            Cart{count ? ` · ${count}` : ""}
            {count ? <span className="nav-total">{formatPrice(total)}</span> : null}
          </NavLink>
        </nav>
      </header>
      {children}
    </div>
  );
}
