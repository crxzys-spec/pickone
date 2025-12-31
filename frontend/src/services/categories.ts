import http from "../apis/http";
import type { ListParams, Page } from "../types/pagination";
import type {
  Category,
  CategoryCreate,
  CategoryUpdate,
} from "../types/domain";

export type CategoryBatchAction = "enable" | "disable" | "delete";

export interface CategoryBatchItem {
  id: number;
}

export async function listCategories(params: ListParams) {
  const { data } = await http.get<Page<Category>>("/categories", { params });
  return data;
}

export async function listCategoryTree() {
  const { data } = await http.get<Category[]>("/categories/tree");
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

export async function importCategories(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await http.post("/categories/import", formData);
  return data as {
    created: number;
    updated: number;
    skipped: number;
    errors?: { row: number; detail: string }[];
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
    errors?: { id: number; detail: string }[];
  };
}
