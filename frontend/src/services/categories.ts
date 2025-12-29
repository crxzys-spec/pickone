import http from "../apis/http";
import type { ListParams, Page } from "../types/pagination";
import type {
  Category,
  CategoryCreate,
  CategoryTree,
  CategoryUpdate,
  Specialty,
  SpecialtyCreate,
  SpecialtyUpdate,
  Subcategory,
  SubcategoryCreate,
  SubcategoryUpdate,
} from "../types/domain";

export type CategoryNodeType = "category" | "subcategory" | "specialty";
export type CategoryBatchAction = "enable" | "disable" | "delete";

export interface CategoryBatchItem {
  id: number;
  type: CategoryNodeType;
}

export async function listCategories(params: ListParams) {
  const { data } = await http.get<Page<Category>>("/categories", { params });
  return data;
}

export async function listCategoryTree() {
  const { data } = await http.get<CategoryTree[]>("/categories/tree");
  return data;
}

export async function createCategory(payload: CategoryCreate) {
  const { data } = await http.post<Category>("/categories", payload);
  return data;
}

export async function updateCategory(categoryId: number, payload: CategoryUpdate) {
  const { data } = await http.put<Category>(`/categories/${categoryId}`, payload);
  return data;
}

export async function deleteCategory(categoryId: number) {
  await http.delete(`/categories/${categoryId}`);
}

export async function listSubcategories(categoryId: number, params: ListParams) {
  const { data } = await http.get<Page<Subcategory>>(
    `/categories/${categoryId}/subcategories`,
    { params },
  );
  return data;
}

export async function createSubcategory(
  categoryId: number,
  payload: SubcategoryCreate,
) {
  const { data } = await http.post<Subcategory>(
    `/categories/${categoryId}/subcategories`,
    payload,
  );
  return data;
}

export async function updateSubcategory(
  subcategoryId: number,
  payload: SubcategoryUpdate,
) {
  const { data } = await http.put<Subcategory>(
    `/categories/subcategories/${subcategoryId}`,
    payload,
  );
  return data;
}

export async function deleteSubcategory(subcategoryId: number) {
  await http.delete(`/categories/subcategories/${subcategoryId}`);
}

export async function listSpecialties(subcategoryId: number, params: ListParams) {
  const { data } = await http.get<Page<Specialty>>(
    `/categories/subcategories/${subcategoryId}/specialties`,
    { params },
  );
  return data;
}

export async function createSpecialty(
  subcategoryId: number,
  payload: SpecialtyCreate,
) {
  const { data } = await http.post<Specialty>(
    `/categories/subcategories/${subcategoryId}/specialties`,
    payload,
  );
  return data;
}

export async function updateSpecialty(
  specialtyId: number,
  payload: SpecialtyUpdate,
) {
  const { data } = await http.put<Specialty>(
    `/categories/specialties/${specialtyId}`,
    payload,
  );
  return data;
}

export async function deleteSpecialty(specialtyId: number) {
  await http.delete(`/categories/specialties/${specialtyId}`);
}

export async function importCategories(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await http.post("/categories/import", formData);
  return data as {
    created: number;
    updated: number;
    skipped: number;
    errors?: { row: number; level: string; detail: string }[];
  };
}

export async function exportCategories() {
  const response = await http.get<Blob>("/categories/export", {
    responseType: "blob",
  });
  return response.data;
}

export async function batchCategories(
  action: CategoryBatchAction,
  items: CategoryBatchItem[],
) {
  const { data } = await http.post("/categories/batch", { action, items });
  return data as {
    updated: number;
    deleted: number;
    skipped: number;
    errors?: { id: number; type: CategoryNodeType; detail: string }[];
  };
}
