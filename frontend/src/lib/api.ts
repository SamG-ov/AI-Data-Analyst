/**
 * API client — the single place the frontend talks to the backend.
 *
 * Components import typed functions from here instead of calling fetch
 * directly, so networking, error handling, and the base URL live in one
 * spot that's easy to change or mock in tests.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

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
    // FastAPI returns errors as { detail: "..." } — surface that to the user.
    let message = `Upload failed (${res.status})`;
    try {
      const data = (await res.json()) as { detail?: string };
      if (data.detail) message = data.detail;
    } catch {
      // response wasn't JSON; keep the generic message
    }
    throw new Error(message);
  }

  return (await res.json()) as DatasetSummary;
}
