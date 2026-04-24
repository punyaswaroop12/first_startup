import { clsx } from "clsx";
import type { PropsWithChildren } from "react";

export function Card({
  children,
  className
}: PropsWithChildren<{ className?: string }>) {
  return (
    <div
      className={clsx(
        "rounded-3xl border border-white/80 bg-white/95 p-6 shadow-panel backdrop-blur",
        className
      )}
    >
      {children}
    </div>
  );
}

