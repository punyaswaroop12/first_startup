"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { useAuth } from "@/components/layout/auth-provider";
import { Card } from "@/components/ui/card";
import { ApiError } from "@/lib/api";

function parseFragment() {
  if (typeof window === "undefined") {
    return new URLSearchParams();
  }
  return new URLSearchParams(window.location.hash.replace(/^#/, ""));
}

export default function MicrosoftAuthCallbackPage() {
  const router = useRouter();
  const { completeTokenLogin } = useAuth();
  const [status, setStatus] = useState("Completing Microsoft sign-in...");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fragment = parseFragment();
    const accessToken = fragment.get("access_token");
    const next = fragment.get("next") ?? "/dashboard";
    const callbackError = fragment.get("error");

    if (callbackError) {
      setError(callbackError);
      setStatus("Microsoft sign-in failed.");
      return;
    }

    if (!accessToken) {
      setError("Microsoft sign-in did not return an application session.");
      setStatus("Microsoft sign-in failed.");
      return;
    }

    completeTokenLogin(accessToken, next).catch((caught: unknown) => {
      if (caught instanceof ApiError) {
        setError(caught.message);
      } else if (caught instanceof Error) {
        setError(caught.message);
      } else {
        setError("Unexpected error while completing Microsoft sign-in.");
      }
      setStatus("Microsoft sign-in failed.");
    });
  }, [completeTokenLogin]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-mist px-6 py-10">
      <Card className="w-full max-w-xl p-8">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate">
          Microsoft authentication
        </p>
        <h1 className="mt-4 text-3xl font-semibold text-ink">{status}</h1>
        <p className="mt-4 text-sm leading-7 text-slate">
          {error
            ? error
            : "Your workspace session is being created and you will be redirected automatically."}
        </p>

        {error ? (
          <div className="mt-8">
            <button
              className="rounded-full bg-ink px-5 py-3 text-sm font-medium text-white transition hover:opacity-90"
              onClick={() => router.push("/login")}
              type="button"
            >
              Return to login
            </button>
          </div>
        ) : null}
      </Card>
    </main>
  );
}
