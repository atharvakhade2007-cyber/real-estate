/** Indian digit grouping: 14500000 -> "1,45,00,000" */
export function groupIN(value) {
  const n = Math.round(Number(value) || 0);
  const sign = n < 0 ? "-" : "";
  const digits = Math.abs(n).toString();
  if (digits.length <= 3) return sign + digits;
  const head = digits.slice(0, -3);
  const tail = digits.slice(-3);
  const groups = [];
  let rest = head;
  while (rest.length > 2) {
    groups.unshift(rest.slice(-2));
    rest = rest.slice(0, -2);
  }
  if (rest) groups.unshift(rest);
  return `${sign}${[...groups, tail].join(",")}`;
}

/** Compact Indian currency: ₹1.45 Cr / ₹85.5 Lakhs / ₹1,25,000 */
export function formatINR(value) {
  const v = Number(value) || 0;
  if (v >= 1e7) return `₹${(v / 1e7).toFixed(2)} Cr`;
  if (v >= 1e5) return `₹${(v / 1e5).toFixed(1)} Lakhs`;
  return `₹${groupIN(v)}`;
}

/** Full-format currency: ₹1,45,00,000 */
export function formatINRFull(value) {
  return `₹${groupIN(value)}`;
}

/** Standard reducing-balance EMI. */
export function calcEmi(principal, annualRatePct, years) {
  const r = annualRatePct / 12 / 100;
  const n = years * 12;
  if (n <= 0) return 0;
  if (r === 0) return principal / n;
  return (principal * r * (1 + r) ** n) / ((1 + r) ** n - 1);
}

export const FURNISHING_LABELS = {
  unfurnished: "Unfurnished",
  semi_furnished: "Semi-Furnished",
  fully_furnished: "Fully-Furnished",
};
