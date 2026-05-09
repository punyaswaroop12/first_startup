import Link from "next/link";
import { ArrowRight, BadgeCheck, Banknote, Building2, CalendarDays, Clock3, MapPin, Plus, ShieldCheck, Sparkles } from "lucide-react";
import { Badge, Button, Card, LinkButton, ProgressBar, SectionHeading, StatCard, Table, TableCell, TableHeaderCell } from "@/components/ui";
import { calculateBestValueScore } from "@/lib/metrics";
import { contractors, jobs, performanceBenchmarks, properties, reviews, statusFlow } from "@/lib/demo-data";
import { formatCurrency, formatPercent, formatShortDate } from "@/lib/format";

const openJobs = jobs.filter((job) => job.status !== "Reviewed").length;
const emergencyJobs = jobs.filter((job) => job.emergency).length;
const averageResponse = Math.round(jobs.reduce((sum, job) => sum + job.responseTimeMinutes, 0) / jobs.length);
const savings = performanceBenchmarks.averageSavings * jobs.filter((job) => job.status === "Completed" || job.status === "Reviewed").length;

export default function DashboardPage() {
  return (
    <div className="container-pad py-8 md:py-12">
      <div className="surface-dark overflow-hidden">
        <div className="grid gap-8 p-6 lg:grid-cols-[1.05fr_0.95fr] lg:p-8">
          <div className="space-y-5">
            <Badge tone="info" className="bg-sky-500/15 text-sky-100">Property manager command center</Badge>
            <div>
              <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">Maintenance without spreadsheets, ghosting, or scattered vendor calls.</h1>
              <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300">
                Track open jobs, compare quotes, dispatch vendors, and keep reliable contractors in a preferred network for recurring work.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <LinkButton href="/jobs/new" className="bg-sky-500 text-slate-950 hover:bg-sky-400">
                <Plus size={16} />
                Create new job
              </LinkButton>
              <LinkButton href="/jobs/job-001/match" variant="outline" className="border-slate-700 bg-transparent text-white hover:bg-white/10">
                View contractor recommendations
              </LinkButton>
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              <Card className="border-slate-800 bg-slate-900/60 p-4 text-white">
                <p className="text-sm text-slate-400">Open jobs</p>
                <p className="mt-2 text-3xl font-semibold">{openJobs}</p>
              </Card>
              <Card className="border-slate-800 bg-slate-900/60 p-4 text-white">
                <p className="text-sm text-slate-400">Emergency jobs</p>
                <p className="mt-2 text-3xl font-semibold">{emergencyJobs}</p>
              </Card>
              <Card className="border-slate-800 bg-slate-900/60 p-4 text-white">
                <p className="text-sm text-slate-400">Avg response</p>
                <p className="mt-2 text-3xl font-semibold">{averageResponse} min</p>
              </Card>
            </div>
          </div>

          <Card className="bg-white p-5 text-slate-950">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sky-700">Operations snapshot</p>
                <h2 className="text-xl font-semibold">Market comparison</h2>
              </div>
              <Badge tone="success">Live demo data</Badge>
            </div>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <StatCard label="Projected savings" value={formatCurrency(savings)} tone="success" />
              <StatCard label="Quote spread" value={`${performanceBenchmarks.averageQuoteSpread}%`} tone="info" />
              <StatCard label="Emergency fill rate" value={formatPercent(performanceBenchmarks.emergencyFillRate)} tone="warning" />
              <StatCard label="Vendor reliability" value="91" tone="default" />
            </div>
          </Card>
        </div>
      </div>

      <div className="mt-8 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Card className="p-6">
          <SectionHeading
            eyebrow="Properties"
            title="Portfolio overview"
            description="Each property has open issues, units, and monthly spend so you can see where maintenance is concentrated."
          />
          <div className="mt-6 overflow-hidden rounded-2xl border border-slate-200">
            <Table>
              <table className="min-w-full">
                <thead className="bg-slate-50">
                  <tr>
                    <TableHeaderCell>Property</TableHeaderCell>
                    <TableHeaderCell>Units</TableHeaderCell>
                    <TableHeaderCell>Open issues</TableHeaderCell>
                    <TableHeaderCell>Monthly spend</TableHeaderCell>
                  </tr>
                </thead>
                <tbody>
                  {properties.slice(0, 6).map((property) => (
                    <tr key={property.id} className="border-t border-slate-100">
                      <TableCell>
                        <div>
                          <p className="font-medium text-slate-950">{property.name}</p>
                          <p className="text-xs text-slate-500">{property.address} • {property.city}</p>
                        </div>
                      </TableCell>
                      <TableCell>{property.units}</TableCell>
                      <TableCell><Badge tone={property.openIssues > 3 ? "warning" : "default"}>{property.openIssues}</Badge></TableCell>
                      <TableCell>{formatCurrency(property.monthlyMaintenanceSpend)}</TableCell>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Table>
          </div>
        </Card>

        <Card className="p-6">
          <SectionHeading
            eyebrow="Decision inbox"
            title="Jobs that need action"
            description="These are the jobs with the highest operational urgency or quote volume."
          />
          <div className="mt-6 space-y-4">
            {jobs.slice(0, 6).map((job) => {
              const property = properties.find((item) => item.id === job.propertyId)!;
              const contractor = job.assignedContractorId ? contractors.find((item) => item.id === job.assignedContractorId) : null;
              return (
                <Card key={job.id} className="p-4">
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="font-semibold text-slate-950">{job.title}</h3>
                        <Badge tone={job.emergency ? "danger" : "default"}>{job.urgency}</Badge>
                      </div>
                      <p className="mt-1 text-sm text-slate-600">{property.name} • {job.unit} • {job.tradeCategory}</p>
                      <p className="mt-2 text-xs text-slate-500">{job.description}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Quotes</p>
                      <p className="text-2xl font-semibold">{job.quotesCount}</p>
                    </div>
                  </div>
                  <div className="mt-4 grid gap-3 sm:grid-cols-3">
                    <div>
                      <p className="text-xs text-slate-500">Assigned vendor</p>
                      <p className="text-sm font-medium text-slate-950">{contractor?.businessName ?? "Not assigned"}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500">Estimated range</p>
                      <p className="text-sm font-medium text-slate-950">{formatCurrency(job.estimateMin)} - {formatCurrency(job.estimateMax)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500">Response window</p>
                      <p className="text-sm font-medium text-slate-950">{job.responseTimeMinutes} min</p>
                    </div>
                  </div>
                  <div className="mt-4 flex items-center justify-between gap-3">
                    <Badge tone={job.status === "Disputed" ? "danger" : job.status === "Completed" ? "success" : "info"}>{job.status}</Badge>
                    <div className="flex flex-wrap gap-2">
                      <Link href={`/jobs/${job.id}/match`} className="inline-flex items-center gap-2 rounded-xl bg-slate-950 px-3 py-2 text-sm font-medium text-white">
                        Compare quotes
                        <ArrowRight size={14} />
                      </Link>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <Card className="p-6">
          <SectionHeading eyebrow="Job lifecycle" title="Move work through the maintenance pipeline" />
          <div className="mt-6 grid gap-3">
            {statusFlow.map((status, index) => (
              <div key={status} className="flex items-center gap-4">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-950 text-sm font-semibold text-white">{index + 1}</div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-slate-950">{status}</p>
                    <p className="text-xs text-slate-500">{Math.max(1, 15 - index)} jobs</p>
                  </div>
                  <div className="mt-2"><ProgressBar value={(index + 1) * 10} /></div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <SectionHeading eyebrow="Trust" title="Reliability and review signals" description="Reviews only exist after completed jobs, so the metrics stay tied to real work." />
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <StatCard label="Completed job reviews" value={String(reviews.length)} tone="success" />
            <StatCard label="Avg contractor score" value={String(Math.round(contractors.reduce((sum, contractor) => sum + contractor.reliabilityScore, 0) / contractors.length))} tone="info" />
          </div>
          <div className="mt-6 space-y-3">
            {reviews.slice(0, 4).map((review) => {
              const contractor = contractors.find((item) => item.id === review.contractorId)!;
              return (
                <Card key={review.id} className="p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-medium text-slate-950">{contractor.businessName}</p>
                      <p className="text-sm text-slate-600">{review.reviewer} • {formatShortDate(review.date)}</p>
                      <p className="mt-2 text-sm text-slate-700">{review.note}</p>
                    </div>
                    <Badge tone="success">Completed job</Badge>
                  </div>
                  <div className="mt-3 grid gap-2 text-xs text-slate-500 sm:grid-cols-2">
                    <p>Quote accuracy: {review.priceMatchedQuote}/5</p>
                    <p>Communication: {review.communication}/5</p>
                  </div>
                </Card>
              );
            })}
          </div>
        </Card>
      </div>
    </div>
  );
}
