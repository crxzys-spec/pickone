import http from "../apis/http";
import type { ListParams, Page } from "../types/pagination";
import type { Title, TitleCreate, TitleUpdate } from "../types/domain";

export type TitleBatchAction = "enable" | "disable" | "delete";

export interface TitleBatchItem {
  id: number;
}

export async function listTitles(params: ListParams) {
  const { data } = await http.get<Page<Title>>("/titles", { params });
  return data;
}

export async function listTitleTree() {
  const { data } = await http.get<Title[]>("/titles/tree");
  return data;
}

export async function listTitlesAll() {
  const { data } = await http.get<Title[]>("/titles/all");
  return data;
}

export async function createTitle(payload: TitleCreate) {
  const { data } = await http.post<Title>("/titles", payload);
  return data;
}

export async function updateTitle(titleId: number, payload: TitleUpdate) {
  const { data } = await http.put<Title>(`/titles/${titleId}`, payload);
  return data;
}

export async function deleteTitle(titleId: number) {
  await http.delete(`/titles/${titleId}`);
}

export async function batchTitles(
  action: TitleBatchAction,
  items: TitleBatchItem[],
) {
  const { data } = await http.post("/titles/batch", { action, items });
  return data as {
    updated: number;
    deleted: number;
    skipped: number;
    errors?: { id: number; detail: string }[];
  };
}
