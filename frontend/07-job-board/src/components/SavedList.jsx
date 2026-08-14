export function SavedList({ jobs, onToggle }) {
  return (
    <section className="saved-panel" id="saved">
      <h2>saved for later ({jobs.length})</h2>
      {jobs.length === 0 ? (
        <p className="lede">nothing saved yet. bookmarks persist across reloads.</p>
      ) : (
        <ul>
          {jobs.map((job) => (
            <li key={job.id}>
              <span>
                {job.title} — {job.company}
              </span>
              <button type="button" className="ghost" onClick={() => onToggle(job.id)}>
                remove
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
