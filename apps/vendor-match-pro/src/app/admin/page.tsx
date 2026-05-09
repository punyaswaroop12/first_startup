import { Badge, Button, Card, SectionHeading, StatCard } from "@/components/ui";
import { invoices, contractors, verificationQueue, reviews, jobs } from "@/lib/demo-data";
import { formatCurrency, formatShortDate } from "@/lib/format";
import { AlertTriangle, BadgeCheck, ShieldAlert, ShieldCheck, TrendingUp, Users } from "lucide-react";

export default function AdminPage() {
  const platformRevenue = invoices.reduce((sum, invoice) => sum + (invoice.status === "paid" ? invoice.amount : 0), 0) + 8120;

  return (
    <div className="container-pad py-8 md:py-12">
      <SectionHeading
        eyebrow="Admin"
        title="Verification, disputes, and marketplace health."
        description="This view is for reviewing contractor quality, platform revenue, and high-risk jobs."
      />

      <div className="mt-8 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Card className="p-6">
          <div className="grid gap-4 md:grid-cols-4">
            <StatCard label="Platform revenue" value={formatCurrency(platformRevenue)} tone="success" />
            <StatCard label="Subscription counts" value="3 plans active" tone="info" />
            <StatCard label="Transaction volume" value={formatCurrency(28460)} tone="warning" />
            <StatCard label="High-risk jobs" value={String(jobs.filter((job) => job.emergency).length)} tone="default" />
          </div>
          <div className="mt-6 grid gap-4 lg:grid-cols-2">
            <Card className="p-4">
              <p className="text-sm font-medium text-slate-950">New contractors awaiting verification</p>
              <div className="mt-3 space-y-3">
                {verificationQueue.slice(0, 5).map((item) => {
                  const contractor = contractors.find((entry) => entry.id === item.contractorId)!;
                  return (
                    <div key={item.contractorId} className="rounded-xl bg-slate-50 p-3">
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <p className="font-medium text-slate-950">{contractor.businessName}</p>
                          <p className="text-xs text-slate-500">{contractor.trade} • {contractor.licenseNumber}</p>
                        </div>
                        <Badge tone={item.riskLevel === "High" ? "danger" : item.riskLevel === "Medium" ? "warning" : "success"}>{item.riskLevel} risk</Badge>
                      </div>
                      <div className="mt-3 flex flex-wrap gap-2">
                        <Button variant="outline">Approve contractor</Button>
                        <Button variant="outline">Mark license verified</Button>
                        <Button variant="outline">Mark insurance verified</Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>

            <Card className="p-4">
              <p className="text-sm font-medium text-slate-950">Reported disputes</p>
              <div className="mt-3 space-y-3">
                {jobs.slice(12, 15).map((job) => (
                  <div key={job.id} className="rounded-xl bg-slate-50 p-3">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-medium text-slate-950">{job.title}</p>
                        <p className="text-xs text-slate-500">{job.status} • {formatShortDate(job.createdAt)}</p>
                      </div>
                      <Badge tone="danger">Dispute</Badge>
                    </div>
                    <div className="mt-3 flex gap-2">
                      <Button variant="outline">Resolve dispute</Button>
                      <Button variant="outline">Suspend contractor</Button>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </Card>

        <Card className="p-6">
          <SectionHeading
            eyebrow="Quality"
            title="Contractor quality metrics"
            description="Useful operational stats for monitoring vendor reliability at the platform level."
          />
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <StatCard label="Verified contractors" value={String(contractors.filter((item) => item.verifiedLicense && item.verifiedInsurance).length)} />
            <StatCard label="Featured contractors" value={String(contractors.filter((item) => item.featured).length)} tone="success" />
          </div>
          <div className="mt-6 space-y-3">
            <Card className="p-4">
              <div className="flex items-center gap-2 text-sm font-medium text-slate-950"><TrendingUp size={16} /> Reliability distribution</div>
              <p className="mt-2 text-sm text-slate-600">Most active vendors sit above 85 reliability, with priority placement reserved for the strongest repeat-property manager history.</p>
            </Card>
            <Card className="p-4">
              <div className="flex items-center gap-2 text-sm font-medium text-slate-950"><Users size={16} /> Completed-job reviews only</div>
              <p className="mt-2 text-sm text-slate-600">{reviews.length} reviews are tied to completed work, not open-ended lead activity.</p>
            </Card>
            <Card className="p-4">
              <div className="flex items-center gap-2 text-sm font-medium text-slate-950"><ShieldCheck size={16} /> License and insurance status</div>
              <p className="mt-2 text-sm text-slate-600">Verification can be flipped manually in the admin workflow until document automation is added.</p>
            </Card>
          </div>
        </Card>
      </div>
    </div>
  );
}
