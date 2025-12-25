import http from "../apis/http";
import type {
  DrawApplication,
  DrawApply,
  DrawResultOut,
  DrawUpdate,
} from "../types/domain";

export async function listDraws() {
  const { data } = await http.get<DrawApplication[]>("/draws");
  return data;
}

export async function getDraw(drawId: number) {
  const { data } = await http.get<DrawApplication>(`/draws/${drawId}`);
  return data;
}

export async function createDraw(payload: DrawApply) {
  const { data } = await http.post<DrawApplication>("/draws/apply", payload);
  return data;
}

export async function updateDraw(drawId: number, payload: DrawUpdate) {
  const { data } = await http.put<DrawApplication>(`/draws/${drawId}`, payload);
  return data;
}

export async function deleteDraw(drawId: number) {
  await http.delete(`/draws/${drawId}`);
}

export async function executeDraw(drawId: number) {
  const { data } = await http.post<DrawResultOut[]>(`/draws/${drawId}/execute`);
  return data;
}

export async function listDrawResults(drawId: number) {
  const { data } = await http.get<DrawResultOut[]>(`/draws/${drawId}/results`);
  return data;
}

export async function replaceDrawResult(drawId: number, resultId: number) {
  const { data } = await http.post<DrawResultOut[]>(
    `/draws/${drawId}/replace`,
    { result_id: resultId },
  );
  return data;
}
