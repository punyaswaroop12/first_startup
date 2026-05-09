import type {
  Contractor,
  Invoice,
  JobStatus,
  MaintenanceJob,
  Message,
  Property,
  Quote,
  Review,
  SubscriptionPlan,
  TradeCategory,
  User,
  VerificationItem
} from "@/lib/types";

export const managers: User[] = [
  { id: "u-1", name: "Maya Carter", email: "maya@harborviewpm.com", role: "landlord", organization: "Harbor View PM" },
  { id: "u-2", name: "Ethan Ross", email: "ethan@northstarholdings.com", role: "landlord", organization: "Northstar Holdings" },
  { id: "u-3", name: "Sofia Nguyen", email: "sofia@lakefrontflats.com", role: "landlord", organization: "Lakefront Flats" },
  { id: "u-4", name: "Derrick Brooks", email: "derrick@clevelandturnkey.com", role: "landlord", organization: "Cleveland Turnkey" },
  { id: "u-5", name: "Priya Shah", email: "priya@summitdoor.com", role: "landlord", organization: "Summit Door Properties" }
];

const propertyBlueprints = [
  ["Lakewood Duplex", "1458 Clifton Blvd", "Lakewood", "Birdtown", 2, 3, 2840, 96],
  ["Old Brooklyn Fourplex", "3467 Ridge Rd", "Cleveland", "Old Brooklyn", 4, 5, 5180, 92],
  ["Parma Ranch Portfolio", "7752 Day Dr", "Parma", "Snow Rd", 3, 4, 4360, 94],
  ["Strongsville Townhome", "11207 Pearl Rd", "Strongsville", "SouthPark", 6, 2, 3970, 98],
  ["West Park Triplex", "1842 West 105th St", "Cleveland", "West Park", 3, 1, 2490, 97],
  ["Ohio City Turnkey", "2810 Bridge Ave", "Cleveland", "Ohio City", 2, 2, 3140, 95],
  ["Shaker Heights Asset", "15301 Van Aken Blvd", "Shaker Heights", "Lomond", 4, 3, 4610, 94],
  ["Avon Lake Condo Row", "2860 Walker Rd", "Avon Lake", "Lake Erie", 5, 2, 3820, 99],
  ["North Olmsted SFR", "26887 Lorain Rd", "North Olmsted", "Great Northern", 1, 1, 1750, 93],
  ["Tremont Duplex", "2214 Professor Ave", "Cleveland", "Tremont", 2, 4, 2980, 91]
] as const;

const unitStatuses = ["occupied", "occupied", "occupied", "turnover", "vacant"] as const;

export const properties: Property[] = propertyBlueprints.map(([name, address, city, neighborhood, units, issues, spend, occupancy], index) => ({
  id: `p-${index + 1}`,
  ownerId: managers[index % managers.length].id,
  name,
  address,
  city,
  neighborhood,
  units,
  openIssues: issues,
  monthlyMaintenanceSpend: spend,
  occupancyRate: occupancy,
  manager: managers[index % managers.length].organization,
  unitsDetail: Array.from({ length: units }, (_, unitIndex) => ({
    id: `p-${index + 1}-u-${unitIndex + 1}`,
    label: `${unitIndex + 1}${unitIndex === 0 ? "A" : ""}`,
    status: unitStatuses[(index + unitIndex) % unitStatuses.length]
  }))
}));

const contractorSeed: Array<{
  name: string;
  businessName: string;
  trade: TradeCategory;
  areas: string[];
  range: [number, number];
  license: string;
  ins: string;
  emergency: boolean;
  response: number;
  reliability: number;
  jobs: number;
  repeat: number;
  licenseVerified: boolean;
  insuranceVerified: boolean;
  featured: boolean;
}> = [
  { name: "Andre Lewis", businessName: "Cleveland Pipe Rescue", trade: "Plumbing", areas: ["Cleveland", "Lakewood", "Parma"], range: [165, 620], license: "PL-77419", ins: "2026-02-18", emergency: true, response: 28, reliability: 94, jobs: 318, repeat: 9.4, licenseVerified: true, insuranceVerified: true, featured: true },
  { name: "Tina Morales", businessName: "Swift Current Electric", trade: "Electrical", areas: ["Cleveland", "Strongsville", "Westlake"], range: [180, 690], license: "EL-59108", ins: "2026-04-05", emergency: true, response: 34, reliability: 92, jobs: 276, repeat: 9.1, licenseVerified: true, insuranceVerified: true, featured: true },
  { name: "Caleb Porter", businessName: "Lakefront HVAC Co", trade: "HVAC", areas: ["Lakewood", "Avon Lake", "Cleveland"], range: [220, 850], license: "HV-45521", ins: "2026-01-30", emergency: true, response: 41, reliability: 91, jobs: 341, repeat: 9.2, licenseVerified: true, insuranceVerified: true, featured: true },
  { name: "Renee Holloway", businessName: "Peak Roof & Siding", trade: "Roofing", areas: ["Parma", "Strongsville", "North Olmsted"], range: [320, 1400], license: "RF-19384", ins: "2025-12-20", emergency: false, response: 58, reliability: 88, jobs: 218, repeat: 8.7, licenseVerified: true, insuranceVerified: true, featured: false },
  { name: "Marcus Bennett", businessName: "RentReady Handyman", trade: "General handyman", areas: ["Cleveland", "Tremont", "Ohio City"], range: [120, 460], license: "HD-71124", ins: "2026-05-14", emergency: true, response: 25, reliability: 90, jobs: 402, repeat: 8.9, licenseVerified: true, insuranceVerified: true, featured: true },
  { name: "Lena Walker", businessName: "Turnover Spark", trade: "Cleaning / turnover", areas: ["Lakewood", "Cleveland", "Shaker Heights"], range: [110, 540], license: "CL-30115", ins: "2026-03-07", emergency: false, response: 47, reliability: 89, jobs: 254, repeat: 8.8, licenseVerified: true, insuranceVerified: true, featured: false },
  { name: "Jamal Price", businessName: "North Coast Appliance", trade: "Appliance repair", areas: ["Parma", "Strongsville", "Westlake"], range: [145, 580], license: "AP-44012", ins: "2026-06-01", emergency: true, response: 52, reliability: 87, jobs: 189, repeat: 8.3, licenseVerified: true, insuranceVerified: false, featured: false },
  { name: "Marisol Vega", businessName: "Fresh Scope Inspections", trade: "Inspection", areas: ["Cleveland", "Lakewood", "Avon Lake"], range: [160, 640], license: "IN-22890", ins: "2026-07-10", emergency: false, response: 63, reliability: 93, jobs: 227, repeat: 9, licenseVerified: true, insuranceVerified: true, featured: true },
  { name: "Drew Foster", businessName: "Green Street Landscaping", trade: "Landscaping", areas: ["Strongsville", "North Olmsted", "Parma"], range: [130, 520], license: "LS-77230", ins: "2025-11-25", emergency: false, response: 55, reliability: 86, jobs: 167, repeat: 8.1, licenseVerified: false, insuranceVerified: true, featured: false },
  { name: "Nia Bennett", businessName: "Reliable Rotors HVAC", trade: "HVAC", areas: ["Cleveland", "Lakewood", "Tremont"], range: [210, 810], license: "HV-88211", ins: "2026-04-15", emergency: true, response: 39, reliability: 90, jobs: 294, repeat: 8.8, licenseVerified: true, insuranceVerified: true, featured: true },
  { name: "Owen Mitchell", businessName: "Gridline Electrical", trade: "Electrical", areas: ["Parma", "West Park", "Ohio City"], range: [175, 710], license: "EL-11844", ins: "2026-01-22", emergency: false, response: 44, reliability: 88, jobs: 210, repeat: 8.4, licenseVerified: true, insuranceVerified: true, featured: false },
  { name: "Kara Simmons", businessName: "TrueFix Plumbing", trade: "Plumbing", areas: ["Cleveland", "Shaker Heights", "Lakewood"], range: [160, 640], license: "PL-90021", ins: "2026-05-28", emergency: true, response: 32, reliability: 95, jobs: 363, repeat: 9.5, licenseVerified: true, insuranceVerified: true, featured: true },
  { name: "Dante Howard", businessName: "Blueprint Handyman", trade: "General handyman", areas: ["Avon Lake", "Westlake", "Strongsville"], range: [125, 470], license: "HD-22034", ins: "2026-02-06", emergency: false, response: 48, reliability: 84, jobs: 153, repeat: 8, licenseVerified: false, insuranceVerified: true, featured: false },
  { name: "Sana Patel", businessName: "Turnaround Turnovers", trade: "Cleaning / turnover", areas: ["Cleveland", "Parma", "Lakewood"], range: [105, 500], license: "CL-66350", ins: "2026-08-18", emergency: false, response: 36, reliability: 91, jobs: 261, repeat: 9.2, licenseVerified: true, insuranceVerified: true, featured: true },
  { name: "Tyler Brooks", businessName: "Metro Roof Response", trade: "Roofing", areas: ["Cleveland", "Strongsville", "Westlake"], range: [350, 1550], license: "RF-40412", ins: "2025-10-03", emergency: true, response: 66, reliability: 85, jobs: 172, repeat: 8.2, licenseVerified: true, insuranceVerified: true, featured: false },
  { name: "Megan Ellis", businessName: "Northstar Inspectors", trade: "Inspection", areas: ["Lakewood", "Parma", "Shaker Heights"], range: [140, 590], license: "IN-77188", ins: "2026-09-09", emergency: false, response: 57, reliability: 90, jobs: 205, repeat: 8.9, licenseVerified: true, insuranceVerified: true, featured: false },
  { name: "Isaiah Cole", businessName: "Summit Appliance Service", trade: "Appliance repair", areas: ["Cleveland", "Lakewood", "Westlake"], range: [150, 610], license: "AP-51510", ins: "2026-03-30", emergency: true, response: 45, reliability: 88, jobs: 233, repeat: 8.5, licenseVerified: true, insuranceVerified: true, featured: false },
  { name: "Paula Grant", businessName: "Dispatch Friendly Plumbing", trade: "Plumbing", areas: ["Parma", "Strongsville", "North Olmsted"], range: [155, 670], license: "PL-11309", ins: "2026-01-11", emergency: true, response: 29, reliability: 89, jobs: 247, repeat: 8.7, licenseVerified: true, insuranceVerified: false, featured: false },
  { name: "Noah Daniels", businessName: "Frontline Electrical", trade: "Electrical", areas: ["Lakewood", "Tremont", "Ohio City"], range: [170, 660], license: "EL-22019", ins: "2026-04-22", emergency: true, response: 31, reliability: 94, jobs: 305, repeat: 9.4, licenseVerified: true, insuranceVerified: true, featured: true },
  { name: "Erin Price", businessName: "RentSafe HVAC", trade: "HVAC", areas: ["Parma", "Cleveland", "Strongsville"], range: [205, 820], license: "HV-99011", ins: "2026-06-30", emergency: true, response: 38, reliability: 89, jobs: 276, repeat: 8.6, licenseVerified: true, insuranceVerified: true, featured: false }
];

export const contractors: Contractor[] = contractorSeed.map((item, index) => ({
  id: `c-${index + 1}`,
  name: item.name,
  businessName: item.businessName,
  trade: item.trade,
  serviceAreas: item.areas,
  estimateRange: item.range,
  licenseNumber: item.license,
  insuranceExpiration: item.ins,
  emergencyAvailability: item.emergency,
  responseTimeMinutes: item.response,
  reliabilityScore: item.reliability,
  completedJobs: item.jobs,
  repeatPropertyManagerRating: item.repeat,
  verifiedLicense: item.licenseVerified,
  verifiedInsurance: item.insuranceVerified,
  featured: item.featured,
  active: true
}));

const statuses: JobStatus[] = [
  "Draft",
  "Posted",
  "Quotes Requested",
  "Quotes Received",
  "Contractor Selected",
  "Scheduled",
  "In Progress",
  "Completed",
  "Reviewed",
  "Disputed"
];

const jobBlueprints = [
  ["Water heater leaking in basement", 1, "Basement", "Plumbing", "Emergency", true, 180, 720, 140, 750, "Water stains near unit 1A utility wall. Shutoff valve accessible behind shelving.", "Use side door code 4137 and text on arrival.", 4, 3, 180],
  ["Two outlets not powering bedroom", 2, "2B", "Electrical", "Within 24 hours", false, 150, 540, 130, 620, "Likely breaker or worn receptacle. Tenant reports intermittent flicker.", "Call tenant 30 minutes ahead. Parking behind building.", 3, 2, 120],
  ["No heat in third-floor unit", 3, "3C", "HVAC", "Emergency", true, 240, 900, 180, 980, "Furnace cycles but does not sustain heat. Filters replaced last week.", "Lockbox by rear entry. Maintenance manager on-call.", 5, 1, 35],
  ["Roof leak over hallway", 4, "Attic / hallway", "Roofing", "Within 24 hours", false, 320, 1300, 250, 1450, "Leak appears after heavy rain. Possible flashing failure around chimney.", "Roof access through attic hatch. Photos attached.", 2, 2, 210],
  ["Drywall repair after turnover", 5, "Unit 2", "General handyman", "This week", false, 120, 420, 110, 480, "Small nail pops and anchor holes from wall mounts. Needs paint ready finish.", "Key in combo lockbox. Work window 10am-4pm.", 2, 4, 60],
  ["Inspection for new acquisition", 6, "Whole property", "Inspection", "This week", false, 160, 640, 130, 690, "Pre-offer inspection and safety checklist requested by investor group.", "Meet buyer at front door. No tenant access needed.", 1, 3, 90],
  ["Dishwasher not draining", 7, "Unit 4A", "Appliance repair", "Within 24 hours", false, 140, 580, 120, 640, "Standing water after every cycle. Filter already cleaned.", "Tenant home after 6pm only.", 2, 2, 45],
  ["Spring landscaping cleanup", 8, "Front yard and curb strip", "Landscaping", "Flexible", false, 130, 520, 100, 560, "Leaf cleanup, edging, and beds reset before listing photos.", "Can access any weekday after 8am.", 0, 1, 70],
  ["Deep clean after move-out", 9, "Unit 1B", "Cleaning / turnover", "This week", false, 115, 500, 100, 540, "Turnover clean plus fridge, oven, baseboards, and cabinets.", "Vacant unit. Supra box on railing.", 1, 5, 55],
  ["GFCI outlets tripping repeatedly", 10, "Kitchen", "Electrical", "Emergency", true, 160, 620, 140, 700, "Likely moisture or overloaded circuit. Tenant lost refrigerator power.", "Please call before entering. Dog in unit.", 6, 1, 25],
  ["Kitchen sink drain clog", 1, "Kitchen", "Plumbing", "This week", false, 130, 480, 115, 525, "Slow drain in both sink bowls. Tenant used enzyme treatment with no change.", "Back alley access preferred.", 2, 2, 150],
  ["Lockset replacement and rekey", 2, "Front entry", "General handyman", "Flexible", false, 95, 260, 85, 300, "Tenant moved out, wants same-day access control reset.", "Call property manager on arrival.", 0, 2, 30],
  ["Boiler annual check", 3, "Mechanical room", "HVAC", "This week", false, 210, 740, 190, 790, "Preventive maintenance for heating system before winter.", "Mechanical key on site. No tenant impact.", 0, 2, 95],
  ["Garage door sensor issue", 4, "Garage", "General handyman", "Within 24 hours", false, 110, 390, 100, 420, "Door reverses midway. Sensors may need alignment.", "Use side gate. Manager on site until noon.", 1, 2, 40],
  ["Emergency cleanup after burst pipe", 5, "Basement", "Cleaning / turnover", "Emergency", true, 260, 1100, 220, 1200, "Water extraction, sanitize, and prepare for mitigation vendor.", "Gas and water already shut off. Rush response required.", 9, 0, 10]
] as const;

export const jobs: MaintenanceJob[] = jobBlueprints.map(([title, propertyIndex, unit, tradeCategory, urgency, emergency, estimateMin, estimateMax, budgetMin, budgetMax, description, accessInstructions, quotesCount, messages, responseTimeMinutes], index) => ({
  id: `job-${String(index + 1).padStart(3, "0")}`,
  title,
  propertyId: properties[propertyIndex - 1].id,
  unit,
  tradeCategory,
  urgency,
  status: statuses[index % statuses.length],
  quotesCount,
  estimateMin,
  estimateMax,
  assignedContractorId: index % 3 === 0 ? contractors[(index % contractors.length)].id : index % 4 === 0 ? contractors[(index + 4) % contractors.length].id : null,
  description,
  accessInstructions,
  budgetMin,
  budgetMax,
  createdAt: `2026-05-${String(10 - (index % 7)).padStart(2, "0")}T10:30:00Z`,
  responseTimeMinutes,
  messages,
  emergency
}));

export const quotes: Quote[] = jobs.flatMap((job, index) => {
  const baseContractors = contractors.slice(index % 4, index % 4 + 3);
  const priceAnchor = (job.estimateMin + job.estimateMax) / 2;
  return baseContractors.map((contractor, qIndex) => ({
    id: `q-${index + 1}-${qIndex + 1}`,
    jobId: job.id,
    contractorId: contractor.id,
    price: Math.round(priceAnchor * (0.88 + qIndex * 0.11) + (index % 3) * 25),
    timelineDays: qIndex === 0 ? "Same day" : qIndex === 1 ? "1-2 days" : "2-4 days",
    warranty: qIndex === 0 ? "90 days labor" : qIndex === 1 ? "1 year labor" : "30 days labor",
    materialsIncluded: qIndex !== 2,
    notes: qIndex === 0 ? "Fastest dispatch, slightly higher rate." : qIndex === 1 ? "Balanced schedule and pricing." : "Lower bid with slower availability.",
    responseMinutes: contractor.responseTimeMinutes + qIndex * 20,
    completionRate: contractor.reliabilityScore - qIndex * 2
  }));
}).slice(0, 30);

export const reviews: Review[] = Array.from({ length: 20 }, (_, index) => {
  const contractor = contractors[index % contractors.length];
  const job = jobs[(index + 2) % jobs.length];
  return {
    id: `r-${index + 1}`,
    jobId: job.id,
    contractorId: contractor.id,
    reviewer: managers[index % managers.length].organization,
    date: `2026-04-${String(28 - index).padStart(2, "0")}T12:00:00Z`,
    showedUpOnTime: 4 + (index % 2),
    priceMatchedQuote: 4 + (index % 2),
    qualityOfWork: 4 + ((index + 1) % 2),
    communication: 4 + (index % 2),
    wouldHireAgain: index % 5 !== 0,
    note: index % 3 === 0 ? "Clear updates, tidy closeout, and no surprises on invoice." : "Good turnaround and comfortable tenant communication." 
  };
});

export const messages: Message[] = Array.from({ length: 12 }, (_, index) => ({
  id: `m-${index + 1}`,
  jobId: jobs[index % jobs.length].id,
  from: index % 2 === 0 ? "Property manager" : "Vendor",
  body:
    index % 2 === 0
      ? "Can you confirm availability and send a window for arrival?"
      : "We can be there within the posted window and will text 20 minutes before arrival.",
  createdAt: `2026-05-09T0${index % 9}:15:00Z`
}));

export const verificationQueue: VerificationItem[] = contractors.slice(0, 10).map((contractor, index) => ({
  contractorId: contractor.id,
  licenseVerified: contractor.verifiedLicense,
  insuranceVerified: contractor.verifiedInsurance,
  riskLevel: index % 4 === 0 ? "Medium" : index % 5 === 0 ? "High" : "Low",
  featured: contractor.featured
}));

export const invoices: Invoice[] = [
  { id: "inv-1", description: "Landlord Pro subscription", amount: 49, status: "paid", createdAt: "2026-05-01T00:00:00Z" },
  { id: "inv-2", description: "Property Manager plan", amount: 199, status: "pending", createdAt: "2026-05-08T00:00:00Z" },
  { id: "inv-3", description: "Completed-job success fee", amount: 128, status: "paid", createdAt: "2026-05-08T00:00:00Z" }
];

export const subscriptionPlans: SubscriptionPlan[] = [
  {
    name: "Starter Landlord",
    audience: "For owners with one property",
    price: "Free",
    summary: "Basic contractor search, simple posting, and demo-ready maintenance visibility.",
    features: ["1 property", "Limited job posts", "Basic contractor search", "Email support"]
  },
  {
    name: "Landlord Pro",
    audience: "For active small landlords",
    price: "$49/month",
    summary: "Unlimited maintenance posts, quote comparison, and preferred vendors for up to 10 properties.",
    features: ["Up to 10 properties", "Unlimited jobs", "Quote comparison", "Preferred vendor list", "Maintenance spend tracking"]
  },
  {
    name: "Property Manager",
    audience: "For small teams and operators",
    price: "$199/month",
    summary: "Unlimited properties, team workflow, vendor management, and priority matching.",
    features: ["Unlimited properties", "Team access", "Vendor management", "Reporting", "Priority matching"],
    featured: true
  },
  {
    name: "Contractor Pro",
    audience: "For vendors who want recurring property work",
    price: "$39/month",
    summary: "Verified profile, priority alerts, quote tools, and reliability tracking.",
    features: ["Verified profile", "Priority alerts", "Quote tools", "Reliability dashboard", "Repeat PM visibility"]
  }
];

export const statusFlow: JobStatus[] = [
  "Draft",
  "Posted",
  "Quotes Requested",
  "Quotes Received",
  "Contractor Selected",
  "Scheduled",
  "In Progress",
  "Completed",
  "Reviewed",
  "Disputed"
];

export const performanceBenchmarks = {
  averageResponseMinutes: 47,
  averageQuoteSpread: 18,
  averageSavings: 236,
  emergencyFillRate: 91
};

export const marketSignals = [
  { label: "Lead spam reduced", value: "79%" },
  { label: "Repeat vendor rate", value: "62%" },
  { label: "Quote response window", value: "42 min" },
  { label: "Emergency fill rate", value: "91%" }
];
