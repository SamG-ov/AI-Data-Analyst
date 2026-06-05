"use client";

import { useEffect, useState } from "react";
import { generateInsights } from "@/lib/api";

interface InsightsProps {
  datasetId: string;
}

export default function Insights({ datasetId }: InsightsProps) {
  const [report, setReport] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Clear when the dataset changes (e.g. after cleaning).
  useEffect(() => {
    setReport(null);
    setError(null);
  }, [datasetId]);

  async function run() {
    setIsLoading(true);
    setError(null);
    try {
      const result = await generateInsights(datasetId);
      setReport(result.report);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to generate insights");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="w-full max-w-4xl rounded-lg border border-gray-200 p-5 dark:border-gray-700">
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-widest text-gray-400">
        AI insights
      </h3>

      <button
        onClick={run}
        disabled={isLoading}
        className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-60"
      >
        {isLoading
          ? "Analyzing…"
          : report
            ? "Regenerate insights"
            : "Generate insights"}
      </button>

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

      {report && (
        <div className="mt-4 rounded-md bg-gray-50 p-4 text-sm leading-relaxed whitespace-pre-wrap dark:bg-gray-800">
          {report}
        </div>
      )}

      <p className="mt-3 text-xs text-gray-400">
        AI-generated from your dataset&apos;s schema, summary statistics, and a
        sample of rows. Review before making decisions.
      </p>
    </div>
  );
}
