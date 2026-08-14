export function SearchBar({ value, onChange, pending }) {
  return (
    <div className="search">
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Title, company, location, or skill"
        aria-label="Search jobs"
      />
      {pending ? (
        <p className="muted" role="status">
          Waiting for typing to stop…
        </p>
      ) : null}
    </div>
  );
}
