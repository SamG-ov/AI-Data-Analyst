import type { Chart } from "@/lib/api";

interface ChartCardProps {
  chart: Chart;
}

/**
 * Renders chart data as simple horizontal bars. No charting dependency —
 * the backend already computed labels + values, so this stays React-19-safe
 * and can later be swapped for Plotly/Recharts behind the same data shape.
 */
export default function ChartCard({ chart }: ChartCardProps) {
  const max = Math.max(...chart.values, 1);

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="mb-3 text-sm font-medium">{chart.title}</h4>
      <div className="space-y-1.5">
        {chart.labels.map((label, i) => (
          <div key={`${label}-${i}`} className="flex items-center gap-2 text-xs">
            <span
              className="w-28 shrink-0 truncate text-right text-gray-500"
              title={label}
            >
              {label}
            </span>
            <div className="h-4 flex-1 rounded bg-gray-100 dark:bg-gray-800">
              <div
                className="h-4 rounded bg-blue-500"
                style={{ width: `${(chart.values[i] / max) * 100}%` }}
              />
            </div>
            <span className="w-10 shrink-0 tabular-nums text-gray-500">
              {chart.values[i]}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
