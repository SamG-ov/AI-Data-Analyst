"use client";

import { useEffect, useState } from "react";
import { getHealth, type HealthResponse } from "@/lib/api";

// A discriminated union models the three states an async call can be in.
// This makes it impossible to, e.g., render data while still loading.
type Status =
  | { state: "loading" }
  | { state: "ok"; data: HealthResponse }
  | { state: "error"; message: string };

export default function Home() {
  const [status, setStatus] = useState<Status>({ state: "loading" });

  useEffect(() => {
    getHealth()
      .then((data) => setStatus({ state: "ok", data }))
      .catch((err: unknown) =>
        setStatus({
          state: "error",
          message: err instanceof Error ? err.message : "Unknown error",
        }),
      );
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-8 p-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight">AI Data Analyst</h1>
        <p className="mt-2 text-gray-500">
          Upload, explore, and ask questions about your data.
        </p>
      </div>

      <div className="w-full max-w-sm rounded-xl border border-gray-200 p-6 text-center dark:border-gray-700">
        <h2 className="mb-3 text-xs font-semibold uppercase tracking-widest text-gray-400">
          Backend connection
        </h2>

        {status.state === "loading" && (
          <p className="text-gray-500">Checking backend…</p>
        )}

        {status.state === "ok" && (
          <>
            <p className="text-lg font-semibold text-green-600">● Connected</p>
            <p className="mt-1 text-sm text-gray-500">
              {status.data.app} · {status.data.environment}
            </p>
          </>
        )}

        {status.state === "error" && (
          <>
            <p className="text-lg font-semibold text-red-600">● Not connected</p>
            <p className="mt-1 text-sm text-gray-500">{status.message}</p>
            <p className="mt-2 text-xs text-gray-400">
              Is the backend running at http://localhost:8000?
            </p>
          </>
        )}
      </div>
    </main>
  );
}
