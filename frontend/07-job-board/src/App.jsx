import { useEffect, useMemo, useState } from "react";
import { JobCard } from "./components/JobCard.jsx";
import { Pagination } from "./components/Pagination.jsx";
import { SavedList } from "./components/SavedList.jsx";
import { SearchBar } from "./components/SearchBar.jsx";
import { JOBS } from "./data/jobs.js";
import { useDebouncedValue } from "./hooks/useDebouncedValue.js";
import { useSavedJobs } from "./hooks/useSavedJobs.js";
import { filterJobs, paginate } from "./lib/filterJobs.js";

const PAGE_SIZE = 10;

export default function App() {
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const { savedIds, toggleSave } = useSavedJobs();
  const debouncedQuery = useDebouncedValue(query, 500);

  useEffect(() => {
    setPage(1);
  }, [debouncedQuery]);

  const filtered = useMemo(() => filterJobs(JOBS, debouncedQuery), [debouncedQuery]);
  const { visible, currentPage, pageCount } = paginate(filtered, page, PAGE_SIZE);
  const savedJobs = JOBS.filter((job) => savedIds.includes(job.id));

  return (
    <main className="page">
      <header className="hero">
        <p className="eyebrow">50 roles · local data</p>
        <h1>Job board</h1>
        <p className="lede">
          Search is debounced 500ms so typing does not thrash the list. Ten jobs per page. Saved roles live in
          localStorage.
        </p>
        <SearchBar value={query} onChange={setQuery} pending={query !== debouncedQuery} />
        <p className="muted">
          {filtered.length} match{filtered.length === 1 ? "" : "es"}
          {debouncedQuery ? ` for “${debouncedQuery}”` : ""}
        </p>
      </header>
      {visible.length === 0 ? (
        <p className="empty">No roles match that search.</p>
      ) : (
        <ul className="jobs">
          {visible.map((job) => (
            <JobCard key={job.id} job={job} saved={savedIds.includes(job.id)} onToggle={toggleSave} />
          ))}
        </ul>
      )}
      {pageCount > 1 ? <Pagination page={currentPage} pageCount={pageCount} onPage={setPage} /> : null}
      <SavedList jobs={savedJobs} onToggle={toggleSave} />
    </main>
  );
}
