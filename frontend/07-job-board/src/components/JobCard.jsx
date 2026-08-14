const TYPE_COLOR = {
  "Full-time": "#0e7c8b",
  Internship: "#7b6cff",
  Contract: "#e05a72",
  "Part-time": "#e0a21b",
};

export function JobCard({ job, saved, onToggle }) {
  return (
    <li className="job">
      <span className="swatch" style={{ background: TYPE_COLOR[job.type] || "#0e7c8b" }} />
      <div>
        <p className="eyebrow">{job.tag}</p>
        <h2>{job.title}</h2>
        <p className="lede tight">
          {job.company} · {job.location} · {job.type}
        </p>
      </div>
      <button type="button" className={saved ? "saved" : "ghost"} onClick={() => onToggle(job.id)}>
        {saved ? "Saved" : "Save"}
      </button>
    </li>
  );
}
