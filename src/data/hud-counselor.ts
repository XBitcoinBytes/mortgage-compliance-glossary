/** Official HUD housing-counselor finder (consumer short URL).
 *  https://www.hud.gov/findacounselor meta-refreshes to
 *  https://answers.hud.gov/housingcounseling/ (HUD's live locator).
 *  HUD still publishes the short URL on hud.gov/helping-americans and in
 *  consumer materials. Toll-free locator assistance: 800-569-4287.
 */
export const HUD_COUNSELOR_URL = "https://www.hud.gov/findacounselor";

/** Servicing, loss-mitigation, and foreclosure terms that should carry a
 *  short, neutral pointer to free HUD-approved counseling. Not every
 *  servicing entry (escrow, PMI, transfers) is included.
 */
export const HUD_COUNSELOR_SLUGS = [
  "acceleration",
  "continuity-of-contact",
  "deed-in-lieu",
  "delinquency",
  "delinquency-foreclosure-wait",
  "dual-tracking",
  "early-intervention",
  "faq-what-if-i-cannot-pay",
  "faq-what-is-forbearance",
  "forbearance",
  "foreclosure",
  "loan-modification",
  "loss-mitigation",
  "loss-mitigation-appeal",
  "loss-mitigation-application",
  "partial-claim",
  "payment-deferral",
  "reinstatement",
  "repayment-plan",
  "short-sale",
] as const;

const SLUG_SET = new Set<string>(HUD_COUNSELOR_SLUGS);

export function hasHudCounselor(slug: string): boolean {
  return SLUG_SET.has(slug);
}
