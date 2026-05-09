import Link from "next/link";

export default function NotFound() {
  return (
    <div className="container-pad flex min-h-[60vh] items-center justify-center py-12">
      <div className="max-w-lg rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-crisp">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Not found</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">That maintenance view does not exist.</h1>
        <p className="mt-3 text-sm leading-6 text-slate-600">Go back to the dashboard or post a new job for the demo.</p>
        <div className="mt-6 flex justify-center gap-3">
          <Link href="/dashboard" className="rounded-xl bg-slate-950 px-4 py-2 text-sm font-medium text-white">Dashboard</Link>
          <Link href="/jobs/new" className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-900">Create job</Link>
        </div>
      </div>
    </div>
  );
}
