import { Badge, Button, Card, SectionHeading, Table, TableCell, TableHeaderCell } from "@/components/ui";
import { calculateBestValueScore, estimateSanityNotes } from "@/lib/metrics";
import { contractors, jobs, properties, quotes } from "@/lib/demo-data";
import { formatCurrency, formatShortDate } from "@/lib/format";
import { BadgeCheck, Clock3, ShieldCheck, Sparkles } from "lucide-react";

export default async function QuotesPage({ params }: { params: Promise<{ jobId: string }> }) {
  const { jobId } = await params;
  const job = jobs.find((item) => item.id === jobId) ?? jobs[0];
  const property = properties.find((item) => item.id === job.propertyId)!;
  const jobQuotes = quotes.filter((quote) => quote.jobId === job.id).sort((a, b) => a.price - b.price);
  const bestQuote = jobQuotes[1] ?? jobQuotes[0];

  return (
    <div className="container-pad py-8 md:py-12">
      <SectionHeading
        eyebrow="Quote comparison"
        title={`${job.title} — side-by-side quotes`}
        description={`${property.name} • ${job.tradeCategory} • compare price, timeline, warranty, and reliability`}
      />

      <div className="mt-8 grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <Card className="p-6">
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone={job.emergency ? "danger" : "info"}>{job.urgency}</Badge>
            <Badge tone="success">{job.status}</Badge>
            <Badge>Job created {formatShortDate(job.createdAt)}</Badge>
          </div>
          <div className="mt-4 overflow-hidden rounded-2xl border border-slate-200">
            <Table>
              <table className="min-w-full">
                <thead className="bg-slate-50">
                  <tr>
                    <TableHeaderCell>Contractor</TableHeaderCell>
                    <TableHeaderCell>Price</TableHeaderCell>
                    <TableHeaderCell>Timeline</TableHeaderCell>
                    <TableHeaderCell>Warranty</TableHeaderCell>
                    <TableHeaderCell>License / insurance</TableHeaderCell>
                    <TableHeaderCell>Reliability</TableHeaderCell>
                    <TableHeaderCell>Completion rate</TableHeaderCell>
                  </tr>
                </thead>
                <tbody>
                  {jobQuotes.map((quote) => {
                    const contractor = contractors.find((item) => item.id === quote.contractorId)!;
                    const score = calculateBestValueScore(contractor, quote, job.budgetMax);
                    return (
                      <tr key={quote.id} className={quote.id === bestQuote?.id ? "border-t border-slate-100 bg-slate-50/80" : "border-t border-slate-100"}>
                        <TableCell>
                          <div>
                            <p className="font-medium text-slate-950">{contractor.businessName}</p>
                            <p className="text-xs text-slate-500">{contractor.trade}</p>
                            <p className="mt-1 text-xs text-slate-500">Best value score {score}</p>
                          </div>
                        </TableCell>
                        <TableCell className="font-medium text-slate-950">{formatCurrency(quote.price)}</TableCell>
                        <TableCell>{quote.timelineDays}</TableCell>
                        <TableCell>{quote.warranty}</TableCell>
                        <TableCell>
                          <div className="space-y-1 text-xs">
                            <p className="flex items-center gap-1"><BadgeCheck size={13} /> {contractor.verifiedLicense ? "Verified license" : "License pending"}</p>
                            <p className="flex items-center gap-1"><ShieldCheck size={13} /> {contractor.verifiedInsurance ? "Insured" : "Insurance pending"}</p>
                          </div>
                        </TableCell>
                        <TableCell>{contractor.reliabilityScore}</TableCell>
                        <TableCell>{Math.round(quote.completionRate)}%</TableCell>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </Table>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {jobQuotes.map((quote) => {
              const contractor = contractors.find((item) => item.id === quote.contractorId)!;
              return (
                <Card key={quote.id} className={quote.id === bestQuote?.id ? "border-slate-950 p-5" : "p-5"}>
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h3 className="font-semibold text-slate-950">{contractor.businessName}</h3>
                      <p className="text-sm text-slate-600">{formatCurrency(quote.price)} • {quote.timelineDays}</p>
                    </div>
                    <Badge tone={quote.id === bestQuote?.id ? "success" : "default"}>{quote.id === bestQuote?.id ? "Best value" : "Comparable"}</Badge>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600">{quote.notes}</p>
                  <div className="mt-4 grid gap-2 text-xs text-slate-500 sm:grid-cols-2">
                    <p className="flex items-center gap-2"><Clock3 size={14} /> Response {quote.responseMinutes} min</p>
                    <p className="flex items-center gap-2"><Sparkles size={14} /> Materials {quote.materialsIncluded ? "included" : "not included"}</p>
                  </div>
                  <Button className="mt-4 w-full">Accept quote</Button>
                </Card>
              );
            })}
          </div>
        </Card>

        <Card className="p-6">
          <SectionHeading
            eyebrow="AI-style estimate sanity check"
            title="Deterministic guidance"
            description="This is intentionally mock logic, not a live AI API, so the demo stays safe and predictable."
          />
          <div className="mt-6 space-y-4">
            {estimateSanityNotes(bestQuote.price, job.estimateMin, job.estimateMax, bestQuote.responseMinutes).map((note) => (
              <Card key={note} className="p-4">
                <p className="text-sm leading-6 text-slate-700">{note}</p>
              </Card>
            ))}
          </div>
          <Card className="mt-6 p-4">
            <p className="text-sm font-medium text-slate-950">Recommendation</p>
            <p className="mt-2 text-sm text-slate-600">
              Choose the moderate-price quote with the strongest reliability score and the cleanest communication history.
            </p>
          </Card>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            <Card className="p-4">
              <p className="text-xs text-slate-500">Expected range</p>
              <p className="mt-1 text-lg font-semibold">{formatCurrency(job.estimateMin)} - {formatCurrency(job.estimateMax)}</p>
            </Card>
            <Card className="p-4">
              <p className="text-xs text-slate-500">Budget</p>
              <p className="mt-1 text-lg font-semibold">{formatCurrency(job.budgetMin)} - {formatCurrency(job.budgetMax)}</p>
            </Card>
          </div>
        </Card>
      </div>
    </div>
  );
}
