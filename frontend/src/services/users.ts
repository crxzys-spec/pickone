import http from "../apis/http";
import type {
  User,
  UserCreate,
  UserPasswordChange,
  UserProfileUpdate,
  UserRolesUpdate,
  UserUpdate,
} from "../types/rbac";

export async function listUsers() {
  const { data } = await http.get<User[]>("/users");
  return data;
}

export async function getMe() {
  const { data } = await http.get<User>("/users/me");
  return data;
}

export async function updateMe(payload: UserProfileUpdate) {
  const { data } = await http.put<User>("/users/me", payload);
  return data;
}

export async function changePassword(payload: UserPasswordChange) {
  await http.post("/users/me/password", payload);
}

export async function getUser(userId: number) {
  const { data } = await http.get<User>(`/users/${userId}`);
  return data;
}

export async function createUser(payload: UserCreate) {
  const { data } = await http.post<User>("/users", payload);
  return data;
}

export async function updateUser(userId: number, payload: UserUpdate) {
  const { data } = await http.put<User>(`/users/${userId}`, payload);
  return data;
}

export async function deleteUser(userId: number) {
  await http.delete(`/users/${userId}`);
}

export async function assignUserRoles(userId: number, payload: UserRolesUpdate) {
  const { data } = await http.put<User>(`/users/${userId}/roles`, payload);
  return data;
}
