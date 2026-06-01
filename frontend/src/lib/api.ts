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
