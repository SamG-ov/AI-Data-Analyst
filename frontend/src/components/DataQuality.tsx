"use client";

import { useEffect, useState } from "react";
import {
  cleanDataset,
  getQualityReport,
  type CleanResult,
  type QualityReport,
} from "@/lib/api";

interface DataQualityProps {
  datasetId: string;
  /** Called with the cleaned dataset + actions after a successful clean. */
  onCleaned: (result: CleanResult) => void;
}

export default function DataQuality({ datasetId, onCleaned }: DataQualityProps) {
  const [report, setReport] = useState<QualityReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isCleaning, setIsCleaning] = useState(false);

  // Re-fetch whenever the dataset changes (e.g. after cleaning produces a new id).
  useEffect(() => {
    let cancelled = false;
    setReport(null);
    setError(null);
    getQualityReport(datasetId)
      .then((r) => {
        if (!cancelled) setReport(r);
      })
      .catch((e: unknown) => {
        if (!cancelled)
          setError(e instanceof Error ? e.message : "Failed to load report");
      });
    return () => {
      cancelled = true;
    };
  }, [datasetId]);

  async function handleClean() {
    setIsCleaning(true);
    setError(null);
    try {
      onCleaned(await cleanDataset(datasetId));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Clean failed");
    } finally {
      setIsCleaning(false);
    }
  }

  if (error) return <p className="w-full max-w-4xl text-sm text-red-600">{error}</p>;
  if (!report)
    return (
      <p className="w-full max-w-4xl text-sm text-gray-500">
        Analyzing data quality…
      </p>
    );

  const columnsWithMissing = report.columns.filter((c) => c.missing > 0);
  const hasIssues =
    report.duplicate_rows > 0 || report.total_missing > 0;

  return (
    <div className="w-full max-w-4xl rounded-lg border border-gray-200 p-5 dark:border-gray-700">
      <h3 className="mb-4 text-xs font-semibold uppercase tracking-widest text-gray-400">
        Data quality
      </h3>

      <div className="flex flex-wrap gap-8">
        <Stat label="Duplicate rows" value={report.duplicate_rows} />
        <Stat label="Missing values" value={report.total_missing} />
        <Stat label="Columns w/ missing" value={columnsWithMissing.length} />
      </div>

      {columnsWithMissing.length > 0 && (
        <ul className="mt-4 space-y-1 text-sm text-gray-600 dark:text-gray-300">
          {columnsWithMissing.map((c) => (
            <li key={c.name}>
              <span className="font-medium">{c.name}</span>: {c.missing} missing (
              {c.missing_pct}%)
            </li>
          ))}
        </ul>
      )}

      <button
        onClick={handleClean}
        disabled={isCleaning}
        className="mt-5 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:opacity-60"
      >
        {isCleaning ? "Cleaning…" : "Auto-clean dataset"}
      </button>

      {!hasIssues && (
        <p className="mt-2 text-xs text-gray-400">
          No duplicates or missing values detected.
        </p>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="text-2xl font-semibold">{value.toLocaleString()}</div>
      <div className="text-xs text-gray-400">{label}</div>
    </div>
  );
}
