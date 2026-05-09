"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, CheckCircle2, ImagePlus, Upload } from "lucide-react";
import { Badge, Button, Card, Input, Select, Textarea } from "@/components/ui";
import { jobs, properties } from "@/lib/demo-data";
import type { TradeCategory, Urgency } from "@/lib/types";
import { cn } from "@/lib/utils";

const trades: TradeCategory[] = [
  "Plumbing",
  "Electrical",
  "HVAC",
  "Roofing",
  "General handyman",
  "Inspection",
  "Appliance repair",
  "Landscaping",
  "Cleaning / turnover"
];

const urgencies: Urgency[] = ["Emergency", "Within 24 hours", "This week", "Flexible"];

export function JobWizard() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [submitted, setSubmitted] = useState(false);
  const [property, setProperty] = useState(properties[0].id);
  const [unit, setUnit] = useState(properties[0].unitsDetail[0].label);
  const [trade, setTrade] = useState<TradeCategory>("Plumbing");
  const [urgency, setUrgency] = useState<Urgency>("Within 24 hours");
  const [description, setDescription] = useState("Describe the issue, symptoms, and any repeat work that should be avoided.");
  const [access, setAccess] = useState("Tenant can provide access between 10am and 4pm. Call 20 minutes ahead.");
  const [budget, setBudget] = useState("200-500");

  const selectedProperty = useMemo(() => properties.find((item) => item.id === property) ?? properties[0], [property]);

  const steps = [
    "Property and unit",
    "Category",
    "Urgency",
    "Job description",
    "Upload photos",
    "Access instructions",
    "Budget range",
    "Submit"
  ];

  const next = () => setStep((current) => Math.min(current + 1, steps.length));
  const back = () => setStep((current) => Math.max(current - 1, 1));

  const submit = () => {
    setSubmitted(true);
    router.push("/jobs/job-001/match?submitted=1");
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[0.74fr_0.26fr]">
      <Card className="p-6">
        <div className="flex items-center justify-between gap-4 border-b border-slate-200 pb-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sky-700">Step {step} of 8</p>
            <h2 className="mt-1 text-xl font-semibold">{steps[step - 1]}</h2>
          </div>
          <Badge tone={step >= 7 ? "success" : "info"}>{submitted ? "Submitted" : "Draft"}</Badge>
        </div>

        <div className="mt-6">
          {step === 1 ? (
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="mb-2 text-sm font-medium text-slate-700">Property</p>
                <Select value={property} onChange={(event) => {
                  setProperty(event.target.value);
                  const nextProperty = properties.find((item) => item.id === event.target.value) ?? properties[0];
                  setUnit(nextProperty.unitsDetail[0].label);
                }}>
                  {properties.map((item) => <option key={item.id} value={item.id}>{item.name} • {item.address}</option>)}
                </Select>
              </div>
              <div>
                <p className="mb-2 text-sm font-medium text-slate-700">Unit</p>
                <Select value={unit} onChange={(event) => setUnit(event.target.value)}>
                  {selectedProperty.unitsDetail.map((item) => <option key={item.id} value={item.label}>{item.label}</option>)}
                </Select>
              </div>
            </div>
          ) : null}

          {step === 2 ? (
            <div>
              <p className="mb-2 text-sm font-medium text-slate-700">Trade category</p>
              <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3">
                {trades.map((item) => (
                  <button
                    key={item}
                    className={cn(
                      "rounded-2xl border px-4 py-3 text-left text-sm transition",
                      trade === item ? "border-slate-950 bg-slate-950 text-white" : "border-slate-200 bg-white hover:border-slate-300"
                    )}
                    onClick={() => setTrade(item)}
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          ) : null}

          {step === 3 ? (
            <div>
              <p className="mb-2 text-sm font-medium text-slate-700">Urgency</p>
              <div className="grid gap-3 sm:grid-cols-2">
                {urgencies.map((item) => (
                  <button
                    key={item}
                    className={cn(
                      "rounded-2xl border px-4 py-3 text-left text-sm transition",
                      urgency === item ? "border-slate-950 bg-slate-950 text-white" : "border-slate-200 bg-white hover:border-slate-300"
                    )}
                    onClick={() => setUrgency(item)}
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          ) : null}

          {step === 4 ? (
            <div>
              <p className="mb-2 text-sm font-medium text-slate-700">Job description</p>
              <Textarea value={description} onChange={(event) => setDescription(event.target.value)} />
            </div>
          ) : null}

          {step === 5 ? (
            <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center">
              <ImagePlus className="mx-auto text-slate-500" size={26} />
              <p className="mt-3 font-medium text-slate-950">Upload photos placeholder</p>
              <p className="mt-1 text-sm text-slate-600">Image upload is mocked for the MVP demo. The workflow is structured for future storage integration.</p>
              <Button variant="outline" className="mt-4">
                <Upload size={16} />
                Add photos
              </Button>
            </div>
          ) : null}

          {step === 6 ? (
            <div>
              <p className="mb-2 text-sm font-medium text-slate-700">Access instructions</p>
              <Textarea value={access} onChange={(event) => setAccess(event.target.value)} />
            </div>
          ) : null}

          {step === 7 ? (
            <div>
              <p className="mb-2 text-sm font-medium text-slate-700">Budget range</p>
              <Input value={budget} onChange={(event) => setBudget(event.target.value)} placeholder="200-500" />
              <p className="mt-2 text-sm text-slate-500">Use a realistic range to improve quote quality and contractor response time.</p>
            </div>
          ) : null}

          {step === 8 ? (
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="flex items-center gap-2 text-sm font-medium text-slate-950">
                <CheckCircle2 size={16} className="text-emerald-600" />
                Review before posting
              </div>
              <div className="mt-4 grid gap-3 text-sm text-slate-700 sm:grid-cols-2">
                <p><span className="font-medium">Property:</span> {selectedProperty.name}</p>
                <p><span className="font-medium">Unit:</span> {unit}</p>
                <p><span className="font-medium">Category:</span> {trade}</p>
                <p><span className="font-medium">Urgency:</span> {urgency}</p>
                <p><span className="font-medium">Budget:</span> {budget}</p>
                <p><span className="font-medium">Route:</span> Matching page with quotes</p>
              </div>
            </div>
          ) : null}
        </div>

        <div className="mt-6 flex items-center justify-between gap-3 border-t border-slate-200 pt-4">
          <Button variant="outline" onClick={back} disabled={step === 1}>Back</Button>
          {step < steps.length ? (
            <Button onClick={next}>
              Continue
              <ArrowRight size={16} />
            </Button>
          ) : (
            <Button onClick={submit}>
              Post job and match vendors
              <ArrowRight size={16} />
            </Button>
          )}
        </div>
      </Card>

      <Card className="p-5">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sky-700">Demo support</p>
        <h3 className="mt-2 text-lg font-semibold">What this form captures</h3>
        <ul className="mt-4 space-y-3 text-sm text-slate-600">
          <li>Property and unit</li>
          <li>Trade and urgency</li>
          <li>Photos and access notes</li>
          <li>Budget range for cleaner quote comparison</li>
          <li>Routing directly into matching and quote comparison</li>
        </ul>
        <div className="mt-6 rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">
          <p className="font-medium text-slate-950">Seeded demo context</p>
          <p className="mt-2">The app already contains {jobs.length} maintenance jobs across Cleveland-area rental properties.</p>
        </div>
      </Card>
    </div>
  );
}
