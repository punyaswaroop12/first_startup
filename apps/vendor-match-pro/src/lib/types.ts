export type UserRole = "landlord" | "contractor" | "admin" | "homeowner";

export type JobStatus =
  | "Draft"
  | "Posted"
  | "Quotes Requested"
  | "Quotes Received"
  | "Contractor Selected"
  | "Scheduled"
  | "In Progress"
  | "Completed"
  | "Reviewed"
  | "Disputed";

export type Urgency = "Emergency" | "Within 24 hours" | "This week" | "Flexible";
export type TradeCategory =
  | "Plumbing"
  | "Electrical"
  | "HVAC"
  | "Roofing"
  | "General handyman"
  | "Inspection"
  | "Appliance repair"
  | "Landscaping"
  | "Cleaning / turnover";

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  organization: string;
}

export interface PropertyUnit {
  id: string;
  label: string;
  status: "occupied" | "turnover" | "vacant";
}

export interface Property {
  id: string;
  ownerId: string;
  name: string;
  address: string;
  city: string;
  neighborhood: string;
  units: number;
  openIssues: number;
  monthlyMaintenanceSpend: number;
  occupancyRate: number;
  manager: string;
  unitsDetail: PropertyUnit[];
}

export interface Contractor {
  id: string;
  name: string;
  businessName: string;
  trade: TradeCategory | string;
  serviceAreas: string[];
  estimateRange: [number, number];
  licenseNumber: string;
  insuranceExpiration: string;
  emergencyAvailability: boolean;
  responseTimeMinutes: number;
  reliabilityScore: number;
  completedJobs: number;
  repeatPropertyManagerRating: number;
  verifiedLicense: boolean;
  verifiedInsurance: boolean;
  featured: boolean;
  active: boolean;
}

export interface MaintenanceJob {
  id: string;
  title: string;
  propertyId: string;
  unit: string;
  tradeCategory: TradeCategory;
  urgency: Urgency;
  status: JobStatus;
  quotesCount: number;
  estimateMin: number;
  estimateMax: number;
  assignedContractorId: string | null;
  description: string;
  accessInstructions: string;
  budgetMin: number;
  budgetMax: number;
  createdAt: string;
  responseTimeMinutes: number;
  messages: number;
  emergency: boolean;
}

export interface Quote {
  id: string;
  jobId: string;
  contractorId: string;
  price: number;
  timelineDays: string;
  warranty: string;
  materialsIncluded: boolean;
  notes: string;
  responseMinutes: number;
  completionRate: number;
}

export interface Review {
  id: string;
  jobId: string;
  contractorId: string;
  reviewer: string;
  date: string;
  showedUpOnTime: number;
  priceMatchedQuote: number;
  qualityOfWork: number;
  communication: number;
  wouldHireAgain: boolean;
  note: string;
}

export interface Message {
  id: string;
  jobId: string;
  from: string;
  body: string;
  createdAt: string;
}

export interface SubscriptionPlan {
  name: string;
  audience: string;
  price: string;
  summary: string;
  features: string[];
  featured?: boolean;
}

export interface Invoice {
  id: string;
  description: string;
  amount: number;
  status: "pending" | "paid" | "failed";
  createdAt: string;
}

export interface VerificationItem {
  contractorId: string;
  licenseVerified: boolean;
  insuranceVerified: boolean;
  riskLevel: "Low" | "Medium" | "High";
  featured: boolean;
}
