import { NavLink } from "react-router-dom";
import { useCart } from "../cart/CartContext.jsx";
import { formatPrice } from "../data/products.js";
import { SiteFooter } from "./SiteFooter.jsx";

export function Layout({ children }) {
  const { count, total } = useCart();

  return (
    <div className="app">
      <header className="topnav">
        <div className="nav-inner">
          <NavLink to="/" className="brand" end>
            Northwind
          </NavLink>
          <nav aria-label="Primary">
            <NavLink to="/products">Catalog</NavLink>
            <NavLink to="/cart">
              Cart{count ? ` · ${count}` : ""}
              {count ? <span className="nav-total">{formatPrice(total)}</span> : null}
            </NavLink>
          </nav>
        </div>
      </header>
      <div className="shell">
        {children}
        <SiteFooter note="Cart stays across routes and refresh" />
      </div>
    </div>
  );
}
