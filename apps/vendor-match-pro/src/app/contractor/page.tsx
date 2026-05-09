import { Badge, Button, Card, LinkButton, ProgressBar, SectionHeading, StatCard } from "@/components/ui";
import { contractors, jobs, reviews } from "@/lib/demo-data";
import { formatCurrency } from "@/lib/format";
import { calculateBestValueScore } from "@/lib/metrics";
import { ArrowRight, BadgeCheck, Clock3, DollarSign, MapPin, ShieldCheck, Star, TrendingUp } from "lucide-react";

const contractor = contractors.find((item) => item.featured) ?? contractors[0];
const contractorReviews = reviews.filter((review) => review.contractorId === contractor.id);

export default function ContractorPage() {
  return (
    <div className="container-pad py-8 md:py-12">
      <SectionHeading
        eyebrow="Contractor portal"
        title="A lighter workflow for vendors who want repeat property work."
        description="See matched jobs, quote quickly, and build a reputation based on completed jobs rather than vanity star ratings."
      />

      <div className="mt-8 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Card className="p-6">
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone="success">Verified profile</Badge>
            <Badge tone={contractor.emergencyAvailability ? "danger" : "default"}>{contractor.emergencyAvailability ? "Emergency ready" : "Standard hours"}</Badge>
            <Badge tone="info">Priority job alerts</Badge>
          </div>
          <div className="mt-5 flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-slate-950">{contractor.businessName}</h2>
              <p className="mt-2 text-sm text-slate-600">{contractor.name} • {contractor.trade}</p>
              <div className="mt-4 grid gap-2 text-sm text-slate-600 sm:grid-cols-2">
                <p className="flex items-center gap-2"><MapPin size={14} /> {contractor.serviceAreas.join(", ")}</p>
                <p className="flex items-center gap-2"><Clock3 size={14} /> Response in {contractor.responseTimeMinutes} minutes</p>
                <p className="flex items-center gap-2"><ShieldCheck size={14} /> License {contractor.verifiedLicense ? "verified" : "pending"}</p>
                <p className="flex items-center gap-2"><BadgeCheck size={14} /> Insurance {contractor.verifiedInsurance ? "verified" : "pending"}</p>
              </div>
            </div>
            <div className="w-full max-w-xs rounded-2xl bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Reliability score</p>
              <p className="mt-2 text-4xl font-semibold">{contractor.reliabilityScore}</p>
              <ProgressBar value={contractor.reliabilityScore} />
              <p className="mt-3 text-sm text-slate-600">Based on completed-job reviews, response time, and repeat property manager feedback.</p>
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-4">
            <StatCard label="Completed jobs" value={String(contractor.completedJobs)} />
            <StatCard label="Typical job size" value={formatCurrency(contractor.estimateRange[0])} />
            <StatCard label="Repeat PM rating" value={contractor.repeatPropertyManagerRating.toFixed(1)} />
            <StatCard label="Best value score" value={String(calculateBestValueScore(contractor))} tone="success" />
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {jobs.slice(0, 4).map((job) => (
              <Card key={job.id} className="p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="font-semibold text-slate-950">{job.title}</h3>
                    <p className="mt-1 text-sm text-slate-600">{job.tradeCategory} • {job.urgency}</p>
                  </div>
                  <Badge tone={job.emergency ? "danger" : "default"}>{job.status}</Badge>
                </div>
                <p className="mt-3 text-sm text-slate-600">Budget {formatCurrency(job.budgetMin)} - {formatCurrency(job.budgetMax)}</p>
                <div className="mt-4 flex gap-2">
                  <LinkButton href={`/jobs/${job.id}/match`} className="w-full">View match</LinkButton>
                </div>
              </Card>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <SectionHeading
            eyebrow="Earnings and readiness"
            title="Contractor dashboard preview"
            description="This side of the platform is about qualified alerts, quote speed, and repeat customer retention."
          />
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <StatCard label="This month" value={formatCurrency(14850)} tone="success" />
            <StatCard label="Completed" value="18 jobs" tone="info" />
          </div>
          <div className="mt-6 space-y-4">
            <Card className="p-4">
              <p className="text-sm font-medium text-slate-950">Profile completion checklist</p>
              <ul className="mt-3 space-y-2 text-sm text-slate-600">
                <li>Business details and service areas</li>
                <li>License and insurance verification</li>
                <li>Response-time targets</li>
                <li>Quote template and warranty terms</li>
                <li>Reliability dashboard</li>
              </ul>
            </Card>
            <Card className="p-4">
              <p className="text-sm font-medium text-slate-950">Reviews from completed jobs only</p>
              <div className="mt-3 space-y-3">
                {contractorReviews.slice(0, 3).map((review) => (
                  <div key={review.id} className="rounded-xl bg-slate-50 p-3">
                    <div className="flex items-center justify-between gap-3">
                      <p className="font-medium text-slate-950">{review.reviewer}</p>
                      <Badge tone="success">{review.wouldHireAgain ? "Would hire again" : "Needs follow-up"}</Badge>
                    </div>
                    <p className="mt-2 text-sm text-slate-600">{review.note}</p>
                  </div>
                ))}
              </div>
            </Card>
            <Card className="border-slate-950 bg-slate-950 p-4 text-white">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-300">Subscription upsell</p>
              <p className="mt-2 text-lg font-semibold">Contractor Pro unlocks better visibility into qualified PM demand.</p>
              <p className="mt-2 text-sm text-slate-300">Priority alerts, quote tools, and reliability analytics for $39/month.</p>
              <Button variant="outline" className="mt-4 border-slate-700 bg-transparent text-white hover:bg-white/10">Upgrade plan</Button>
            </Card>
          </div>
        </Card>
      </div>
    </div>
  );
}
