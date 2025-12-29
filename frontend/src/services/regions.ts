import http from "../apis/http";
import type { ListParams, Page } from "../types/pagination";
import type { Region, RegionCreate, RegionUpdate } from "../types/domain";

export async function listRegions(params: ListParams) {
  const { data } = await http.get<Page<Region>>("/regions", { params });
  return data;
}

export async function listRegionsAll() {
  const { data } = await http.get<Region[]>("/regions/all");
  return data;
}

export async function createRegion(payload: RegionCreate) {
  const { data } = await http.post<Region>("/regions", payload);
  return data;
}

export async function updateRegion(regionId: number, payload: RegionUpdate) {
  const { data } = await http.put<Region>(`/regions/${regionId}`, payload);
  return data;
}

export async function deleteRegion(regionId: number) {
  await http.delete(`/regions/${regionId}`);
}

export async function deleteRegions(ids: number[]) {
  const { data } = await http.post("/regions/batch-delete", { ids });
  return data as { deleted: number; skipped: number };
}
