import { JobWizard } from "@/components/job-wizard";
import { SectionHeading } from "@/components/ui";

export default function NewJobPage() {
  return (
    <div className="container-pad py-8 md:py-12">
      <SectionHeading
        eyebrow="Create job"
        title="Post a maintenance job in a few guided steps."
        description="This flow is built for rental property maintenance intake: property, unit, urgency, access, and budget."
      />
      <div className="mt-8">
        <JobWizard />
      </div>
    </div>
  );
}
