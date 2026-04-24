import type { Metadata } from "next";

import { AuthProvider } from "@/components/layout/auth-provider";
import { AuthGate } from "@/components/layout/auth-gate";
import "@/app/globals.css";

export const metadata: Metadata = {
  title: "AI Knowledge + Reporting Assistant",
  description:
    "Operations-focused knowledge search, reporting, and automation assistant."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">
        <AuthProvider>
          <AuthGate>{children}</AuthGate>
        </AuthProvider>
      </body>
    </html>
  );
}
