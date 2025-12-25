export function hasScopes(scopes: string[], required: string[]): boolean {
  if (scopes.includes("*")) {
    return true;
  }
  return required.every((scope) => scopes.includes(scope));
}
