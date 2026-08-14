import { NavLink } from "react-router-dom";
import { useCart } from "../cart/CartContext.jsx";
import { formatPrice } from "../data/products.js";
import { SiteFooter } from "./SiteFooter.jsx";

export function Layout({ children }) {
  const { count, total } = useCart();

  return (
    <div className="shell">
      <header className="topnav">
        <NavLink to="/" className="brand" end>
          northwind
        </NavLink>
        <nav aria-label="primary">
          <NavLink to="/products">catalog</NavLink>
          <NavLink to="/cart">
            cart{count ? ` · ${count}` : ""}
            {count ? <span className="nav-total">{formatPrice(total)}</span> : null}
          </NavLink>
        </nav>
      </header>
      {children}
      <SiteFooter note="cart stays across routes and refresh" />
    </div>
  );
}
