"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuth } from "@/components/layout/auth-provider";

export function AuthGate({ children }: { children: React.ReactNode }) {
  const { token, isBooting } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!isBooting && !token && pathname !== "/login") {
      router.replace("/login");
    }
  }, [isBooting, pathname, router, token]);

  if (isBooting) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-canvas">
        <div className="rounded-3xl border border-white/80 bg-white px-6 py-5 text-sm font-medium text-slate shadow-panel">
          Loading workspace...
        </div>
      </div>
    );
  }

  if (!token && pathname !== "/login") {
    return null;
  }

  return <>{children}</>;
}

