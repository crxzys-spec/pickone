import http from "../apis/http";
import type { ListParams, Page } from "../types/pagination";
import type {
  Permission,
  PermissionCreate,
  PermissionUpdate,
} from "../types/rbac";

export async function listPermissions(params: ListParams) {
  const { data } = await http.get<Page<Permission>>("/permissions", { params });
  return data;
}

export async function listPermissionsAll() {
  const { data } = await http.get<Permission[]>("/permissions/all");
  return data;
}

export async function getPermission(permissionId: number) {
  const { data } = await http.get<Permission>(`/permissions/${permissionId}`);
  return data;
}

export async function createPermission(payload: PermissionCreate) {
  const { data } = await http.post<Permission>("/permissions", payload);
  return data;
}

export async function updatePermission(
  permissionId: number,
  payload: PermissionUpdate,
) {
  const { data } = await http.put<Permission>(
    `/permissions/${permissionId}`,
    payload,
  );
  return data;
}

export async function deletePermission(permissionId: number) {
  await http.delete(`/permissions/${permissionId}`);
}
