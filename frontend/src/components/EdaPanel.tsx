"use client";

import { useEffect, useState } from "react";
import {
  getCharts,
  getEda,
  type Chart,
  type EdaReport,
} from "@/lib/api";
import ChartCard from "@/components/ChartCard";

interface EdaPanelProps {
  datasetId: string;
}

export default function EdaPanel({ datasetId }: EdaPanelProps) {
  const [eda, setEda] = useState<EdaReport | null>(null);
  const [charts, setCharts] = useState<Chart[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset when the dataset changes (e.g. after cleaning).
  useEffect(() => {
    setEda(null);
    setCharts(null);
    setError(null);
  }, [datasetId]);

  async function runAnalysis() {
    setIsLoading(true);
    setError(null);
    try {
      const [edaResult, chartsResult] = await Promise.all([
        getEda(datasetId),
        getCharts(datasetId),
      ]);
      setEda(edaResult);
      setCharts(chartsResult.charts);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="w-full max-w-4xl">
      {!eda && (
        <button
          onClick={runAnalysis}
          disabled={isLoading}
          className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium transition-colors hover:bg-gray-50 disabled:opacity-60 dark:border-gray-600 dark:hover:bg-gray-800"
        >
          {isLoading ? "Analyzing…" : "Run EDA & charts"}
        </button>
      )}

      {error && <p className="text-sm text-red-600">{error}</p>}

      {eda && (
        <div className="space-y-8">
          {eda.numeric.length > 0 && <NumericTable rows={eda.numeric} />}
          {eda.categorical.length > 0 && (
            <CategoricalTable rows={eda.categorical} />
          )}

          {charts && charts.length > 0 && (
            <div>
              <h3 className="mb-3 text-xs font-semibold uppercase tracking-widest text-gray-400">
                Charts
              </h3>
              <div className="grid gap-4 sm:grid-cols-2">
                {charts.map((c) => (
                  <ChartCard key={c.column} chart={c} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function fmt(value: number | null): string {
  return value === null ? "—" : value.toLocaleString();
}

function NumericTable({ rows }: { rows: EdaReport["numeric"] }) {
  const headers = [
    "Column",
    "Count",
    "Missing",
    "Mean",
    "Std",
    "Min",
    "25%",
    "Median",
    "75%",
    "Max",
  ];
  return (
    <div>
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-widest text-gray-400">
        Numeric columns
      </h3>
      <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-gray-50 dark:bg-gray-800">
            <tr>
              {headers.map((h) => (
                <th key={h} className="px-3 py-2 font-medium">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr
                key={r.name}
                className="border-t border-gray-100 tabular-nums dark:border-gray-800"
              >
                <td className="px-3 py-2 font-medium">{r.name}</td>
                <td className="px-3 py-2">{r.count.toLocaleString()}</td>
                <td className="px-3 py-2">{r.missing.toLocaleString()}</td>
                <td className="px-3 py-2">{fmt(r.mean)}</td>
                <td className="px-3 py-2">{fmt(r.std)}</td>
                <td className="px-3 py-2">{fmt(r.min)}</td>
                <td className="px-3 py-2">{fmt(r.q25)}</td>
                <td className="px-3 py-2">{fmt(r.median)}</td>
                <td className="px-3 py-2">{fmt(r.q75)}</td>
                <td className="px-3 py-2">{fmt(r.max)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function CategoricalTable({ rows }: { rows: EdaReport["categorical"] }) {
  const headers = ["Column", "Count", "Missing", "Unique", "Top", "Top freq"];
  return (
    <div>
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-widest text-gray-400">
        Categorical columns
      </h3>
      <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-gray-50 dark:bg-gray-800">
            <tr>
              {headers.map((h) => (
                <th key={h} className="px-3 py-2 font-medium">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr
                key={r.name}
                className="border-t border-gray-100 dark:border-gray-800"
              >
                <td className="px-3 py-2 font-medium">{r.name}</td>
                <td className="px-3 py-2">{r.count.toLocaleString()}</td>
                <td className="px-3 py-2">{r.missing.toLocaleString()}</td>
                <td className="px-3 py-2">{r.unique.toLocaleString()}</td>
                <td className="px-3 py-2">{r.top ?? "—"}</td>
                <td className="px-3 py-2">{r.top_freq.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
