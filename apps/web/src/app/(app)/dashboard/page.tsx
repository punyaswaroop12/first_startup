"use client";

import { format } from "date-fns";
import { useEffect, useState } from "react";

import { useAuth } from "@/components/layout/auth-provider";
import { PageHeader } from "@/components/layout/page-header";
import { Card } from "@/components/ui/card";
import { dashboardApi } from "@/lib/api";
import type { DashboardOverview } from "@/lib/types";

export default function DashboardPage() {
  const { token } = useAuth();
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      return;
    }
    dashboardApi
      .overview(token)
      .then(setOverview)
      .catch(() => {
        setError("Unable to load dashboard data.");
      });
  }, [token]);

  return (
    <div>
      <PageHeader
        eyebrow="Operations Overview"
        title="Control center"
        description="Track knowledge coverage, report activity, and the operational events that matter for the next decision cycle."
        tag="Operations overview"
      />

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {overview?.metrics.map((metric) => (
          <Card key={metric.label}>
            <p className="text-sm font-medium text-slate">{metric.label}</p>
            <h3 className="mt-4 text-4xl font-semibold text-ink">{metric.value}</h3>
            <p className="mt-4 text-sm text-slate">{metric.trend}</p>
          </Card>
        )) ?? (
          <>
            {[...Array.from({ length: 4 })].map((_, index) => (
              <Card key={index} className="h-[158px] animate-pulse bg-white/70" />
            ))}
          </>
        )}
      </section>

      <section className="mt-6 grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <Card>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate">Recent activity</p>
          <div className="mt-6 space-y-4">
            {overview?.activity.length ? (
              overview.activity.map((item) => (
                <div
                  key={`${item.timestamp}-${item.title}`}
                  className="rounded-2xl border border-edge bg-mist px-4 py-4"
                >
                  <div className="flex items-center justify-between gap-4">
                    <h3 className="text-sm font-semibold text-ink">{item.title}</h3>
                    <span className="text-xs text-slate">
                      {format(new Date(item.timestamp), "MMM d, yyyy HH:mm")}
                    </span>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-slate">{item.description}</p>
                </div>
              ))
            ) : (
              <div className="rounded-2xl border border-dashed border-edge px-4 py-10 text-sm text-slate">
                {error ?? "No activity yet. Uploading documents and generating reports will show here."}
              </div>
            )}
          </div>
        </Card>

        <Card>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate">Power BI references</p>
          <div className="mt-6 space-y-4">
            {overview?.power_bi_reports.length ? (
              overview.power_bi_reports.map((report) => (
                <a
                  key={report.id}
                  className="block rounded-2xl border border-edge bg-mist px-4 py-4 transition hover:border-accent"
                  href={report.report_url}
                  rel="noreferrer"
                  target="_blank"
                >
                  <p className="text-sm font-semibold text-ink">{report.name}</p>
                  <p className="mt-2 text-xs uppercase tracking-[0.18em] text-slate">
                    {report.workspace_name ?? "Power BI"}
                  </p>
                  <p className="mt-3 text-sm leading-6 text-slate">
                    {report.description ?? "Configured reference for operational reporting context."}
                  </p>
                </a>
              ))
            ) : (
              <div className="rounded-2xl border border-dashed border-edge px-4 py-10 text-sm text-slate">
                No Power BI references configured yet. Admins can add them in Admin Settings.
              </div>
            )}
          </div>
        </Card>
      </section>
    </div>
  );
}
