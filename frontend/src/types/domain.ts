export interface Expert {
  id: number;
  name: string;
  gender?: string | null;
  phone?: string | null;
  email?: string | null;
  company?: string | null;
  organization_id?: number | null;
  title?: string | null;
  title_id?: number | null;
  category_id?: number | null;
  category?: string | null;
  subcategory_id?: number | null;
  subcategory?: string | null;
  avoid_units?: string | null;
  avoid_persons?: string | null;
  is_active: boolean;
}

export interface ExpertCreate {
  name: string;
  gender?: string | null;
  phone?: string | null;
  email?: string | null;
  company?: string | null;
  organization_id?: number | null;
  title?: string | null;
  title_id?: number | null;
  category_id?: number | null;
  category?: string | null;
  subcategory_id?: number | null;
  subcategory?: string | null;
  avoid_units?: string | null;
  avoid_persons?: string | null;
  is_active: boolean;
}

export interface ExpertUpdate {
  name?: string | null;
  gender?: string | null;
  phone?: string | null;
  email?: string | null;
  company?: string | null;
  organization_id?: number | null;
  title?: string | null;
  title_id?: number | null;
  category_id?: number | null;
  category?: string | null;
  subcategory_id?: number | null;
  subcategory?: string | null;
  avoid_units?: string | null;
  avoid_persons?: string | null;
  is_active?: boolean | null;
}

export interface Rule {
  id: number;
  name: string;
  category_id?: number | null;
  category: string;
  subcategory_id?: number | null;
  subcategory?: string | null;
  title_required?: string | null;
  avoid_enabled: boolean;
  draw_method: string;
  is_active: boolean;
}

export interface RuleCreate {
  name: string;
  category_id?: number | null;
  category?: string | null;
  subcategory_id?: number | null;
  subcategory?: string | null;
  title_required?: string | null;
  avoid_enabled: boolean;
  draw_method: string;
  is_active: boolean;
}

export interface RuleUpdate {
  name?: string | null;
  category_id?: number | null;
  category?: string | null;
  subcategory_id?: number | null;
  subcategory?: string | null;
  title_required?: string | null;
  avoid_enabled?: boolean | null;
  draw_method?: string | null;
  is_active?: boolean | null;
}

export interface DrawApplication {
  id: number;
  category_id?: number | null;
  category: string;
  subcategory_id?: number | null;
  subcategory?: string | null;
  expert_count: number;
  backup_count: number;
  draw_method: string;
  review_time?: string | null;
  review_location?: string | null;
  status: string;
  rule_id?: number | null;
}

export interface DrawApply {
  category_id?: number | null;
  category?: string | null;
  subcategory_id?: number | null;
  subcategory?: string | null;
  expert_count: number;
  backup_count: number;
  draw_method: string;
  review_time?: string | null;
  review_location?: string | null;
  rule_id?: number | null;
}

export interface DrawUpdate {
  category_id?: number | null;
  category?: string | null;
  subcategory_id?: number | null;
  subcategory?: string | null;
  expert_count?: number | null;
  backup_count?: number | null;
  draw_method?: string | null;
  review_time?: string | null;
  review_location?: string | null;
  status?: string | null;
  rule_id?: number | null;
}

export interface DrawResultExpert {
  id: number;
  name: string;
  company?: string | null;
  category_id?: number | null;
  category?: string | null;
  subcategory_id?: number | null;
  subcategory?: string | null;
  phone?: string | null;
  email?: string | null;
  title?: string | null;
}

export interface DrawResultOut {
  id: number;
  draw_id: number;
  expert_id: number;
  is_backup: boolean;
  is_replacement: boolean;
  ordinal?: number | null;
  expert?: DrawResultExpert | null;
}

export interface Category {
  id: number;
  name: string;
  code?: string | null;
  is_active: boolean;
  sort_order: number;
}

export interface CategoryCreate {
  name: string;
  code?: string | null;
  is_active: boolean;
  sort_order: number;
}

export interface CategoryUpdate {
  name?: string | null;
  code?: string | null;
  is_active?: boolean | null;
  sort_order?: number | null;
}

export interface Organization {
  id: number;
  name: string;
  code?: string | null;
  is_active: boolean;
  sort_order: number;
}

export interface OrganizationCreate {
  name: string;
  code?: string | null;
  is_active: boolean;
  sort_order: number;
}

export interface OrganizationUpdate {
  name?: string | null;
  code?: string | null;
  is_active?: boolean | null;
  sort_order?: number | null;
}

export interface Subcategory {
  id: number;
  category_id: number;
  name: string;
  code?: string | null;
  is_active: boolean;
  sort_order: number;
}

export interface SubcategoryCreate {
  name: string;
  code?: string | null;
  is_active: boolean;
  sort_order: number;
}

export interface SubcategoryUpdate {
  name?: string | null;
  code?: string | null;
  is_active?: boolean | null;
  sort_order?: number | null;
}

export interface CategoryTree extends Category {
  subcategories: Subcategory[];
}

export interface Title {
  id: number;
  name: string;
  code?: string | null;
  is_active: boolean;
  sort_order: number;
}

export interface TitleCreate {
  name: string;
  code?: string | null;
  is_active: boolean;
  sort_order: number;
}

export interface TitleUpdate {
  name?: string | null;
  code?: string | null;
  is_active?: boolean | null;
  sort_order?: number | null;
}
