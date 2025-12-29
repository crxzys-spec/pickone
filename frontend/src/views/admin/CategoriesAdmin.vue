<template>
  <div class="page">
    <div class="grid">
      <section class="panel panel-left">
        <div class="toolbar">
          <div class="actions">
            <el-upload
              :show-file-list="false"
              :http-request="handleImport"
              accept=".xlsx"
            >
              <el-button :loading="importing">{{ t("common.import") }}</el-button>
            </el-upload>
            <el-button :loading="exporting" @click="handleExport">
              {{ t("common.export") }}
            </el-button>
            <el-button @click="refreshTree">{{ t("common.refresh") }}</el-button>
            <el-button @click="expandAll">{{ t("common.expand") }}</el-button>
            <el-button @click="collapseAll">{{ t("common.collapse") }}</el-button>
            <el-button
              :disabled="!hasChecked"
              :loading="batching"
              @click="handleBatchEnable"
            >
              {{ t("categories.actions.batchEnable") }}
            </el-button>
            <el-button
              :disabled="!hasChecked"
              :loading="batching"
              @click="handleBatchDisable"
            >
              {{ t("categories.actions.batchDisable") }}
            </el-button>
            <el-button
              :disabled="!hasChecked"
              :loading="batching"
              type="danger"
              @click="handleBatchDelete"
            >
              {{ t("categories.actions.batchDelete") }}
            </el-button>
            <el-button
              :disabled="!hasChecked"
              :loading="batching"
              @click="clearChecked"
            >
              {{ t("categories.actions.clearSelection") }}
            </el-button>
          </div>
          <el-input
            v-model="keyword"
            :placeholder="t('categories.searchPlaceholder')"
            clearable
            class="search"
          />
        </div>

        <el-tree
          ref="treeRef"
          :data="treeData"
          :props="treeProps"
          node-key="key"
          highlight-current
          show-checkbox
          :check-strictly="false"
          :check-on-click-node="false"
          :filter-node-method="filterNode"
          v-loading="loading"
          class="tree"
          @check="handleCheck"
          @node-expand="handleNodeExpand"
          @node-collapse="handleNodeCollapse"
        >
          <template #default="{ data }">
            <div
              class="tree-node"
              :class="{ 'tree-node--inactive': !data.is_active }"
              @click.stop="handleNodeClick(data)"
            >
              <div class="tree-left">
                <span
                  class="level-icon"
                  :class="`level-icon--${data.type}`"
                  aria-hidden="true"
                ></span>
                <el-tag size="small" :type="levelTagType(data.type)">
                  {{ t(`categories.levels.${data.type}`) }}
                </el-tag>
                <span class="tree-name">{{ data.name }}</span>
                <span v-if="data.code" class="tree-code">{{ data.code }}</span>
                <span v-else class="tree-code tree-code--missing">
                  {{ t("categories.labels.missingCode") }}
                </span>
              </div>
              <div class="tree-right">
                <div class="tree-actions">
                  <el-button
                    v-if="data.type !== 'specialty'"
                    link
                    size="small"
                    class="icon-button"
                    :title="t('categories.actions.addChild')"
                    :aria-label="t('categories.actions.addChild')"
                    @click.stop="openCreateChild(data)"
                  >
                    <svg class="icon-svg" viewBox="0 0 16 16" aria-hidden="true">
                      <path d="M8 3.5v9M3.5 8h9" />
                    </svg>
                  </el-button>
                  <el-button
                    link
                    size="small"
                    type="danger"
                    class="icon-button icon-button--danger"
                    :title="t('common.delete')"
                    :aria-label="t('common.delete')"
                    @click.stop="confirmDelete(data)"
                  >
                    <svg
                      class="icon-svg"
                      viewBox="0 0 16 16"
                      aria-hidden="true"
                    >
                      <path d="M3.5 5.5h9M6.5 5.5v6M9.5 5.5v6M6 3.5h4" />
                      <path d="M4.5 5.5l.6 7h5.8l.6-7" />
                    </svg>
                  </el-button>
                </div>
              </div>
            </div>
          </template>
        </el-tree>
      </section>

      <section class="panel panel-right">
        <div class="panel-header">
          <div class="panel-title">
            {{ formTitle }}
            <el-tag v-if="formMode !== 'empty'" size="small" class="panel-tag">
              {{ t(`categories.levels.${formType}`) }}
            </el-tag>
          </div>
          <div class="panel-actions">
            <el-button type="primary" @click="openCreateCategory">
              {{ t("categories.actions.newCategory") }}
            </el-button>
          </div>
        </div>

        <el-empty
          v-if="formMode === 'empty'"
          :description="t('categories.form.empty')"
        />
        <div v-else class="form-card">
          <el-form
            ref="formRef"
            :model="formState"
            :rules="formRules"
            label-width="120px"
          >
            <div class="form-section">
              <div class="form-section-title">
                {{ t("categories.form.section.basic") }}
              </div>
              <el-form-item v-if="formParent" :label="t('categories.form.parent')">
                <el-input :model-value="formParent.name" disabled />
              </el-form-item>
              <el-form-item
                :label="t(formLabelPrefix + '.name')"
                prop="name"
                required
              >
                <el-input v-model="formState.name" />
              </el-form-item>
              <el-form-item
                :label="t(formLabelPrefix + '.code')"
                prop="code"
                required
              >
                <el-input v-model="formState.code" />
              </el-form-item>
            </div>
            <div class="form-section">
              <div class="form-section-title">
                {{ t("categories.form.section.settings") }}
              </div>
              <el-form-item :label="t(formLabelPrefix + '.sort')">
                <el-input-number v-model="formState.sort_order" :min="0" />
              </el-form-item>
              <el-form-item :label="t(formLabelPrefix + '.active')">
                <el-switch v-model="formState.is_active" />
              </el-form-item>
            </div>
            <div class="form-actions">
              <el-button @click="cancelForm">
                {{ t("common.cancel") }}
              </el-button>
              <el-button type="primary" @click="submitForm">
                {{ t("common.save") }}
              </el-button>
            </div>
          </el-form>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from "vue";
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules,
  type UploadRequestOptions,
} from "element-plus";
import { useI18n } from "vue-i18n";

import {
  batchCategories,
  createCategory,
  createSubcategory,
  createSpecialty,
  deleteCategory,
  deleteSubcategory,
  deleteSpecialty,
  exportCategories,
  importCategories,
  listCategoryTree,
  updateCategory,
  updateSubcategory,
  updateSpecialty,
} from "../../services/categories";
import type { CategoryTree } from "../../types/domain";
import { resolveErrorMessage } from "../../utils/errors";

type NodeType = "category" | "subcategory" | "specialty";
type FormMode = "empty" | "create" | "edit";

interface TreeNode {
  key: string;
  id: number;
  type: NodeType;
  name: string;
  code?: string | null;
  is_active: boolean;
  sort_order: number;
  parent_id?: number | null;
  parent_name?: string | null;
  children?: TreeNode[];
}

interface FormState {
  name: string;
  code: string;
  sort_order: number;
  is_active: boolean;
}

const treeData = ref<TreeNode[]>([]);
const treeRef = ref();
const keyword = ref("");
const loading = ref(false);
const importing = ref(false);
const exporting = ref(false);
const batching = ref(false);
const selectedNode = ref<TreeNode | null>(null);
const expandedKeys = ref<string[]>([]);
const checkedKeys = ref<string[]>([]);
const checkedNodes = ref<TreeNode[]>([]);
const formMode = ref<FormMode>("empty");
const { t } = useI18n();

const formType = ref<NodeType>("category");
const formParent = ref<{ id: number; name: string; type: NodeType } | null>(null);

const formState = reactive<FormState>({
  name: "",
  code: "",
  sort_order: 0,
  is_active: true,
});
const formRef = ref<FormInstance>();
const formRules = computed<FormRules>(() => ({
  name: [
    {
      required: true,
      message: t("categories.form.nameRequired"),
      trigger: "blur",
    },
  ],
  code: [
    {
      required: true,
      message: t("categories.form.codeRequired"),
      trigger: "blur",
    },
  ],
}));

const treeProps = {
  children: "children",
  label: "name",
};

const formLabelPrefix = computed(() => {
  if (formType.value === "category") {
    return "categories.form";
  }
  if (formType.value === "subcategory") {
    return "categories.subcategories.form";
  }
  return "categories.specialties.form";
});

const formTitle = computed(() => {
  if (formMode.value === "empty") {
    return t("categories.form.title");
  }
  if (formType.value === "category") {
    return formMode.value === "edit"
      ? t("categories.dialog.edit")
      : t("categories.dialog.new");
  }
  if (formType.value === "subcategory") {
    return formMode.value === "edit"
      ? t("categories.subcategories.dialog.edit")
      : t("categories.subcategories.dialog.new");
  }
  return formMode.value === "edit"
    ? t("categories.specialties.dialog.edit")
    : t("categories.specialties.dialog.new");
});

const checkedCount = computed(() => checkedKeys.value.length);
const hasChecked = computed(() => checkedCount.value > 0);

function translateCategoryDetail(detail: string) {
  switch (detail) {
    case "Category is in use":
      return t("categories.messages.inUse");
    case "Category is in use by rules":
      return t("categories.messages.inUseByRules");
    case "Category is in use by draws":
      return t("categories.messages.inUseByDraws");
    case "Category is in use by rules, draws":
      return t("categories.messages.inUseByRulesAndDraws");
    case "Category name already exists":
      return t("categories.messages.nameExists");
    case "Category code already exists":
      return t("categories.messages.codeExists");
    case "Category code is required":
      return t("categories.messages.codeRequired");
    case "Category not found":
      return t("categories.messages.notFound");
    case "Subcategory is in use":
      return t("categories.subcategories.messages.inUse");
    case "Subcategory is in use by rules":
      return t("categories.subcategories.messages.inUseByRules");
    case "Subcategory is in use by draws":
      return t("categories.subcategories.messages.inUseByDraws");
    case "Subcategory is in use by rules, draws":
      return t("categories.subcategories.messages.inUseByRulesAndDraws");
    case "Subcategory has specialties":
      return t("categories.subcategories.messages.hasSpecialties");
    case "Subcategory name already exists":
      return t("categories.subcategories.messages.nameExists");
    case "Subcategory code already exists":
      return t("categories.subcategories.messages.codeExists");
    case "Subcategory code is required":
      return t("categories.subcategories.messages.codeRequired");
    case "Subcategory not found":
      return t("categories.subcategories.messages.notFound");
    case "Specialty is in use":
      return t("categories.specialties.messages.inUse");
    case "Specialty is in use by rules":
      return t("categories.specialties.messages.inUseByRules");
    case "Specialty is in use by draws":
      return t("categories.specialties.messages.inUseByDraws");
    case "Specialty is in use by rules, draws":
      return t("categories.specialties.messages.inUseByRulesAndDraws");
    case "Specialty name already exists":
      return t("categories.specialties.messages.nameExists");
    case "Specialty code already exists":
      return t("categories.specialties.messages.codeExists");
    case "Specialty code is required":
      return t("categories.specialties.messages.codeRequired");
    case "Specialty not found":
      return t("categories.specialties.messages.notFound");
    default:
      return null;
  }
}

watch(keyword, (value) => {
  treeRef.value?.filter(value.trim());
});

function filterNode(value: string, data: TreeNode) {
  if (!value) {
    return true;
  }
  const lower = value.toLowerCase();
  return (
    data.name.toLowerCase().includes(lower) ||
    (data.code ?? "").toLowerCase().includes(lower)
  );
}

function levelTagType(type: NodeType) {
  if (type === "category") {
    return "warning";
  }
  if (type === "subcategory") {
    return "success";
  }
  return "info";
}

function syncCheckedNodes() {
  checkedKeys.value =
    (treeRef.value?.getCheckedKeys?.(false) as string[]) ?? checkedKeys.value;
  const nodes = treeRef.value?.getCheckedNodes?.(false, false) ?? [];
  checkedNodes.value = nodes as TreeNode[];
}

function resetForm() {
  formState.name = "";
  formState.code = "";
  formState.sort_order = 0;
  formState.is_active = true;
}

function buildTree(categories: CategoryTree[]): TreeNode[] {
  const sortedCategories = [...categories].sort(sortByOrder);
  return sortedCategories.map((category) => {
    const subcategories = (category.subcategories ?? []).sort(sortByOrder);
    return {
      key: `cat-${category.id}`,
      id: category.id,
      type: "category",
      name: category.name,
      code: category.code,
      is_active: category.is_active,
      sort_order: category.sort_order,
      children: subcategories.map((subcategory) => {
        const specialties = (subcategory.specialties ?? []).sort(sortByOrder);
        return {
          key: `sub-${subcategory.id}`,
          id: subcategory.id,
          type: "subcategory",
          name: subcategory.name,
          code: subcategory.code,
          is_active: subcategory.is_active,
          sort_order: subcategory.sort_order,
          parent_id: category.id,
          parent_name: category.name,
          children: specialties.map((specialty) => ({
            key: `sp-${specialty.id}`,
            id: specialty.id,
            type: "specialty",
            name: specialty.name,
            code: specialty.code,
            is_active: specialty.is_active,
            sort_order: specialty.sort_order,
            parent_id: subcategory.id,
            parent_name: subcategory.name,
          })),
        };
      }),
    };
  });
}

function sortByOrder<
  T extends { sort_order: number; name: string; code?: string | null },
>(a: T, b: T) {
  if (a.sort_order !== b.sort_order) {
    return a.sort_order - b.sort_order;
  }
  const codeA = (a.code ?? "").toString();
  const codeB = (b.code ?? "").toString();
  if (codeA !== codeB) {
    return codeA.localeCompare(codeB);
  }
  return a.name.localeCompare(b.name);
}

function findNodeByKey(nodes: TreeNode[], key: string): TreeNode | null {
  for (const node of nodes) {
    if (node.key === key) {
      return node;
    }
    if (node.children && node.children.length > 0) {
      const found = findNodeByKey(node.children, key);
      if (found) {
        return found;
      }
    }
  }
  return null;
}

function findParentAndIndex(
  nodes: TreeNode[],
  key: string,
  parent: TreeNode | null = null,
): { parent: TreeNode | null; siblings: TreeNode[]; index: number } | null {
  for (let index = 0; index < nodes.length; index += 1) {
    const node = nodes[index];
    if (node.key === key) {
      return { parent, siblings: nodes, index };
    }
    if (node.children && node.children.length > 0) {
      const result = findParentAndIndex(node.children, key, node);
      if (result) {
        return result;
      }
    }
  }
  return null;
}

function getFallbackKeyOnDelete(key: string) {
  const info = findParentAndIndex(treeData.value, key);
  if (!info) {
    return null;
  }
  const { parent, siblings, index } = info;
  const prev = siblings[index - 1];
  if (prev) {
    return prev.key;
  }
  const next = siblings[index + 1];
  if (next) {
    return next.key;
  }
  return parent?.key ?? null;
}

function collectExpandedKeys(nodes: TreeNode[], keys: string[] = []) {
  for (const node of nodes) {
    if (node.children && node.children.length > 0) {
      keys.push(node.key);
      collectExpandedKeys(node.children, keys);
    }
  }
  return keys;
}

type StoreNode = {
  childNodes?: StoreNode[];
  expand?: (callback?: (() => void) | null, expandParent?: boolean) => void;
  collapse?: () => void;
};

type TreeStore = {
  root?: StoreNode;
  getNode?: (key: string) => StoreNode | null;
  setDefaultExpandedKeys?: (keys: string[]) => void;
};

function getTreeStore() {
  const tree = treeRef.value as { store?: TreeStore } | undefined;
  return tree?.store;
}

function walkStoreNodes(nodes: StoreNode[], callback: (node: StoreNode) => void) {
  nodes.forEach((node) => {
    callback(node);
    if (node.childNodes && node.childNodes.length > 0) {
      walkStoreNodes(node.childNodes, callback);
    }
  });
}

function applyExpandedKeys(keys: string[]) {
  const store = getTreeStore();
  if (!store) {
    return;
  }
  if (typeof store.setDefaultExpandedKeys === "function") {
    store.setDefaultExpandedKeys(keys);
    return;
  }
  keys.forEach((key) => {
    const node = store.getNode?.(key);
    node?.expand?.(null, true);
  });
}

function expandAll() {
  const store = getTreeStore();
  const nodes = store?.root?.childNodes;
  if (!nodes || nodes.length === 0) {
    return;
  }
  const keys = collectExpandedKeys(treeData.value);
  expandedKeys.value = keys;
  walkStoreNodes(nodes, (node) => node.expand?.(null, true));
}

function collapseAll() {
  const store = getTreeStore();
  const nodes = store?.root?.childNodes;
  if (!nodes || nodes.length === 0) {
    return;
  }
  expandedKeys.value = [];
  walkStoreNodes(nodes, (node) => node.collapse?.());
}

async function refreshTree() {
  loading.value = true;
  const keepEdit = formMode.value === "edit";
  const selectedKey = selectedNode.value?.key;
  try {
    const result = await listCategoryTree();
    treeData.value = buildTree(result);
    await nextTick();
    treeRef.value?.filter(keyword.value.trim());
    if (expandedKeys.value.length > 0) {
      applyExpandedKeys(expandedKeys.value);
    }
    if (checkedKeys.value.length > 0) {
      treeRef.value?.setCheckedKeys?.(checkedKeys.value, false);
      syncCheckedNodes();
    }
    if (keepEdit && selectedKey) {
      const found = findNodeByKey(treeData.value, selectedKey);
      if (found) {
        selectNode(found);
        startEdit(found);
      } else {
        selectedNode.value = null;
        formMode.value = "empty";
      }
    }
  } finally {
    loading.value = false;
  }
}

function selectNode(node: TreeNode | null) {
  selectedNode.value = node;
  if (node) {
    treeRef.value?.setCurrentKey(node.key);
  }
}

function scrollCurrentNodeIntoView() {
  const treeEl = treeRef.value?.$el as HTMLElement | undefined;
  if (!treeEl) {
    return;
  }
  const currentNode = treeEl.querySelector(".el-tree-node.is-current") as
    | HTMLElement
    | null;
  currentNode?.scrollIntoView({ block: "center" });
}

async function focusNodeByKey(key: string, mode: "edit" | "select" = "edit") {
  const found = findNodeByKey(treeData.value, key);
  if (!found) {
    return false;
  }
  selectNode(found);
  if (mode === "edit") {
    startEdit(found);
  }
  await nextTick();
  scrollCurrentNodeIntoView();
  return true;
}

function startEdit(node: TreeNode) {
  formMode.value = "edit";
  formType.value = node.type;
  formState.name = node.name;
  formState.code = node.code ?? "";
  formState.sort_order = node.sort_order;
  formState.is_active = node.is_active;
  if (node.parent_id && node.parent_name) {
    formParent.value = {
      id: node.parent_id,
      name: node.parent_name,
      type: node.type === "subcategory" ? "category" : "subcategory",
    };
  } else {
    formParent.value = null;
  }
}

function startCreate(type: NodeType, parent?: TreeNode) {
  formMode.value = "create";
  formType.value = type;
  resetForm();
  if (parent) {
    formParent.value = { id: parent.id, name: parent.name, type: parent.type };
  } else {
    formParent.value = null;
  }
}

function cancelForm() {
  if (selectedNode.value) {
    startEdit(selectedNode.value);
  } else {
    formMode.value = "empty";
    resetForm();
    formParent.value = null;
  }
}

function handleNodeClick(data: TreeNode) {
  selectNode(data);
  startEdit(data);
}

function handleNodeExpand(data: TreeNode) {
  if (!expandedKeys.value.includes(data.key)) {
    expandedKeys.value = [...expandedKeys.value, data.key];
  }
}

function handleNodeCollapse(data: TreeNode) {
  if (expandedKeys.value.includes(data.key)) {
    expandedKeys.value = expandedKeys.value.filter((key) => key !== data.key);
  }
}

function handleCheck(
  _data: TreeNode,
  _info: { checkedKeys: string[]; checkedNodes: TreeNode[] },
) {
  syncCheckedNodes();
}

function ensureExpandedForCreate() {
  const keys = new Set(expandedKeys.value);
  if (formType.value === "subcategory" && formParent.value) {
    keys.add(`cat-${formParent.value.id}`);
  }
  if (formType.value === "specialty" && formParent.value) {
    keys.add(`sub-${formParent.value.id}`);
    if (selectedNode.value?.parent_id) {
      keys.add(`cat-${selectedNode.value.parent_id}`);
    }
  }
  expandedKeys.value = Array.from(keys);
}

function openCreateCategory() {
  startCreate("category");
}

function openCreateChild(node: TreeNode) {
  selectNode(node);
  if (!expandedKeys.value.includes(node.key)) {
    expandedKeys.value = [...expandedKeys.value, node.key];
    applyExpandedKeys(expandedKeys.value);
  }
  if (node.type === "category") {
    startCreate("subcategory", node);
  } else if (node.type === "subcategory") {
    startCreate("specialty", node);
  }
}

function openEdit(node: TreeNode) {
  selectNode(node);
  startEdit(node);
}

function getAncestorKeys(node: TreeNode) {
  if (node.type === "category") {
    return [];
  }
  if (node.type === "subcategory") {
    return node.parent_id ? [`cat-${node.parent_id}`] : [];
  }
  const keys: string[] = [];
  if (node.parent_id) {
    const subKey = `sub-${node.parent_id}`;
    keys.push(subKey);
    const subNode = findNodeByKey(treeData.value, subKey);
    if (subNode?.parent_id) {
      keys.push(`cat-${subNode.parent_id}`);
    }
  }
  return keys;
}

function getPrimaryCheckedNodes() {
  const keySet = new Set(checkedKeys.value);
  const nodes = checkedKeys.value
    .map((key) => findNodeByKey(treeData.value, key))
    .filter((node): node is TreeNode => Boolean(node));
  return nodes.filter((node) => {
    const ancestors = getAncestorKeys(node);
    return !ancestors.some((ancestor) => keySet.has(ancestor));
  });
}

function buildBatchItems(mode: "all" | "primary" = "all") {
  const nodes = mode === "primary" ? getPrimaryCheckedNodes() : checkedNodes.value;
  return nodes.map((node) => ({
    id: node.id,
    type: node.type,
  }));
}

function clearChecked() {
  checkedKeys.value = [];
  checkedNodes.value = [];
  treeRef.value?.setCheckedKeys?.([]);
}

async function handleImport(options: UploadRequestOptions) {
  importing.value = true;
  try {
    const result = await importCategories(options.file as File);
    ElMessage.success(
      t("categories.messages.importSuccess", {
        created: result.created,
        updated: result.updated,
        skipped: result.skipped,
      }),
    );
    if (result.errors && result.errors.length > 0) {
      const sample = result.errors[0]?.detail ?? "";
      ElMessage.warning(
        t("categories.messages.importMissingCode", {
          count: result.errors.length,
          sample,
        }),
      );
    }
    await refreshTree();
    options.onSuccess?.(result);
  } catch (error) {
    ElMessage.error(t("categories.messages.importFailed"));
    options.onError?.(error as Error);
  } finally {
    importing.value = false;
  }
}

async function handleExport() {
  exporting.value = true;
  try {
    const blob = await exportCategories();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "categories_export.xlsx";
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    ElMessage.error(t("categories.messages.exportFailed"));
  } finally {
    exporting.value = false;
  }
}

async function submitForm() {
  if (formMode.value === "empty") {
    return;
  }
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) {
    return;
  }
  let focusKey: string | null = null;
  try {
    if (formType.value === "category") {
      if (formMode.value === "edit" && selectedNode.value) {
        await updateCategory(selectedNode.value.id, {
          name: formState.name,
          code: formState.code || null,
          sort_order: formState.sort_order,
          is_active: formState.is_active,
        });
        ElMessage.success(t("categories.messages.updated"));
      } else {
        const created = await createCategory({
          name: formState.name,
          code: formState.code || null,
          sort_order: formState.sort_order,
          is_active: formState.is_active,
        });
        focusKey = `cat-${created.id}`;
        ElMessage.success(t("categories.messages.created"));
        resetForm();
      }
    } else if (formType.value === "subcategory") {
      if (formMode.value === "edit" && selectedNode.value) {
        await updateSubcategory(selectedNode.value.id, {
          name: formState.name,
          code: formState.code || null,
          sort_order: formState.sort_order,
          is_active: formState.is_active,
        });
        ElMessage.success(t("categories.subcategories.messages.updated"));
      } else {
        if (!formParent.value) {
          return;
        }
        const created = await createSubcategory(formParent.value.id, {
          name: formState.name,
          code: formState.code || null,
          sort_order: formState.sort_order,
          is_active: formState.is_active,
        });
        focusKey = `sub-${created.id}`;
        ElMessage.success(t("categories.subcategories.messages.created"));
        resetForm();
      }
    } else {
      if (formMode.value === "edit" && selectedNode.value) {
        await updateSpecialty(selectedNode.value.id, {
          name: formState.name,
          code: formState.code || null,
          sort_order: formState.sort_order,
          is_active: formState.is_active,
        });
        ElMessage.success(t("categories.specialties.messages.updated"));
      } else {
        if (!formParent.value) {
          return;
        }
        const created = await createSpecialty(formParent.value.id, {
          name: formState.name,
          code: formState.code || null,
          sort_order: formState.sort_order,
          is_active: formState.is_active,
        });
        focusKey = `sp-${created.id}`;
        ElMessage.success(t("categories.specialties.messages.created"));
        resetForm();
      }
    }
    if (formMode.value === "create") {
      ensureExpandedForCreate();
    }
    await refreshTree();
    if (focusKey) {
      await focusNodeByKey(focusKey, "edit");
    }
  } catch (error) {
    ElMessage.error(
      resolveErrorMessage(error, t("categories.messages.opFailed"), translateCategoryDetail),
    );
  }
}

async function confirmDelete(node: TreeNode) {
  const message =
    node.type === "category"
      ? t("categories.messages.deleteConfirm", { name: node.name })
      : node.type === "subcategory"
        ? t("categories.subcategories.messages.deleteConfirm", { name: node.name })
        : t("categories.specialties.messages.deleteConfirm", { name: node.name });
  const wasSelected = selectedNode.value?.key === node.key;
  const fallbackKey = wasSelected ? getFallbackKeyOnDelete(node.key) : null;
  try {
    await ElMessageBox.confirm(message, t("common.confirm"), {
      type: "warning",
    });
  } catch {
    return;
  }
  try {
    if (node.type === "category") {
      await deleteCategory(node.id);
      ElMessage.success(t("categories.messages.deleted"));
    } else if (node.type === "subcategory") {
      await deleteSubcategory(node.id);
      ElMessage.success(t("categories.subcategories.messages.deleted"));
    } else {
      await deleteSpecialty(node.id);
      ElMessage.success(t("categories.specialties.messages.deleted"));
    }
    if (wasSelected) {
      selectedNode.value = null;
      formMode.value = "empty";
    }
    expandedKeys.value = expandedKeys.value.filter((key) => key !== node.key);
    await refreshTree();
    if (fallbackKey) {
      await focusNodeByKey(fallbackKey, "edit");
    }
  } catch (error) {
    const fallback =
      node.type === "category"
        ? t("categories.messages.deleteFailed")
        : node.type === "subcategory"
          ? t("categories.subcategories.messages.deleteFailed")
          : t("categories.specialties.messages.deleteFailed");
    ElMessage.error(resolveErrorMessage(error, fallback, translateCategoryDetail));
  }
}

async function handleBatchEnable() {
  if (!hasChecked.value) {
    return;
  }
  batching.value = true;
  try {
    const result = await batchCategories("enable", buildBatchItems("all"));
    ElMessage.success(
      t("categories.messages.batchEnableSuccess", { count: result.updated }),
    );
    await refreshTree();
  } catch (error) {
    ElMessage.error(
      resolveErrorMessage(error, t("categories.messages.batchFailed"), translateCategoryDetail),
    );
  } finally {
    batching.value = false;
    clearChecked();
  }
}

async function handleBatchDisable() {
  if (!hasChecked.value) {
    return;
  }
  batching.value = true;
  try {
    const result = await batchCategories("disable", buildBatchItems("all"));
    ElMessage.success(
      t("categories.messages.batchDisableSuccess", { count: result.updated }),
    );
    await refreshTree();
  } catch (error) {
    ElMessage.error(
      resolveErrorMessage(error, t("categories.messages.batchFailed"), translateCategoryDetail),
    );
  } finally {
    batching.value = false;
    clearChecked();
  }
}

async function handleBatchDelete() {
  if (!hasChecked.value) {
    return;
  }
  try {
    await ElMessageBox.confirm(
      t("categories.messages.batchDeleteConfirm", { count: checkedCount.value }),
      t("common.confirm"),
      { type: "warning" },
    );
  } catch {
    return;
  }
  batching.value = true;
  const selectedKey = selectedNode.value?.key;
  const selectedDeleted = selectedKey && checkedKeys.value.includes(selectedKey);
  if (selectedDeleted) {
    selectedNode.value = null;
    formMode.value = "empty";
  }
  try {
    const result = await batchCategories("delete", buildBatchItems("primary"));
    ElMessage.success(
      t("categories.messages.batchDeleteSuccess", {
        deleted: result.deleted,
        skipped: result.skipped,
      }),
    );
    const firstError = result.errors?.[0]?.detail;
    if (result.skipped > 0 && firstError) {
      const translated = translateCategoryDetail(firstError) ?? firstError;
      ElMessage.warning(
        t("categories.messages.batchDeleteSkippedReason", {
          skipped: result.skipped,
          reason: translated,
        }),
      );
    }
    await refreshTree();
  } catch (error) {
    ElMessage.error(
      resolveErrorMessage(error, t("categories.messages.batchFailed"), translateCategoryDetail),
    );
  } finally {
    batching.value = false;
    clearChecked();
  }
}

onMounted(refreshTree);
</script>

<style scoped>
.page {
  position: relative;
  background: var(--gov-card);
  padding: 20px;
  border-radius: 6px;
  border: 1px solid var(--gov-border);
  box-shadow: var(--gov-shadow);
  overflow: hidden;
  animation: gov-rise 360ms ease-out;
}

.page::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  height: 4px;
  width: 100%;
  background: linear-gradient(
    90deg,
    var(--gov-blue-700),
    var(--gov-blue-500),
    var(--gov-blue-700)
  );
}

.grid {
  display: grid;
  grid-template-columns: minmax(360px, 520px) minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}

.panel {
  background: var(--gov-card);
  border: 1px solid var(--gov-border);
  border-radius: 6px;
  padding: 16px;
}

.panel-left {
  display: flex;
  flex-direction: column;
  height: 85vh;
}

.panel-right {
  min-height: 85vh;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.panel-title {
  font-weight: 600;
  color: var(--gov-blue-700);
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-tag {
  background: #f1f5fb;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 12px;
  flex-wrap: wrap;
  flex: 0 0 auto;
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.search {
  min-width: 200px;
  max-width: 280px;
  flex: 1 1 auto;
}

.tree {
  background: var(--gov-card);
  border: 1px solid var(--gov-border);
  border-radius: 6px;
  padding: 12px;
  flex: 1 1 auto;
  min-height: 0;
  overflow: auto;
}

:deep(.el-tree-node__content) {
  width: 100%;
  box-sizing: border-box;
  padding-right: 8px;
}

:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background: #eef5ff;
  border-radius: 6px;
  box-shadow: inset 3px 0 0 var(--gov-blue-600);
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  padding: 4px 0;
}

.tree-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1 1 auto;
  min-width: 0;
  flex-wrap: nowrap;
  overflow: hidden;
}

.tree-right {
  display: flex;
  align-items: center;
  gap: 2px;
  flex-shrink: 0;
  min-width: 44px;
  justify-content: flex-end;
}

.level-icon {
  width: 10px;
  height: 10px;
  display: inline-block;
  border-radius: 50%;
  border: 1px solid transparent;
  flex: 0 0 auto;
}

.level-icon--category {
  background: #f6e6c4;
  border-color: #e0c58a;
}

.level-icon--subcategory {
  background: #d6ecdf;
  border-color: #a9d1b8;
  border-radius: 2px;
}

.level-icon--specialty {
  background: #d6e1f1;
  border-color: #a9bfd9;
  transform: rotate(45deg);
}

:deep(.el-tag.el-tag--warning) {
  --el-tag-bg-color: #fbf2de;
  --el-tag-border-color: #e9d7b6;
  --el-tag-text-color: #9b6a1f;
}

:deep(.el-tag.el-tag--success) {
  --el-tag-bg-color: #e6f3ec;
  --el-tag-border-color: #c7e1d5;
  --el-tag-text-color: #2e6b4e;
}

:deep(.el-tag.el-tag--info) {
  --el-tag-bg-color: #eff3f8;
  --el-tag-border-color: #d4dde7;
  --el-tag-text-color: #4a5d73;
}

.tree-name {
  font-weight: 600;
  color: var(--gov-text);
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tree-code {
  font-size: 12px;
  color: var(--gov-muted);
  background: #f2f5f9;
  border-radius: 4px;
  padding: 2px 6px;
  min-width: 0;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tree-code--missing {
  color: #9a3412;
  background: #fff7ed;
  border: 1px dashed #fdba74;
}

.tree-node--inactive {
  opacity: 0.55;
}

.tree-actions {
  display: flex;
  align-items: center;
  gap: 2px;
  margin-left: 4px;
  flex-shrink: 0;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
}

.icon-button {
  min-width: 0;
  width: 20px;
  height: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #3b4c63;
}

.icon-button :deep(.el-button__content) {
  padding: 0;
}

:deep(.tree-actions .el-button + .el-button) {
  margin-left: 0;
}

:deep(.icon-button.el-button) {
  padding: 0;
  line-height: 1;
}

.icon-button--danger {
  color: #b42318;
}

.icon-svg {
  width: 14px;
  height: 14px;
  stroke: currentColor;
  stroke-width: 1.6;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}

:deep(.el-tree-node__content:hover) .tree-actions,
:deep(.el-tree-node__content:focus-within) .tree-actions {
  opacity: 1;
  pointer-events: auto;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 16px;
}

.form-card {
  background: #f8fafc;
  border: 1px solid var(--gov-border);
  border-radius: 8px;
  padding: 16px;
}

.form-section {
  padding-bottom: 12px;
  margin-bottom: 16px;
  border-bottom: 1px dashed #d6dde8;
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.form-section-title {
  font-weight: 600;
  color: #233a55;
  margin-bottom: 12px;
}

@media (max-width: 900px) {
  .grid {
    grid-template-columns: 1fr;
  }
  .tree {
    max-height: none;
  }
}
</style>
