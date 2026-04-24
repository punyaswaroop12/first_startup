import { AppSidebar } from "@/components/layout/app-sidebar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-dashboard-grid lg:flex-row">
      <AppSidebar />
      <main className="min-w-0 flex-1 px-4 py-5 sm:px-6 sm:py-8 lg:px-8">{children}</main>
    </div>
  );
}
