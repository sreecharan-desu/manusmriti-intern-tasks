import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { PRODUCTS } from "../data/products.js";

const CartContext = createContext(null);
const STORAGE_KEY = "catalog.cart.v1";

function loadLines() {
  try {
    const raw = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    if (!Array.isArray(raw)) return [];
    return raw
      .map((entry) => {
        const product = PRODUCTS.find((item) => item.id === entry.id);
        const quantity = Number(entry.quantity);
        if (!product || !Number.isFinite(quantity) || quantity < 1) return null;
        return { product, quantity: Math.min(99, Math.floor(quantity)) };
      })
      .filter(Boolean);
  } catch {
    return [];
  }
}

export function CartProvider({ children }) {
  const [lines, setLines] = useState(loadLines);

  useEffect(() => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(lines.map((line) => ({ id: line.product.id, quantity: line.quantity }))),
    );
  }, [lines]);

  const value = useMemo(() => {
    const count = lines.reduce((sum, line) => sum + line.quantity, 0);
    const total = lines.reduce((sum, line) => sum + line.quantity * line.product.price, 0);

    function add(product) {
      setLines((current) => {
        const existing = current.find((line) => line.product.id === product.id);
        if (existing) {
          return current.map((line) =>
            line.product.id === product.id ? { ...line, quantity: Math.min(99, line.quantity + 1) } : line,
          );
        }
        return [...current, { product, quantity: 1 }];
      });
    }

    function setQuantity(productId, quantity) {
      setLines((current) => {
        if (quantity <= 0) return current.filter((line) => line.product.id !== productId);
        return current.map((line) =>
          line.product.id === productId ? { ...line, quantity: Math.min(99, quantity) } : line,
        );
      });
    }

    function clear() {
      setLines([]);
    }

    return { lines, count, total, add, setQuantity, clear };
  }, [lines]);

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used inside CartProvider");
  return ctx;
}
