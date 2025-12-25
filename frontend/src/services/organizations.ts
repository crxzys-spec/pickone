import http from "../apis/http";
import type {
  Organization,
  OrganizationCreate,
  OrganizationUpdate,
} from "../types/domain";

export async function listOrganizations() {
  const { data } = await http.get<Organization[]>("/organizations");
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
