/** Utility to convert department / municipality names to URL-safe slugs */

export function toSlug(s: string): string {
  return s
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9-]/g, "");
}

export const DEPARTMENTS = [
  "Ahuachapán",
  "Cabañas",
  "Chalatenango",
  "Cuscatlán",
  "La Libertad",
  "La Paz",
  "La Unión",
  "Morazán",
  "San Miguel",
  "San Salvador",
  "San Vicente",
  "Santa Ana",
  "Sonsonate",
  "Usulután",
] as const;

export type Department = (typeof DEPARTMENTS)[number];

/** Resolve a URL slug back to a department name */
export function departmentFromSlug(slug: string): string | undefined {
  return DEPARTMENTS.find((d) => toSlug(d) === slug);
}
