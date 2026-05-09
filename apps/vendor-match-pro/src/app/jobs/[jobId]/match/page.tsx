import { notFound } from "next/navigation";
import { MatchingWorkspace } from "@/components/matching-workspace";
import { SectionHeading } from "@/components/ui";
import { jobs } from "@/lib/demo-data";

export default async function MatchPage({
  params,
  searchParams
}: {
  params: Promise<{ jobId: string }>;
  searchParams?: Promise<{ submitted?: string }>;
}) {
  const { jobId } = await params;
  const submitted = searchParams ? (await searchParams).submitted === "1" : false;
  const jobExists = jobs.some((item) => item.id === jobId);
  if (!jobExists && jobId !== "job-001") notFound();

  return (
    <div className="container-pad py-8 md:py-12">
      <SectionHeading
        eyebrow="Vendor matching"
        title="Recommended contractors for this job"
        description="The list below is ranked by Best Value Score, not lowest price alone."
      />
      <div className="mt-8">
        <MatchingWorkspace jobId={jobId} submitted={submitted} />
      </div>
    </div>
  );
}
