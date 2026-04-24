import { Badge } from "@/components/ui/badge";

export function PageHeader({
  eyebrow,
  title,
  description,
  tag
}: {
  eyebrow: string;
  title: string;
  description: string;
  tag?: string;
}) {
  return (
    <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate">{eyebrow}</p>
        <h1 className="mt-3 text-3xl font-semibold text-ink">{title}</h1>
        <p className="mt-3 max-w-2xl text-sm leading-7 text-slate">{description}</p>
      </div>
      {tag ? <Badge tone="accent">{tag}</Badge> : null}
    </div>
  );
}

