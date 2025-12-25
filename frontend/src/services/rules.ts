import http from "../apis/http";
import type { Rule, RuleCreate, RuleUpdate } from "../types/domain";

export async function listRules() {
  const { data } = await http.get<Rule[]>("/rules");
  return data;
}

export async function getRule(ruleId: number) {
  const { data } = await http.get<Rule>(`/rules/${ruleId}`);
  return data;
}

export async function createRule(payload: RuleCreate) {
  const { data } = await http.post<Rule>("/rules", payload);
  return data;
}

export async function updateRule(ruleId: number, payload: RuleUpdate) {
  const { data } = await http.put<Rule>(`/rules/${ruleId}`, payload);
  return data;
}

export async function deleteRule(ruleId: number) {
  await http.delete(`/rules/${ruleId}`);
}
