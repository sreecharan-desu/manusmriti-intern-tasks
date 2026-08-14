export const PRODUCTS = [
  {
    id: 1,
    title: "Mechanical Keyboard",
    price: 8499,
    category: "electronics",
    description: "Hot-swap 75% layout, gasket mount, south-facing RGB.",
  },
  {
    id: 2,
    title: "USB-C Hub",
    price: 2499,
    category: "electronics",
    description: "HDMI 4K, SD/microSD, two USB-A ports, 100W passthrough.",
  },
  {
    id: 3,
    title: "Wool Crewneck",
    price: 4299,
    category: "clothing",
    description: "Heavyweight merino. Cut for layering, not shrinking.",
  },
  {
    id: 4,
    title: "Canvas Tote",
    price: 1299,
    category: "clothing",
    description: "16oz canvas, one interior pocket, unbranded hardware.",
  },
  {
    id: 5,
    title: "Desk Lamp",
    price: 3199,
    category: "home",
    description: "Warm LED, dimmable, USB-C powered. No wall wart.",
  },
  {
    id: 6,
    title: "Ceramic Mug",
    price: 799,
    category: "home",
    description: "350ml matte glaze. Dishwasher safe.",
  },
  {
    id: 7,
    title: "Closed-back Headphones",
    price: 11999,
    category: "electronics",
    description: "30-hour battery, USB-C, analog fallback.",
  },
  {
    id: 8,
    title: "Linen Shirt",
    price: 3499,
    category: "clothing",
    description: "Relaxed fit. Two colours, one pocket.",
  },
  {
    id: 9,
    title: "Plant Pot",
    price: 899,
    category: "home",
    description: "12cm terracotta with a matching saucer.",
  },
  {
    id: 10,
    title: "1080p Webcam",
    price: 4599,
    category: "electronics",
    description: "Privacy shutter, clip or tripod mount.",
  },
  {
    id: 11,
    title: "Running Shorts",
    price: 1899,
    category: "clothing",
    description: "5-inch inseam, zip pocket, lined.",
  },
  {
    id: 12,
    title: "Throw Blanket",
    price: 2499,
    category: "home",
    description: "Cotton knit. Machine wash, no pills after week one.",
  },
];

export const CATEGORIES = ["all", "electronics", "clothing", "home"];

export const CATEGORY_COLOR = {
  electronics: "#1f7a6c",
  clothing: "#e25a2a",
  home: "#e0a21b",
};

export function formatPrice(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}
