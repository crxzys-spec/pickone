import http from "../apis/http";
import type { Title, TitleCreate, TitleUpdate } from "../types/domain";

export async function listTitles() {
  const { data } = await http.get<Title[]>("/titles");
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
