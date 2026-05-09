import { Badge, Card, LinkButton, SectionHeading } from "@/components/ui";
import { Building2, Hammer, ShieldCheck, UserRound } from "lucide-react";

const roles = [
  {
    title: "Landlord / Property Manager",
    icon: Building2,
    href: "/dashboard",
    summary: "Track jobs, compare quotes, and manage preferred vendors."
  },
  {
    title: "Contractor",
    icon: Hammer,
    href: "/contractor",
    summary: "See matched jobs, submit quotes, and grow repeat property work."
  },
  {
    title: "Admin",
    icon: ShieldCheck,
    href: "/admin",
    summary: "Review verifications, disputes, and platform health."
  }
];

export default function LoginPage() {
  return (
    <div className="container-pad py-12">
      <SectionHeading
        eyebrow="Mock auth"
        title="Pick a role to preview the right workflow."
        description="This is a lightweight role switcher for the demo. Real authentication can be added later."
        action={<Badge tone="info">Demo only</Badge>}
      />
      <div className="mt-8 grid gap-4 lg:grid-cols-3">
        {roles.map((role) => {
          const Icon = role.icon;
          return (
            <Card key={role.title} className="p-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-950 text-white">
                <Icon size={20} />
              </div>
              <h2 className="mt-5 text-xl font-semibold">{role.title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">{role.summary}</p>
              <div className="mt-6">
                <LinkButton href={role.href} className="w-full">Continue</LinkButton>
              </div>
            </Card>
          );
        })}
      </div>
      <div className="mt-8 max-w-2xl rounded-2xl border border-slate-200 bg-white p-5 text-sm text-slate-600">
        <p className="font-medium text-slate-950">Why this exists</p>
        <p className="mt-2 leading-6">
          Investors and property managers need to see the product from their own point of view. This switcher keeps the demo simple without introducing a full auth stack yet.
        </p>
      </div>
    </div>
  );
}
