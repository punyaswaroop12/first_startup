import { Badge, Card, LinkButton, SectionHeading } from "@/components/ui";
import { subscriptionPlans } from "@/lib/demo-data";
import { ArrowRight, Check, Coins, CreditCard } from "lucide-react";

export default function PricingPage() {
  return (
    <div className="container-pad py-8 md:py-12">
      <SectionHeading
        eyebrow="Pricing"
        title="Simple pricing that supports recurring maintenance operations."
        description="Subscriptions are the main revenue engine, with a light completed-job success fee layered on top."
      />

      <div className="mt-8 grid gap-4 lg:grid-cols-4">
        {subscriptionPlans.map((plan) => (
          <Card key={plan.name} className={plan.featured ? "border-slate-950 p-6" : "p-6"}>
            {plan.featured ? <Badge tone="success">Most popular</Badge> : null}
            <h3 className="mt-3 text-xl font-semibold">{plan.name}</h3>
            <p className="mt-2 text-3xl font-semibold">{plan.price}</p>
            <p className="mt-3 text-sm leading-6 text-slate-600">{plan.summary}</p>
            <ul className="mt-4 space-y-2 text-sm text-slate-700">
              {plan.features.map((feature) => (
                <li key={feature} className="flex items-start gap-2">
                  <Check size={16} className="mt-0.5 text-emerald-600" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
            <LinkButton href="/login" className="mt-6 w-full">
              Choose plan
              <ArrowRight size={16} />
            </LinkButton>
          </Card>
        ))}
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <Card className="p-6">
          <div className="flex items-center gap-2 text-sm font-medium text-slate-950">
            <Coins size={16} /> Platform fee
          </div>
          <h3 className="mt-3 text-2xl font-semibold">Optional 5% success fee on completed jobs</h3>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            The fee aligns revenue with actual maintenance outcomes and creates a path to monetization before deep integrations are in place.
          </p>
        </Card>
        <Card className="p-6">
          <div className="flex items-center gap-2 text-sm font-medium text-slate-950">
            <CreditCard size={16} /> Subscription mix
          </div>
          <h3 className="mt-3 text-2xl font-semibold">Designed for landlords, PMs, and vendors</h3>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            Landlords pay for workflow, property managers pay for scale, and contractors pay for verified access to repeat maintenance demand.
          </p>
        </Card>
      </div>
    </div>
  );
}
