export function SearchBar({ value, onChange, pending }) {
  return (
    <div className="search">
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="title, company, location, or skill"
        aria-label="search jobs"
      />
      {pending ? (
        <p className="mono" role="status">
          waiting for typing to stop…
        </p>
      ) : null}
    </div>
  );
}
