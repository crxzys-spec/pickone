<template>
  <div class="page">
    <div class="toolbar">
      <div class="actions">
        <el-button type="primary" @click="openCreate">
          {{ t("titles.new") }}
        </el-button>
        <el-button @click="refresh">{{ t("common.refresh") }}</el-button>
      </div>
      <el-input
        v-model="keyword"
        :placeholder="t('titles.searchPlaceholder')"
        clearable
        class="search"
      />
    </div>

    <el-table :data="filteredTitles" v-loading="loading" border stripe class="table">
      <el-table-column :label="t('titles.columns.id')" prop="id" width="80" />
      <el-table-column :label="t('titles.columns.name')" prop="name" min-width="180" />
      <el-table-column :label="t('titles.columns.code')" prop="code" min-width="160" />
      <el-table-column :label="t('titles.columns.sort')" prop="sort_order" width="120" />
      <el-table-column :label="t('titles.columns.active')" width="120">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? t("common.yes") : t("common.no") }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('titles.columns.actions')" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">
            {{ t("common.edit") }}
          </el-button>
          <el-button link type="danger" @click="confirmDelete(row)">
            {{ t("common.delete") }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>

  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px">
    <el-form :model="form" label-width="120px">
      <el-form-item :label="t('titles.form.name')">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item :label="t('titles.form.code')">
        <el-input v-model="form.code" />
      </el-form-item>
      <el-form-item :label="t('titles.form.sort')">
        <el-input-number v-model="form.sort_order" :min="0" />
      </el-form-item>
      <el-form-item :label="t('titles.form.active')">
        <el-switch v-model="form.is_active" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">
        {{ t("common.cancel") }}
      </el-button>
      <el-button type="primary" @click="submitForm">
        {{ t("common.save") }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useI18n } from "vue-i18n";

import { createTitle, deleteTitle, listTitles, updateTitle } from "../../services/titles";
import type { Title } from "../../types/domain";

interface TitleForm {
  name: string;
  code: string;
  sort_order: number;
  is_active: boolean;
}

const titles = ref<Title[]>([]);
const loading = ref(false);
const keyword = ref("");
const { t } = useI18n();

const dialogVisible = ref(false);
const isEditing = ref(false);
const editingId = ref<number | null>(null);

const form = reactive<TitleForm>({
  name: "",
  code: "",
  sort_order: 0,
  is_active: true,
});

const dialogTitle = computed(() =>
  isEditing.value ? t("titles.dialog.edit") : t("titles.dialog.new"),
);

const filteredTitles = computed(() => {
  const key = keyword.value.trim().toLowerCase();
  if (!key) {
    return titles.value;
  }
  return titles.value.filter((item) => item.name.toLowerCase().includes(key));
});

function resetForm() {
  form.name = "";
  form.code = "";
  form.sort_order = 0;
  form.is_active = true;
}

async function refresh() {
  loading.value = true;
  try {
    titles.value = await listTitles();
  } finally {
    loading.value = false;
  }
}

function openCreate() {
  resetForm();
  isEditing.value = false;
  editingId.value = null;
  dialogVisible.value = true;
}

function openEdit(title: Title) {
  isEditing.value = true;
  editingId.value = title.id;
  form.name = title.name;
  form.code = title.code ?? "";
  form.sort_order = title.sort_order;
  form.is_active = title.is_active;
  dialogVisible.value = true;
}

async function submitForm() {
  try {
    if (isEditing.value && editingId.value) {
      await updateTitle(editingId.value, {
        name: form.name,
        code: form.code || null,
        sort_order: form.sort_order,
        is_active: form.is_active,
      });
      ElMessage.success(t("titles.messages.updated"));
    } else {
      await createTitle({
        name: form.name,
        code: form.code || null,
        sort_order: form.sort_order,
        is_active: form.is_active,
      });
      ElMessage.success(t("titles.messages.created"));
    }
    dialogVisible.value = false;
    await refresh();
  } catch (error) {
    ElMessage.error(t("titles.messages.opFailed"));
  }
}

async function confirmDelete(title: Title) {
  try {
    await ElMessageBox.confirm(
      t("titles.messages.deleteConfirm", { name: title.name }),
      t("common.confirm"),
      { type: "warning" },
    );
  } catch {
    return;
  }
  await deleteTitle(title.id);
  ElMessage.success(t("titles.messages.deleted"));
  await refresh();
}

onMounted(refresh);
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


.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 12px;
}

.actions {
  display: flex;
  gap: 8px;
}

.search {
  max-width: 260px;
}

.table {
  width: 100%;
}
</style>
