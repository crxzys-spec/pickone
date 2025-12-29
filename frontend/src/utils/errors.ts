type ErrorDetail =
  | string
  | { message?: unknown; error?: unknown; detail?: unknown }
  | Array<{ msg?: unknown }>;

export type ErrorDetailTranslator = (detail: string) => string | null;

function extractDetail(detail: unknown): string | null {
  if (typeof detail === "string" && detail.trim()) {
    return detail.trim();
  }
  if (Array.isArray(detail) && detail.length > 0) {
    const message = (detail[0] as { msg?: unknown })?.msg;
    if (typeof message === "string" && message.trim()) {
      return message.trim();
    }
  }
  if (detail && typeof detail === "object") {
    const message = (detail as { message?: unknown; error?: unknown }).message;
    if (typeof message === "string" && message.trim()) {
      return message.trim();
    }
    const error = (detail as { error?: unknown }).error;
    if (typeof error === "string" && error.trim()) {
      return error.trim();
    }
  }
  return null;
}

export function resolveErrorMessage(
  error: unknown,
  fallback: string,
  translateDetail?: ErrorDetailTranslator,
): string {
  const responseData = (error as { response?: { data?: unknown } })?.response?.data;
  if (typeof responseData === "string" && responseData.trim()) {
    const translated = translateDetail?.(responseData.trim());
    return `${fallback}: ${translated ?? responseData.trim()}`;
  }
  if (responseData && typeof responseData === "object") {
    const detail = (responseData as { detail?: ErrorDetail }).detail;
    const detailMessage = extractDetail(detail);
    if (detailMessage) {
      const translated = translateDetail?.(detailMessage);
      return `${fallback}: ${translated ?? detailMessage}`;
    }
    const message = extractDetail(responseData);
    if (message) {
      const translated = translateDetail?.(message);
      return `${fallback}: ${translated ?? message}`;
    }
  }
  const errorMessage = (error as { message?: unknown })?.message;
  if (typeof errorMessage === "string" && errorMessage.trim()) {
    return `${fallback}: ${errorMessage.trim()}`;
  }
  return fallback;
}
