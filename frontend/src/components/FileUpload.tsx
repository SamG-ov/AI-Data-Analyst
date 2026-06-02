"use client";

import { useState } from "react";
import { uploadDataset, type DatasetSummary } from "@/lib/api";

interface FileUploadProps {
  /** Called with the dataset summary after a successful upload. */
  onUploaded: (summary: DatasetSummary) => void;
}

export default function FileUpload({ onUploaded }: FileUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);
    try {
      const summary = await uploadDataset(file);
      onUploaded(summary);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsUploading(false);
      // Reset so selecting the same file again still triggers onChange.
      event.target.value = "";
    }
  }

  return (
    <div className="w-full max-w-md">
      <label
        className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 text-center transition-colors ${
          isUploading
            ? "border-gray-300 opacity-60"
            : "border-gray-300 hover:border-blue-500 dark:border-gray-600"
        }`}
      >
        <span className="text-sm font-medium">
          {isUploading ? "Uploading…" : "Click to upload a CSV or Excel file"}
        </span>
        <span className="mt-1 text-xs text-gray-400">.csv, .xlsx, .xls</span>
        <input
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileChange}
          disabled={isUploading}
          className="hidden"
        />
      </label>

      {error && (
        <p className="mt-3 text-center text-sm text-red-600">{error}</p>
      )}
    </div>
  );
}
