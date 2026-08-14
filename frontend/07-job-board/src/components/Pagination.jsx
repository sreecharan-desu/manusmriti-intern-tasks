export function Pagination({ page, pageCount, onPage }) {
  return (
    <nav className="pager" aria-label="pagination">
      <button type="button" className="ghost" disabled={page === 1} onClick={() => onPage(page - 1)}>
        previous
      </button>
      {Array.from({ length: pageCount }, (_, index) => index + 1).map((number) => (
        <button
          key={number}
          type="button"
          className={number === page ? "active" : "ghost"}
          onClick={() => onPage(number)}
        >
          {number}
        </button>
      ))}
      <button type="button" className="ghost" disabled={page === pageCount} onClick={() => onPage(page + 1)}>
        next
      </button>
    </nav>
  );
}
