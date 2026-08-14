export function JobCard({ job, saved, onToggle }) {
  return (
    <li className="job">
      <div>
        <p className="eyebrow">{job.tag}</p>
        <h2>{job.title}</h2>
        <p>
          {job.company} · {job.location} · {job.type}
        </p>
      </div>
      <button type="button" className={saved ? "saved" : "ghost"} onClick={() => onToggle(job.id)}>
        {saved ? "Saved" : "Save"}
      </button>
    </li>
  );
}
