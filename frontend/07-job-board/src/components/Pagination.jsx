export function Pagination({ page, pageCount, onPage }) {
  return (
    <nav className="pager" aria-label="Pagination">
      <button type="button" disabled={page === 1} onClick={() => onPage(page - 1)}>
        Previous
      </button>
      {Array.from({ length: pageCount }, (_, index) => index + 1).map((number) => (
        <button
          key={number}
          type="button"
          className={number === page ? "active" : ""}
          onClick={() => onPage(number)}
        >
          {number}
        </button>
      ))}
      <button type="button" disabled={page === pageCount} onClick={() => onPage(page + 1)}>
        Next
      </button>
    </nav>
  );
}
