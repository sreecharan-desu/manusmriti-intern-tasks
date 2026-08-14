export function IconKey() {
  return (
    <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
      <circle cx="8" cy="14" r="4" />
      <path d="M12 14h9v3h-3v-3" />
    </svg>
  );
}

export function IconUser() {
  return (
    <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
      <circle cx="12" cy="8" r="3.5" />
      <path d="M5 19c1.2-3 3.6-4.5 7-4.5S17.8 16 19 19" />
    </svg>
  );
}

export function IconPlus() {
  return (
    <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
      <path d="M12 5v14M5 12h14" />
    </svg>
  );
}

export function blurDock(event) {
  event.currentTarget.blur();
}
