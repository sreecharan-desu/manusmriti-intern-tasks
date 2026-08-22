import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { filterJobs, paginate } from "./filterJobs.js";

const jobs = [
  { id: 1, title: "Backend Engineer", company: "Helios", location: "Guntur", type: "Full-time", tag: "Python" },
  { id: 2, title: "Frontend Engineer", company: "Northwind", location: "Hyderabad", type: "Full-time", tag: "React" },
];

describe("filterJobs", () => {
  it("matches title, company, location, and tag", () => {
    assert.equal(filterJobs(jobs, "helios").length, 1);
    assert.equal(filterJobs(jobs, "REACT").length, 1);
    assert.equal(filterJobs(jobs, "guntur").length, 1);
  });

  it("returns all jobs for a blank query", () => {
    assert.equal(filterJobs(jobs, "   ").length, 2);
  });
});

describe("paginate", () => {
  it("clamps the page when the list shrinks", () => {
    const result = paginate(jobs, 9, 1);
    assert.equal(result.currentPage, 2);
    assert.equal(result.visible.length, 1);
  });
});
