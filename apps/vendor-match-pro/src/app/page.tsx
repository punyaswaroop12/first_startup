import Link from "next/link";
import { ArrowRight, BadgeCheck, Clock3, MessageSquareText, ShieldCheck, Star, TrendingUp, Wrench } from "lucide-react";
import { Badge, Button, Card, LinkButton, ProgressBar, SectionHeading, StatCard } from "@/components/ui";
import { calculateBestValueScore } from "@/lib/metrics";
import { contractors, jobs, marketSignals, performanceBenchmarks, properties, reviews, subscriptionPlans } from "@/lib/demo-data";
import { formatCurrency, formatPercent } from "@/lib/format";

const featuredContractor = contractors.find((contractor) => contractor.featured) ?? contractors[0];
const featuredJob = jobs[0];
const avgReliability = Math.round(contractors.reduce((sum, contractor) => sum + contractor.reliabilityScore, 0) / contractors.length);

export default function HomePage() {
  return (
    <div className="bg-slate-50">
      <section className="relative overflow-hidden border-b border-slate-200 bg-slate-950 text-white">
        <div className="absolute inset-0 subtle-grid opacity-25" />
        <div className="container-pad relative grid gap-10 py-16 lg:grid-cols-[1.1fr_0.9fr] lg:items-center lg:py-20">
          <div className="space-y-6">
            <Badge tone="info" className="bg-sky-500/15 text-sky-100">Property-manager-first maintenance marketplace</Badge>
            <div className="space-y-4">
              <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-balance md:text-5xl">
                Find reliable contractors for rental property maintenance faster, cheaper, and with less chaos.
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-slate-300">
                UnitDispatch helps landlords and small property managers post jobs, compare quotes, and keep recurring vendor relationships organized in one place.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <LinkButton href="/jobs/new" className="bg-sky-500 text-slate-950 hover:bg-sky-400">
                Post a maintenance job
                <ArrowRight size={16} />
              </LinkButton>
              <LinkButton href="/contractor" variant="outline" className="border-slate-700 bg-transparent text-white hover:bg-white/10">
                Join as a contractor
              </LinkButton>
              <LinkButton href="/dashboard" variant="outline" className="border-slate-700 bg-transparent text-white hover:bg-white/10">
                View demo dashboard
              </LinkButton>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              {marketSignals.map((signal) => (
                <Card key={signal.label} className="border-slate-800 bg-slate-900/60 p-4 text-white">
                  <p className="text-sm text-slate-400">{signal.label}</p>
                  <p className="mt-2 text-2xl font-semibold">{signal.value}</p>
                </Card>
              ))}
            </div>
          </div>

          <Card className="border-slate-800 bg-white p-5 text-slate-950 shadow-panel">
            <div className="flex items-center justify-between gap-3 border-b border-slate-200 pb-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sky-700">Live maintenance board</p>
                <h2 className="mt-1 text-xl font-semibold">Dispatch command center</h2>
              </div>
              <Badge tone="success">Cleveland demo</Badge>
            </div>
            <div className="mt-5 space-y-4">
              <div className="grid gap-3 sm:grid-cols-2">
                <StatCard label="Open jobs" value={String(jobs.filter((job) => job.status !== "Reviewed").length)} detail="Emergency and planned work across 10 properties." />
                <StatCard label="Quotes received" value={String(jobs.reduce((sum, job) => sum + job.quotesCount, 0))} detail="Multiple bids per job with response-time tracking." />
                <StatCard label="Avg response time" value={`${performanceBenchmarks.averageResponseMinutes} min`} detail="Measured from posting to first qualified reply." />
                <StatCard label="Savings from compare" value={formatCurrency(performanceBenchmarks.averageSavings)} detail="Compared with top-line estimate ranges." />
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-sm font-medium text-slate-500">Featured vendor</p>
                    <h3 className="text-lg font-semibold">{featuredContractor.businessName}</h3>
                    <p className="text-sm text-slate-600">{featuredContractor.trade} • {featuredContractor.serviceAreas.join(", ")}</p>
                  </div>
                  <Badge tone="info">Reliability {featuredContractor.reliabilityScore}</Badge>
                </div>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Best value score</p>
                    <p className="mt-1 text-3xl font-semibold">{calculateBestValueScore(featuredContractor)} / 100</p>
                    <ProgressBar value={calculateBestValueScore(featuredContractor)} />
                  </div>
                  <div className="space-y-2 text-sm text-slate-600">
                    <div className="flex items-center gap-2"><BadgeCheck size={16} /> License and insurance verified</div>
                    <div className="flex items-center gap-2"><Clock3 size={16} /> Response in about {featuredContractor.responseTimeMinutes} minutes</div>
                    <div className="flex items-center gap-2"><ShieldCheck size={16} /> {featuredContractor.completedJobs} completed jobs</div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </section>

      <section className="container-pad py-16">
        <SectionHeading
          eyebrow="Why this works"
          title="Built for recurring rental maintenance, not generic lead spam."
          description="Property managers need repeat vendors, quote comparison, and fast dispatch, not another homeowner directory."
        />
        <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {[
            "Verified completed-job reviews only",
            "Reliability score instead of generic stars",
            "Quote comparison with sanity checks",
            "Recurring vendor relationships",
            "Maintenance ticket tracking",
            "Preferred vendor network and emergency dispatch readiness"
          ].map((item) => (
            <Card key={item} className="p-5">
              <div className="flex items-start gap-3">
                <div className="rounded-xl bg-slate-950 p-2 text-white">
                  <Wrench size={16} />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-950">{item}</h3>
                  <p className="mt-1 text-sm leading-6 text-slate-600">
                    Designed to reduce vendor ghosting, invoice confusion, and property-manager follow-up work.
                  </p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </section>

      <section className="bg-white py-16">
        <div className="container-pad">
          <SectionHeading
            eyebrow="Why we win"
            title="Better than generic contractor marketplaces"
            description="We optimize for reliability, recurring revenue, and property operations instead of one-time homeowner leads."
          />
          <div className="mt-8 grid gap-4 lg:grid-cols-2">
            <Card className="p-6">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Generic marketplaces</p>
              <ul className="mt-4 space-y-3 text-sm text-slate-700">
                <li>Lead spam and poor-intent inquiries</li>
                <li>Star ratings without job context</li>
                <li>Homeowner-first workflows</li>
                <li>Hard to compare quotes consistently</li>
                <li>No maintenance ticket history</li>
              </ul>
            </Card>
            <Card className="p-6 border-slate-950">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">UnitDispatch</p>
              <ul className="mt-4 space-y-3 text-sm text-slate-700">
                <li>Less lead spam and more qualified jobs</li>
                <li>Property-manager-first recurring workflow</li>
                <li>Verified completed-job reviews and documentation</li>
                <li>Reliability score, quote accuracy tracking, and preferred vendors</li>
                <li>Emergency dispatch and maintenance history built in</li>
              </ul>
            </Card>
          </div>
        </div>
      </section>

      <section className="container-pad py-16">
        <SectionHeading
          eyebrow="Pricing teaser"
          title="Simple monetization that fits the workflow."
          description="The business model combines subscriptions with a light success fee for completed jobs."
          action={<LinkButton href="/pricing">See pricing</LinkButton>}
        />
        <div className="mt-8 grid gap-4 lg:grid-cols-4">
          {subscriptionPlans.map((plan) => (
            <Card key={plan.name} className={plan.featured ? "border-slate-950 p-6" : "p-6"}>
              <p className="text-sm font-semibold text-slate-500">{plan.audience}</p>
              <h3 className="mt-2 text-xl font-semibold">{plan.name}</h3>
              <p className="mt-2 text-3xl font-semibold">{plan.price}</p>
              <p className="mt-3 text-sm leading-6 text-slate-600">{plan.summary}</p>
              <ul className="mt-4 space-y-2 text-sm text-slate-700">
                {plan.features.slice(0, 4).map((feature) => <li key={feature}>• {feature}</li>)}
              </ul>
            </Card>
          ))}
        </div>
      </section>

      <section className="container-pad py-12">
        <Card className="grid gap-6 p-6 md:grid-cols-[1.2fr_0.8fr] md:items-center">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-700">Demo snapshot</p>
            <h3 className="mt-2 text-2xl font-semibold">Cleveland properties, live vendor rankings, and job history.</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              {properties.length} properties, {contractors.length} contractors, {jobs.length} jobs, and {reviews.length} completed-job reviews are seeded for the investor demo.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <StatCard label="Average contractor reliability" value={String(avgReliability)} />
            <StatCard label="Projected savings" value={formatCurrency(performanceBenchmarks.averageSavings)} />
          </div>
        </Card>
      </section>

      <section className="container-pad pb-16">
        <Card className="flex flex-col gap-4 p-6 md:flex-row md:items-center md:justify-between">
          <div>
            <h3 className="text-2xl font-semibold">Ready to demo the workflow?</h3>
            <p className="mt-2 text-sm text-slate-600">Open a dashboard, post a job, and show the quote comparison in under five minutes.</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <LinkButton href="/jobs/new">Post a maintenance job</LinkButton>
            <LinkButton href="/dashboard" variant="outline">View demo dashboard</LinkButton>
          </div>
        </Card>
      </section>
    </div>
  );
}
