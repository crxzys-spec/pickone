import http from "../apis/http";
import type {
  Category,
  ExpertPublicCreate,
  Organization,
  Region,
  Title,
} from "../types/domain";

export interface ExpertPublicMetadata {
  organizations: Organization[];
  regions: Region[];
  titles: Title[];
  specialties: Category[];
}

export async function fetchExpertPublicMetadata() {
  const { data } = await http.get<ExpertPublicMetadata>("/public/experts/metadata");
  return data;
}

export async function submitExpertPublicRegistration(payload: ExpertPublicCreate) {
  const { data } = await http.post<{ id: number; audit_status: string }>(
    "/public/experts/register",
    payload,
  );
  return data;
}
