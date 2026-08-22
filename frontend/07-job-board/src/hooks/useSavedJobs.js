import { useEffect, useState } from "react";

const SAVE_KEY = "saved-job-ids";

function loadSaved() {
  try {
    return JSON.parse(localStorage.getItem(SAVE_KEY) || "[]");
  } catch {
    return [];
  }
}

export function useSavedJobs() {
  const [savedIds, setSavedIds] = useState(loadSaved);

  useEffect(() => {
    localStorage.setItem(SAVE_KEY, JSON.stringify(savedIds));
  }, [savedIds]);

  function toggleSave(id) {
    setSavedIds((current) => (current.includes(id) ? current.filter((item) => item !== id) : [...current, id]));
  }

  return { savedIds, toggleSave };
}
