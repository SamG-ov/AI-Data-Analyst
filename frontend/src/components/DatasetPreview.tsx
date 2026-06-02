import type { DatasetSummary } from "@/lib/api";

interface DatasetPreviewProps {
  dataset: DatasetSummary;
}

export default function DatasetPreview({ dataset }: DatasetPreviewProps) {
  return (
    <div className="w-full max-w-4xl">
      <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-lg font-semibold">{dataset.filename}</h2>
        <p className="text-sm text-gray-500">
          {dataset.n_rows.toLocaleString()} rows · {dataset.n_columns} columns
        </p>
      </div>

      <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-gray-50 dark:bg-gray-800">
            <tr>
              {dataset.columns.map((col) => (
                <th key={col.name} className="px-3 py-2 font-medium">
                  <div>{col.name}</div>
                  <div className="text-xs font-normal text-gray-400">
                    {col.dtype}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {dataset.preview.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className="border-t border-gray-100 dark:border-gray-800"
              >
                {dataset.columns.map((col) => (
                  <td key={col.name} className="px-3 py-2">
                    {formatCell(row[col.name])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="mt-2 text-xs text-gray-400">
        Showing first {dataset.preview.length} rows.
      </p>
    </div>
  );
}

/** Render a cell value as a string, showing empty/null clearly. */
function formatCell(value: unknown): string {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}
