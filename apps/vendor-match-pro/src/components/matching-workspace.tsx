import { Badge, Button, Card, ProgressBar, SectionHeading } from "@/components/ui";
import { calculateBestValueScore, estimateSanityNotes } from "@/lib/metrics";
import { contractors, jobs, properties, quotes } from "@/lib/demo-data";
import { formatCurrency, formatShortDate } from "@/lib/format";
import { BadgeCheck, Clock3, MessageCircle, MapPin, ShieldCheck, Star } from "lucide-react";

export function MatchingWorkspace({ jobId, submitted }: { jobId: string; submitted?: boolean }) {
  const job = jobs.find((item) => item.id === jobId) ?? jobs[0];
  const property = properties.find((item) => item.id === job.propertyId)!;
  const jobQuotes = quotes.filter((quote) => quote.jobId === job.id);

  const matchingPool = contractors.filter(
    (contractor) =>
      contractor.trade.toLowerCase().includes(job.tradeCategory.toLowerCase().split(" ")[0]) ||
      contractor.serviceAreas.some((area) => area.toLowerCase().includes("cleveland"))
  );

  const rankedContractors = (matchingPool.length > 0 ? matchingPool : contractors)
    .slice(0, 6)
    .map((contractor) => {
      const quote = jobQuotes.find((item) => item.contractorId === contractor.id);
      return {
        contractor,
        quote,
        score: calculateBestValueScore(contractor, quote, job.budgetMax)
      };
    })
    .sort((a, b) => b.score - a.score);

  return (
    <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
      <Card className="p-6">
        {submitted ? (
          <div className="mb-5 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
            Job posted successfully. Matching contractors now.
          </div>
        ) : null}
        <SectionHeading
          eyebrow="Matching page"
          title={`${job.title}`}
          description={`${property.name} • ${job.unit} • ${job.tradeCategory} • ${job.urgency}`}
          action={<Badge tone={job.emergency ? "danger" : "info"}>{job.status}</Badge>}
        />
        <div className="mt-6 grid gap-3 md:grid-cols-3">
          <Card className="p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Budget</p>
            <p className="mt-2 text-xl font-semibold">{formatCurrency(job.budgetMin)} - {formatCurrency(job.budgetMax)}</p>
          </Card>
          <Card className="p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Quotes</p>
            <p className="mt-2 text-xl font-semibold">{job.quotesCount}</p>
          </Card>
          <Card className="p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Preferred vendors</p>
            <p className="mt-2 text-xl font-semibold">{rankedContractors.length}</p>
          </Card>
        </div>

        <div className="mt-6 space-y-4">
          {rankedContractors.map(({ contractor, quote, score }, index) => (
            <Card key={contractor.id} className={index === 0 ? "border-slate-950 p-5" : "p-5"}>
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="space-y-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="text-lg font-semibold">{contractor.businessName}</h3>
                    <Badge tone={contractor.featured ? "success" : "default"}>{contractor.trade}</Badge>
                    {contractor.emergencyAvailability ? <Badge tone="danger">Emergency</Badge> : null}
                  </div>
                  <p className="text-sm text-slate-600">{contractor.name} • {contractor.serviceAreas.join(", ")}</p>
                  <div className="grid gap-2 text-sm text-slate-600 sm:grid-cols-2">
                    <div className="flex items-center gap-2"><MapPin size={14} /> Service area fit</div>
                    <div className="flex items-center gap-2"><Clock3 size={14} /> {contractor.responseTimeMinutes} min response</div>
                    <div className="flex items-center gap-2"><ShieldCheck size={14} /> License {contractor.verifiedLicense ? "verified" : "pending"}</div>
                    <div className="flex items-center gap-2"><BadgeCheck size={14} /> Insurance {contractor.verifiedInsurance ? "verified" : "pending"}</div>
                  </div>
                </div>
                <div className="w-full max-w-xs rounded-2xl bg-slate-50 p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Best Value Score</p>
                  <p className="mt-2 text-3xl font-semibold">{score}</p>
                  <ProgressBar value={score} />
                  <p className="mt-2 text-sm text-slate-600">
                    Reliability and quote fit weighted ahead of cheapest price.
                  </p>
                </div>
              </div>

              <div className="mt-5 grid gap-3 sm:grid-cols-4">
                <Card className="p-3">
                  <p className="text-xs text-slate-500">Estimated price</p>
                  <p className="mt-1 font-semibold">{quote ? formatCurrency(quote.price) : formatCurrency(contractor.estimateRange[0])}</p>
                </Card>
                <Card className="p-3">
                  <p className="text-xs text-slate-500">Timeline</p>
                  <p className="mt-1 font-semibold">{quote?.timelineDays ?? "1-3 days"}</p>
                </Card>
                <Card className="p-3">
                  <p className="text-xs text-slate-500">Completed jobs</p>
                  <p className="mt-1 font-semibold">{contractor.completedJobs}</p>
                </Card>
                <Card className="p-3">
                  <p className="text-xs text-slate-500">Reliability</p>
                  <p className="mt-1 font-semibold">{contractor.reliabilityScore}</p>
                </Card>
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                <Button variant={index === 0 ? "primary" : "outline"}>Request quote</Button>
                <Button variant="outline">
                  <MessageCircle size={16} />
                  Message
                </Button>
                <Button variant="outline">Save preferred vendor</Button>
              </div>
            </Card>
          ))}
        </div>
      </Card>

      <Card className="p-6">
        <SectionHeading eyebrow="Best value formula" title="Why this contractor ranks well" description="We score the vendor on reliability, price fit, response speed, proximity, verification, and repeat-property-manager results." />
        <div className="mt-6 space-y-4">
          <Card className="p-4">
            <p className="text-sm font-medium text-slate-950">Score formula</p>
            <div className="mt-3 space-y-2 text-sm text-slate-600">
              <p>30% reliability</p>
              <p>20% price competitiveness</p>
              <p>20% response time</p>
              <p>15% proximity / service area fit</p>
              <p>10% verified license / insurance</p>
              <p>5% repeat-property-manager rating</p>
            </div>
          </Card>
          <Card className="p-4">
            <p className="text-sm font-medium text-slate-950">Estimate sanity check</p>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              {estimateSanityNotes(rankedContractors[0]?.quote?.price ?? job.budgetMax, job.estimateMin, job.estimateMax, job.responseTimeMinutes).map((note) => (
                <li key={note}>• {note}</li>
              ))}
            </ul>
          </Card>
          <Card className="p-4">
            <p className="text-sm font-medium text-slate-950">Recent message</p>
            <p className="mt-2 text-sm text-slate-600">
              {job.description}
            </p>
            <p className="mt-4 text-xs text-slate-500">Posted {formatShortDate(job.createdAt)}</p>
          </Card>
        </div>
      </Card>
    </div>
  );
}
