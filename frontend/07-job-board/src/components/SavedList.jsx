export function SavedList({ jobs, onToggle }) {
  return (
    <section className="saved">
      <h2>Saved for later ({jobs.length})</h2>
      {jobs.length === 0 ? (
        <p className="muted">Nothing saved yet. Bookmarks persist across reloads.</p>
      ) : (
        <ul>
          {jobs.map((job) => (
            <li key={job.id}>
              <span>
                {job.title} — {job.company}
              </span>
              <button type="button" className="ghost" onClick={() => onToggle(job.id)}>
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
