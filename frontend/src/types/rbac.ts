export interface RoleSummary {
  id: number;
  name: string;
}

export interface Permission {
  id: number;
  name: string;
  scope: string;
  description?: string | null;
}

export interface Role {
  id: number;
  name: string;
  description?: string | null;
  permissions?: Permission[];
}

export interface User {
  id: number;
  username: string;
  full_name?: string | null;
  email?: string | null;
  is_active: boolean;
  is_superuser: boolean;
  roles: RoleSummary[];
}

export interface UserCreate {
  username: string;
  full_name?: string | null;
  email?: string | null;
  password: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface UserUpdate {
  username?: string | null;
  full_name?: string | null;
  email?: string | null;
  is_active?: boolean | null;
  is_superuser?: boolean | null;
  password?: string | null;
}

export interface UserProfileUpdate {
  full_name?: string | null;
  email?: string | null;
}

export interface UserPasswordChange {
  current_password: string;
  new_password: string;
}

export interface UserRolesUpdate {
  role_ids: number[];
}

export interface RoleCreate {
  name: string;
  description?: string | null;
}

export interface RoleUpdate {
  name?: string | null;
  description?: string | null;
}

export interface RolePermissionsUpdate {
  permission_ids: number[];
}

export interface PermissionCreate {
  name: string;
  scope: string;
  description?: string | null;
}

export interface PermissionUpdate {
  name?: string | null;
  scope?: string | null;
  description?: string | null;
}
