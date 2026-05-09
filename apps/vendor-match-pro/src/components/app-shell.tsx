"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bell, Building2, CalendarClock, Hammer, MenuSquare, ShieldCheck, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { navLinks, siteName, siteTagline } from "@/lib/site";
import { Badge, Button, LinkButton } from "@/components/ui";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950">
      <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-2xl bg-slate-950 text-white shadow-panel">
              <Hammer size={18} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-sm font-semibold tracking-tight">{siteName}</h1>
                <Badge tone="success">Demo</Badge>
              </div>
              <p className="text-xs text-slate-500">{siteTagline}</p>
            </div>
          </div>

          <nav className="hidden items-center gap-1 rounded-2xl border border-slate-200 bg-slate-50 p-1 md:flex">
            {navLinks.slice(0, 6).map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "rounded-xl px-3 py-2 text-sm font-medium transition",
                  pathname === link.href ? "bg-white text-slate-950 shadow-sm" : "text-slate-600 hover:bg-white/70 hover:text-slate-950"
                )}
              >
                {link.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <LinkButton variant="outline" href="/login" className="hidden sm:inline-flex">
              <MenuSquare size={16} />
              Switch role
            </LinkButton>
            <Button variant="outline" className="hidden lg:inline-flex">
              <Bell size={16} />
              Alerts
            </Button>
          </div>
        </div>
      </header>

      <main>{children}</main>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-6 text-sm text-slate-500 sm:px-6 lg:px-8 md:flex-row md:items-center md:justify-between">
          <p>Built for recurring rental-property maintenance, not one-off homeowner leads.</p>
          <div className="flex flex-wrap gap-3">
            <span className="inline-flex items-center gap-2"><ShieldCheck size={14} /> Verified completed-job reviews</span>
            <span className="inline-flex items-center gap-2"><CalendarClock size={14} /> Emergency dispatch ready</span>
            <span className="inline-flex items-center gap-2"><Building2 size={14} /> Property-manager-first workflow</span>
            <span className="inline-flex items-center gap-2"><Sparkles size={14} /> Reliability scoring</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
