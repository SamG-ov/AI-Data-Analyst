"use client";

import { useState } from "react";
import FileUpload from "@/components/FileUpload";
import DatasetPreview from "@/components/DatasetPreview";
import DataQuality from "@/components/DataQuality";
import type { CleanAction, CleanResult, DatasetSummary } from "@/lib/api";

export default function Home() {
  const [dataset, setDataset] = useState<DatasetSummary | null>(null);
  const [appliedActions, setAppliedActions] = useState<CleanAction[] | null>(null);

  function handleUploaded(summary: DatasetSummary) {
    setDataset(summary);
    setAppliedActions(null);
  }

  function handleCleaned(result: CleanResult) {
    setDataset(result.dataset);
    setAppliedActions(result.actions);
  }

  return (
    <main className="flex min-h-screen flex-col items-center gap-8 p-8 py-16">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight">AI Data Analyst</h1>
        <p className="mt-2 text-gray-500">
          Upload a dataset to explore and analyze it.
        </p>
      </div>

      <FileUpload onUploaded={handleUploaded} />

      {dataset && (
        <>
          {appliedActions && (
            <div className="w-full max-w-4xl rounded-lg border border-green-200 bg-green-50 p-4 text-sm dark:border-green-900 dark:bg-green-950/40">
              <p className="font-medium text-green-700 dark:text-green-400">
                Cleaning applied:
              </p>
              <ul className="mt-1 list-disc pl-5 text-green-800 dark:text-green-300">
                {appliedActions.map((a, i) => (
                  <li key={i}>{a.detail}</li>
                ))}
              </ul>
            </div>
          )}

          <DataQuality datasetId={dataset.id} onCleaned={handleCleaned} />
          <DatasetPreview dataset={dataset} />
        </>
      )}
    </main>
  );
}
