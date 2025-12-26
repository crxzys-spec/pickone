import http from "../apis/http";
import type { ListParams, Page } from "../types/pagination";
import type {
  Category,
  CategoryCreate,
  CategoryTree,
  CategoryUpdate,
  Subcategory,
  SubcategoryCreate,
  SubcategoryUpdate,
} from "../types/domain";

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
