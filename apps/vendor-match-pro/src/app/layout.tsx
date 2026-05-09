import type { Metadata } from "next";
import { AppShell } from "@/components/app-shell";
import { siteDescription, siteName, siteTagline } from "@/lib/site";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://useunitdispatch.com"),
  title: {
    default: siteName,
    template: `%s | ${siteName}`
  },
  description: siteDescription,
  applicationName: siteName,
  alternates: {
    canonical: "https://useunitdispatch.com"
  },
  openGraph: {
    title: `${siteName} | ${siteTagline}`,
    description: siteDescription,
    url: "https://useunitdispatch.com",
    siteName,
    type: "website"
  },
  icons: {
    icon: "/favicon.svg"
  },
  twitter: {
    card: "summary_large_image",
    title: `${siteName} | ${siteTagline}`,
    description: siteDescription
  }
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
