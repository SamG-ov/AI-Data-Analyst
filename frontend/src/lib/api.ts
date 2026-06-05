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

/** Small GET helper that throws a readable error on failure. */
async function getJson<T>(path: string, fallback: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`);
  if (!res.ok) {
    throw new Error(await parseError(res, fallback));
  }
  return (await res.json()) as T;
}

// --- Health -----------------------------------------------------------------

export interface HealthResponse {
  status: string;
  app: string;
  environment: string;
}

/** Calls the backend /health endpoint. Throws if the request fails. */
export async function getHealth(): Promise<HealthResponse> {
  return getJson<HealthResponse>("/health", "Backend unreachable");
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
  return getJson<QualityReport>(
    `/datasets/${datasetId}/quality`,
    "Failed to load quality report",
  );
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

// --- EDA & charts -----------------------------------------------------------

// Mirrors the backend's app/schemas/eda.py one-to-one.
export interface NumericStats {
  name: string;
  count: number;
  missing: number;
  mean: number | null;
  std: number | null;
  min: number | null;
  q25: number | null;
  median: number | null;
  q75: number | null;
  max: number | null;
}

export interface CategoricalStats {
  name: string;
  count: number;
  missing: number;
  unique: number;
  top: string | null;
  top_freq: number;
}

export interface EdaReport {
  n_rows: number;
  n_columns: number;
  numeric: NumericStats[];
  categorical: CategoricalStats[];
}

export interface Chart {
  column: string;
  type: "histogram" | "bar";
  title: string;
  labels: string[];
  values: number[];
}

export interface ChartsResponse {
  charts: Chart[];
}

/** Fetches descriptive statistics for a dataset. */
export async function getEda(datasetId: string): Promise<EdaReport> {
  return getJson<EdaReport>(`/datasets/${datasetId}/eda`, "Failed to load EDA");
}

/** Fetches pre-computed chart data for a dataset. */
export async function getCharts(datasetId: string): Promise<ChartsResponse> {
  return getJson<ChartsResponse>(
    `/datasets/${datasetId}/charts`,
    "Failed to load charts",
  );
}

// --- Natural-language Q&A ---------------------------------------------------

export interface AnswerResponse {
  answer: string;
}

/** Asks Claude a natural-language question about a dataset. */
export async function askQuestion(
  datasetId: string,
  question: string,
): Promise<AnswerResponse> {
  const res = await fetch(`${API_BASE_URL}/datasets/${datasetId}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    throw new Error(await parseError(res, "Failed to get an answer"));
  }
  return (await res.json()) as AnswerResponse;
}

// --- AI insights ------------------------------------------------------------

export interface InsightsResponse {
  report: string;
}

/** Generates an AI analysis (summary, findings, recommendations). */
export async function generateInsights(
  datasetId: string,
): Promise<InsightsResponse> {
  const res = await fetch(`${API_BASE_URL}/datasets/${datasetId}/insights`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(await parseError(res, "Failed to generate insights"));
  }
  return (await res.json()) as InsightsResponse;
}
