import { NavLink } from "react-router-dom";
import { useCart } from "../cart/CartContext.jsx";
import { SiteFooter } from "./SiteFooter.jsx";
import { IconBag, IconGrid, IconHome, blurDock } from "./icons.jsx";

export function Layout({ children }) {
  const { count } = useCart();

  return (
    <div className="shell">
      <div className="dock-wrap">
        <nav className="site-dock" aria-label="primary">
          <NavLink to="/" end className="dock-btn" aria-label="home" onPointerUp={blurDock}>
            <IconHome />
          </NavLink>
          <NavLink to="/products" className="dock-btn" aria-label="catalog" onPointerUp={blurDock}>
            <IconGrid />
          </NavLink>
          <span className="dock-divider" />
          <NavLink to="/cart" className="dock-btn" aria-label="cart" onPointerUp={blurDock}>
            <IconBag />
            {count ? <span className="dock-badge">{count}</span> : null}
          </NavLink>
        </nav>
      </div>
      {children}
      <SiteFooter note="cart stays across routes and refresh" />
    </div>
  );
}
