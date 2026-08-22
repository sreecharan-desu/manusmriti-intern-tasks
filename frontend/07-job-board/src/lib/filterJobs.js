export function filterJobs(jobs, query) {
  const needle = query.trim().toLowerCase();
  if (!needle) return jobs;
  return jobs.filter((job) =>
    [job.title, job.company, job.location, job.tag, job.type].join(" ").toLowerCase().includes(needle),
  );
}

export function paginate(items, page, pageSize) {
  const pageCount = Math.max(1, Math.ceil(items.length / pageSize));
  const currentPage = Math.min(page, pageCount);
  const visible = items.slice((currentPage - 1) * pageSize, currentPage * pageSize);
  return { visible, currentPage, pageCount };
}
