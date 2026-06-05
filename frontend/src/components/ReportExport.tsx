"use client";

import { useState } from "react";
import { fetchReport } from "@/lib/api";

interface ReportExportProps {
  datasetId: string;
}

export default function ReportExport({ datasetId }: ReportExportProps) {
  const [includeInsights, setIncludeInsights] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleDownload() {
    setIsLoading(true);
    setError(null);
    try {
      const blob = await fetchReport(datasetId, includeInsights);
      // Turn the Blob into a temporary URL and click an invisible link.
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "data-analysis-report.html";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to generate report");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="w-full max-w-4xl rounded-lg border border-gray-200 p-5 dark:border-gray-700">
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-widest text-gray-400">
        Export report
      </h3>

      <div className="flex flex-wrap items-center gap-4">
        <button
          onClick={handleDownload}
          disabled={isLoading}
          className="rounded-md bg-gray-800 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-gray-900 disabled:opacity-60 dark:bg-gray-200 dark:text-gray-900 dark:hover:bg-white"
        >
          {isLoading ? "Preparing…" : "Download report"}
        </button>

        <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
          <input
            type="checkbox"
            checked={includeInsights}
            onChange={(e) => setIncludeInsights(e.target.checked)}
            disabled={isLoading}
          />
          Include AI insights (requires API key; slower)
        </label>
      </div>

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

      <p className="mt-3 text-xs text-gray-400">
        Downloads a self-contained HTML file (stats, charts, preview). Open it in
        any browser, or use Print → Save as PDF.
      </p>
    </div>
  );
}
