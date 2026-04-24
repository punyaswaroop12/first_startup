"use client";

import { BarChart3, Bot, FileStack, LayoutDashboard, Settings2, Workflow } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/components/layout/auth-provider";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/documents", label: "Documents", icon: FileStack },
  { href: "/assistant", label: "Chat Assistant", icon: Bot },
  { href: "/reports", label: "Reports", icon: BarChart3 },
  { href: "/automations", label: "Automations", icon: Workflow },
  { href: "/admin-settings", label: "Admin Settings", icon: Settings2 }
];

export function AppSidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="w-full shrink-0 border-b border-white/70 bg-ink px-4 py-5 text-white sm:px-6 sm:py-6 lg:flex lg:min-h-screen lg:max-w-[280px] lg:flex-col lg:border-b-0 lg:border-r lg:px-6 lg:py-7">
      <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
        <p className="text-xs uppercase tracking-[0.24em] text-white/50">Ops Intelligence</p>
        <h1 className="mt-2 text-xl font-semibold">Knowledge + Reporting</h1>
        <p className="mt-3 text-sm leading-6 text-white/65">
          Operations teams can search SOPs, report weekly movement, and automate follow-up.
        </p>
      </div>

      <nav className="mt-6 grid gap-2 sm:grid-cols-2 lg:mt-8 lg:grid-cols-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition lg:w-full ${
                isActive ? "bg-white text-ink" : "text-white/70 hover:bg-white/8 hover:text-white"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="mt-6 rounded-3xl border border-white/10 bg-white/5 p-5 lg:mt-auto">
        <div className="flex items-center justify-between">
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold">{user?.full_name ?? "User"}</p>
            <p className="mt-1 truncate text-xs text-white/55" title={user?.email ?? ""}>
              {user?.email}
            </p>
          </div>
          <Badge tone={user?.role === "admin" ? "accent" : "signal"}>
            {user?.role ?? "user"}
          </Badge>
        </div>
        <Button className="mt-5 w-full" variant="secondary" onClick={logout}>
          Sign out
        </Button>
      </div>
    </aside>
  );
}
