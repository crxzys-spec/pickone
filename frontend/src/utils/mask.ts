export function maskPhone(value?: string | null): string {
  const raw = String(value ?? "").trim();
  if (!raw) {
    return "";
  }
  if (raw.length <= 7) {
    return raw;
  }
  return `${raw.slice(0, 3)}${"*".repeat(raw.length - 7)}${raw.slice(-4)}`;
}

export function maskIdCard(value?: string | null): string {
  const raw = String(value ?? "").trim();
  if (!raw) {
    return "";
  }
  if (raw.length <= 7) {
    return raw;
  }
  return `${raw.slice(0, 3)}${"*".repeat(raw.length - 7)}${raw.slice(-4)}`;
}

export function maskName(value?: string | null): string {
  const raw = String(value ?? "").trim();
  if (!raw) {
    return "";
  }
  if (raw.length === 1) {
    return raw;
  }
  if (raw.length === 2) {
    return `${raw[0]}*`;
  }
  return `${raw[0]}${"*".repeat(raw.length - 2)}${raw[raw.length - 1]}`;
}
