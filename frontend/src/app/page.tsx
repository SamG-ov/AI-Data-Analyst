"use client";

import { useState } from "react";
import FileUpload from "@/components/FileUpload";
import DatasetPreview from "@/components/DatasetPreview";
import type { DatasetSummary } from "@/lib/api";

export default function Home() {
  const [dataset, setDataset] = useState<DatasetSummary | null>(null);

  return (
    <main className="flex min-h-screen flex-col items-center gap-10 p-8 py-16">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight">AI Data Analyst</h1>
        <p className="mt-2 text-gray-500">
          Upload a dataset to explore and analyze it.
        </p>
      </div>

      <FileUpload onUploaded={setDataset} />

      {dataset && <DatasetPreview dataset={dataset} />}
    </main>
  );
}
