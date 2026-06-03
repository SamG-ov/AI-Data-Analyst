/**
 * API client — the single place the frontend talks to the backend.
 *
 * Components import typed functions from here instead of calling fetch
 * directly, so networking, error handling, and the base URL live in one
 * spot that's easy to change or mock in tests.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** Extract a FastAPI { detail } error message, falling back to a generic one. */
async function parseError(res: Response, fallback: string): Promise<string> {
  try {
    const data = (await res.json()) as { detail?: string };
    if (data.detail) return data.detail;
  } catch {
    // response wasn't JSON; ignore
  }
  return `${fallback} (${res.status})`;
}

// --- Health -----------------------------------------------------------------

export interface HealthResponse {
  status: string;
  app: string;
  environment: string;
}

/** Calls the backend /health endpoint. Throws if the request fails. */
export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) {
    throw new Error(`Backend responded with ${res.status}`);
  }
  return (await res.json()) as HealthResponse;
}

// --- Datasets ---------------------------------------------------------------

// Mirrors the backend's app/schemas/dataset.py one-to-one.
export interface ColumnInfo {
  name: string;
  dtype: string;
}

export interface DatasetSummary {
  id: string;
  filename: string;
  n_rows: number;
  n_columns: number;
  columns: ColumnInfo[];
  preview: Record<string, unknown>[];
}

/** Uploads a CSV/Excel file and returns its summary. */
export async function uploadDataset(file: File): Promise<DatasetSummary> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE_URL}/datasets`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    throw new Error(await parseError(res, "Upload failed"));
  }
  return (await res.json()) as DatasetSummary;
}

// --- Data quality & cleaning ------------------------------------------------

// Mirrors the backend's app/schemas/cleaning.py one-to-one.
export interface ColumnQuality {
  name: string;
  dtype: string;
  missing: number;
  missing_pct: number;
  n_unique: number;
  is_constant: boolean;
}

export interface QualityReport {
  n_rows: number;
  n_columns: number;
  duplicate_rows: number;
  total_missing: number;
  columns: ColumnQuality[];
}

export interface CleanAction {
  action: string;
  detail: string;
}

export interface CleanResult {
  dataset: DatasetSummary;
  actions: CleanAction[];
}

/** Fetches the data-quality report for a dataset. */
export async function getQualityReport(datasetId: string): Promise<QualityReport> {
  const res = await fetch(`${API_BASE_URL}/datasets/${datasetId}/quality`);
  if (!res.ok) {
    throw new Error(await parseError(res, "Failed to load quality report"));
  }
  return (await res.json()) as QualityReport;
}

/** Runs auto-clean and returns the new cleaned dataset + actions taken. */
export async function cleanDataset(datasetId: string): Promise<CleanResult> {
  const res = await fetch(`${API_BASE_URL}/datasets/${datasetId}/clean`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(await parseError(res, "Failed to clean dataset"));
  }
  return (await res.json()) as CleanResult;
}
