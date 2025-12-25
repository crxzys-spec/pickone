import http from "../apis/http";
import type { Role, RoleCreate, RolePermissionsUpdate, RoleUpdate } from "../types/rbac";

export async function listRoles() {
  const { data } = await http.get<Role[]>("/roles");
  return data;
}

export async function getRole(roleId: number) {
  const { data } = await http.get<Role>(`/roles/${roleId}`);
  return data;
}

export async function createRole(payload: RoleCreate) {
  const { data } = await http.post<Role>("/roles", payload);
  return data;
}

export async function updateRole(roleId: number, payload: RoleUpdate) {
  const { data } = await http.put<Role>(`/roles/${roleId}`, payload);
  return data;
}

export async function deleteRole(roleId: number) {
  await http.delete(`/roles/${roleId}`);
}

export async function assignRolePermissions(
  roleId: number,
  payload: RolePermissionsUpdate,
) {
  const { data } = await http.put<Role>(`/roles/${roleId}/permissions`, payload);
  return data;
}
