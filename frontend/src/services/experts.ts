import http from "../apis/http";
import type { ListParams, Page } from "../types/pagination";
import type { Expert, ExpertCreate, ExpertUpdate } from "../types/domain";

export interface ExpertListParams extends ListParams {
  organization_id?: number;
  region_id?: number;
  title_id?: number;
  specialty_id?: number;
  is_active?: boolean;
  gender?: string;
}

export async function listExperts(params: ExpertListParams) {
  const { data } = await http.get<Page<Expert>>("/experts", { params });
  return data;
}

export async function listExpertsAll() {
  const { data } = await http.get<Expert[]>("/experts/all");
  return data;
}

export async function getExpert(expertId: number) {
  const { data } = await http.get<Expert>(`/experts/${expertId}`);
  return data;
}

export async function createExpert(payload: ExpertCreate) {
  const { data } = await http.post<Expert>("/experts", payload);
  return data;
}

export async function updateExpert(expertId: number, payload: ExpertUpdate) {
  const { data } = await http.put<Expert>(`/experts/${expertId}`, payload);
  return data;
}

export async function deleteExpert(expertId: number) {
  await http.delete(`/experts/${expertId}`);
}

export async function deleteExperts(ids: number[]) {
  const { data } = await http.post("/experts/batch-delete", { ids });
  return data as { deleted: number; skipped: number };
}

export async function importExperts(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await http.post("/experts/import", formData);
  return data as { created: number; skipped: number };
}

export async function exportExperts() {
  const response = await http.get<Blob>("/experts/export", {
    responseType: "blob",
  });
  return response.data;
}
