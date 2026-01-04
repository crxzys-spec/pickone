import http from "../apis/http";
import type { ListParams, Page } from "../types/pagination";
import type {
  DrawApplication,
  DrawApply,
  DrawResultContact,
  DrawResultContactUpdate,
  DrawResultOut,
  DrawUpdate,
} from "../types/domain";

export async function listDraws(params: ListParams) {
  const { data } = await http.get<Page<DrawApplication>>("/draws", { params });
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

export async function deleteDraws(ids: number[]) {
  const { data } = await http.post<{ deleted: number; skipped: number }>(
    "/draws/batch-delete",
    { ids },
  );
  return data;
}

export async function executeDraw(drawId: number) {
  const { data } = await http.post<DrawResultOut[]>(`/draws/${drawId}/execute`);
  return data;
}

export async function listDrawResults(drawId: number, params: ListParams) {
  const { data } = await http.get<Page<DrawResultOut>>(
    `/draws/${drawId}/results`,
    { params },
  );
  return data;
}

export async function replaceDrawResult(drawId: number, resultId: number) {
  const { data } = await http.post<DrawResultOut[]>(
    `/draws/${drawId}/replace`,
    { result_id: resultId },
  );
  return data;
}

export async function getDrawResultContact(drawId: number, resultId: number) {
  const { data } = await http.get<DrawResultContact>(
    `/draws/${drawId}/results/${resultId}/contact`,
  );
  return data;
}

export async function updateDrawResultContact(
  drawId: number,
  resultId: number,
  payload: DrawResultContactUpdate,
) {
  const { data } = await http.put<DrawResultOut[]>(
    `/draws/${drawId}/results/${resultId}/contact`,
    payload,
  );
  return data;
}

export async function exportDrawResults(drawId: number) {
  const response = await http.get<Blob>(`/draws/${drawId}/export`, {
    responseType: "blob",
  });
  return response.data;
}

export async function exportDrawSignin(drawId: number) {
  const response = await http.get<Blob>(`/draws/${drawId}/export-signin`, {
    responseType: "blob",
  });
  return response.data;
}
