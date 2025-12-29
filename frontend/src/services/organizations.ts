import http from "../apis/http";
import type { ListParams, Page } from "../types/pagination";
import type {
  Organization,
  OrganizationCreate,
  OrganizationUpdate,
} from "../types/domain";

export async function listOrganizations(params: ListParams) {
  const { data } = await http.get<Page<Organization>>("/organizations", { params });
  return data;
}

export async function listOrganizationsAll() {
  const { data } = await http.get<Organization[]>("/organizations/all");
  return data;
}

export async function createOrganization(payload: OrganizationCreate) {
  const { data } = await http.post<Organization>("/organizations", payload);
  return data;
}

export async function updateOrganization(
  organizationId: number,
  payload: OrganizationUpdate,
) {
  const { data } = await http.put<Organization>(
    `/organizations/${organizationId}`,
    payload,
  );
  return data;
}

export async function deleteOrganization(organizationId: number) {
  await http.delete(`/organizations/${organizationId}`);
}

export async function deleteOrganizations(ids: number[]) {
  const { data } = await http.post("/organizations/batch-delete", { ids });
  return data as { deleted: number; skipped: number };
}
