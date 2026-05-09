import type { Contractor, Quote } from "@/lib/types";
import { formatCurrency } from "@/lib/format";

const clamp = (value: number, min = 0, max = 100) => Math.min(max, Math.max(min, value));

export function calculateBestValueScore(contractor: Contractor, quote?: Quote, budgetMax?: number) {
  const reliability = contractor.reliabilityScore;
  const price = quote
    ? clamp(
        100 - ((quote.price - (budgetMax ?? quote.price)) / Math.max(budgetMax ?? quote.price, 1)) * 100 + 18
      )
    : clamp(88 - (contractor.estimateRange[1] / 1000) * 6);
  const response = clamp(100 - contractor.responseTimeMinutes * 1.35);
  const proximity = contractor.serviceAreas.some((area) => area.includes("Cleveland") || area.includes("Lakewood"))
    ? 92
    : 78;
  const verification = (contractor.verifiedLicense ? 50 : 0) + (contractor.verifiedInsurance ? 50 : 0);
  const repeat = clamp(contractor.repeatPropertyManagerRating * 10);

  return Math.round(
    reliability * 0.3 + price * 0.2 + response * 0.2 + proximity * 0.15 + verification * 0.1 + repeat * 0.05
  );
}

export function estimateSanityNotes(price: number, expectedMin: number, expectedMax: number, responseMinutes: number) {
  const notes: string[] = [];

  if (price < expectedMin * 0.85) {
    notes.push("This quote appears lower than average for similar jobs in this market.");
  } else if (price > expectedMax * 1.15) {
    notes.push("This quote is above the typical range for this type of maintenance work.");
  } else {
    notes.push("This quote falls within the expected range for similar jobs.");
  }

  if (responseMinutes > 180) {
    notes.push("This contractor may be slower to respond during urgent dispatch windows.");
  } else {
    notes.push("Response timing looks acceptable for property-manager workflows.");
  }

  notes.push("Best value recommendation: choose the contractor with the strongest reliability and quote accuracy balance.");

  return notes;
}

export function quoteAccuracyScore(quote: Quote, actualPrice: number) {
  const delta = Math.abs(actualPrice - quote.price);
  const score = clamp(100 - (delta / Math.max(actualPrice, 1)) * 100);
  return Math.round(score);
}

export function summarizeSavings(expectedMax: number, acceptedPrice: number) {
  return formatCurrency(Math.max(0, expectedMax - acceptedPrice));
}
