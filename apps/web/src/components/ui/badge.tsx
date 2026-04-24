import { clsx } from "clsx";
import type { PropsWithChildren } from "react";

export function Badge({
  children,
  tone = "neutral"
}: PropsWithChildren<{ tone?: "neutral" | "accent" | "signal" | "alert" }>) {
  const tones = {
    neutral: "bg-mist text-slate",
    accent: "bg-accent/10 text-accent",
    signal: "bg-signal/10 text-signal",
    alert: "bg-alert/10 text-alert"
  };

  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold",
        tones[tone]
      )}
    >
      {children}
    </span>
  );
}

