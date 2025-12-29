<template>
  <div class="page">
    <div class="toolbar">
      <div class="actions">
        <el-button type="primary" @click="openCreate">
          {{ t("experts.new") }}
        </el-button>
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
        <el-button
          type="danger"
          :loading="deleting"
          :disabled="selectedIds.length === 0"
          @click="handleBatchDelete"
        >
          {{ t("experts.actions.batchDelete") }}
        </el-button>
        <el-button @click="refresh">{{ t("common.refresh") }}</el-button>
      </div>
      <el-input
        v-model="keyword"
        :placeholder="t('experts.searchPlaceholder')"
        clearable
        class="search"
      />
    </div>

    <el-table
      ref="tableRef"
      :data="experts"
      v-loading="loading"
      border
      stripe
      class="table"
      @sort-change="handleSortChange"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="48" />
      <el-table-column
        :label="t('experts.columns.id')"
        prop="id"
        width="80"
        sortable="custom"
      />
      <el-table-column
        :label="t('experts.columns.name')"
        prop="name"
        min-width="140"
        sortable="custom"
      >
        <template #default="{ row }">
          {{ maskName(row.name) || "-" }}
        </template>
      </el-table-column>
      <el-table-column
        :label="t('experts.columns.idCard')"
        prop="id_card_no"
        min-width="160"
        sortable="custom"
      >
        <template #default="{ row }">
          {{ maskIdCard(row.id_card_no) || "-" }}
        </template>
      </el-table-column>
      <el-table-column :label="t('experts.columns.gender')" width="90" prop="gender" sortable="custom">
        <template #default="{ row }">
          {{ genderLabel(row.gender) }}
        </template>
      </el-table-column>
      <el-table-column
        :label="t('experts.columns.company')"
        prop="company"
        min-width="180"
        sortable="custom"
      />
      <el-table-column
        :label="t('experts.columns.region')"
        prop="region"
        min-width="140"
        sortable="custom"
      />
      <el-table-column
        :label="t('experts.columns.specialties')"
        min-width="200"
      >
        <template #default="{ row }">
          {{ specialtiesLabel(row) }}
        </template>
      </el-table-column>
      <el-table-column
        :label="t('experts.columns.title')"
        prop="title"
        min-width="120"
        sortable="custom"
      />
      <el-table-column
        :label="t('experts.columns.phone')"
        prop="phone"
        min-width="140"
        sortable="custom"
      >
        <template #default="{ row }">
          {{ maskPhone(row.phone) || "-" }}
        </template>
      </el-table-column>
      <el-table-column :label="t('experts.columns.appointmentLetters')" width="140">
        <template #default="{ row }">
          <el-button
            v-if="row.appointment_letter_urls?.length"
            link
            type="primary"
            @click="openLetters(row)"
          >
            {{ t("experts.actions.viewLetters") }} ({{ row.appointment_letter_urls.length }})
          </el-button>
          <span v-else class="muted">-</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('experts.columns.active')" width="100" prop="is_active" sortable="custom">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? t("common.yes") : t("common.no") }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('experts.columns.actions')" width="220" fixed="right">
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

    <div class="pager">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange"
        @size-change="handlePageSizeChange"
      />
    </div>
  </div>

  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="620px">
    <el-form :model="form" label-width="120px">
      <el-form-item :label="t('experts.form.name')" required>
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item :label="t('experts.form.idCard')" required>
        <el-input v-model="form.id_card_no" />
      </el-form-item>
      <el-form-item :label="t('experts.form.gender')">
        <el-select v-model="form.gender" clearable style="width: 100%;">
          <el-option :label="t('experts.gender.male')" value="男" />
          <el-option :label="t('experts.gender.female')" value="女" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('experts.form.phone')">
        <el-input v-model="form.phone" />
      </el-form-item>
      <el-form-item :label="t('experts.form.email')">
        <el-input v-model="form.email" />
      </el-form-item>
      <el-form-item :label="t('experts.form.company')">
        <el-select
          v-model="form.organization_id"
          clearable
          filterable
          style="width: 100%;"
          @change="handleOrganizationChange"
        >
          <el-option
            v-for="organization in organizations"
            :key="organization.id"
            :label="organization.name"
            :value="organization.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('experts.form.region')">
        <el-select
          v-model="form.region_id"
          clearable
          filterable
          style="width: 100%;"
          @change="handleRegionChange"
        >
          <el-option
            v-for="region in regions"
            :key="region.id"
            :label="region.name"
            :value="region.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('experts.form.title')">
        <el-select
          v-model="form.title_id"
          clearable
          filterable
          style="width: 100%;"
          @change="handleTitleChange"
        >
          <el-option
            v-for="title in titles"
            :key="title.id"
            :label="title.name"
            :value="title.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('experts.form.specialties')">
        <el-select
          v-model="form.specialty_ids"
          multiple
          filterable
          collapse-tags
          collapse-tags-tooltip
          style="width: 100%;"
        >
          <el-option
            v-for="option in specialtyOptions"
            :key="option.id"
            :label="option.label"
            :value="option.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('experts.form.appointmentLetters')">
        <el-upload
          class="credential-uploader"
          list-type="picture-card"
          v-model:file-list="credentialFiles"
          :http-request="handleCredentialUpload"
          :on-preview="handleCredentialPreview"
          :on-remove="handleCredentialRemove"
          :auto-upload="true"
          :accept="credentialAccept"
        >
          <el-icon><Plus /></el-icon>
          <template #tip>
            <div class="upload-tip">
              {{ t("experts.form.appointmentLettersTip") }}
            </div>
          </template>
        </el-upload>
      </el-form-item>
      <el-form-item :label="t('experts.form.active')">
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

  <el-dialog v-model="previewVisible" :title="t('experts.form.previewTitle')" width="720px">
    <div v-if="previewUrl" class="preview-body">
      <img v-if="isImagePreview" :src="previewUrl" class="preview-image" />
      <iframe v-else :src="previewUrl" class="preview-frame" />
    </div>
  </el-dialog>

  <el-dialog
    v-model="lettersVisible"
    :title="t('experts.dialog.letters')"
    width="980px"
    top="4vh"
    class="letters-dialog"
  >
    <div v-if="lettersUrls.length === 0" class="muted">
      {{ t("experts.messages.noLetters") }}
    </div>
    <div v-else class="letters-viewer">
      <div
        v-if="lettersImageUrls.length > 0"
        ref="galleryRef"
        class="gallery"
      >
        <div
          class="gallery-main"
          :class="{ dragging: isDragging }"
          @mousedown="handleDragStart"
          @wheel.prevent="handleWheelZoom"
        >
          <img
            :src="activeImageUrl"
            class="gallery-image"
            draggable="false"
            :style="{
              transform: `translate(${panX}px, ${panY}px) scale(${imageScale}) rotate(${imageRotate}deg)`,
            }"
          />
          <div class="gallery-toolbar" @mousedown.stop>
            <div class="gallery-tools">
              <el-button
                circle
                size="small"
                :disabled="lettersImageUrls.length < 2"
                :title="t('experts.actions.prev')"
                @click="goPrev"
              >
                <el-icon><ArrowLeft /></el-icon>
              </el-button>
              <el-button
                circle
                size="small"
                :disabled="lettersImageUrls.length < 2"
                :title="t('experts.actions.next')"
                @click="goNext"
              >
                <el-icon><ArrowRight /></el-icon>
              </el-button>
              <el-button circle size="small" :title="t('experts.actions.zoomIn')" @click="zoomIn">
                <el-icon><ZoomIn /></el-icon>
              </el-button>
              <el-button circle size="small" :title="t('experts.actions.zoomOut')" @click="zoomOut">
                <el-icon><ZoomOut /></el-icon>
              </el-button>
              <el-button circle size="small" :title="t('experts.actions.rotateLeft')" @click="rotateLeft">
                <el-icon><RefreshLeft /></el-icon>
              </el-button>
              <el-button circle size="small" :title="t('experts.actions.rotateRight')" @click="rotateRight">
                <el-icon><RefreshRight /></el-icon>
              </el-button>
              <el-button circle size="small" :title="t('experts.actions.reset')" @click="resetTransform">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
            <div class="gallery-tools">
              <el-button
                circle
                size="small"
                :title="isGalleryFullscreen ? t('experts.actions.exitFullscreen') : t('experts.actions.fullscreen')"
                @click="toggleGalleryFullscreen"
              >
                <el-icon><FullScreen /></el-icon>
              </el-button>
              <el-button
                circle
                size="small"
                :title="t('experts.actions.download')"
                @click="downloadActiveImage"
              >
                <el-icon><Download /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
        <div class="gallery-thumbs">
          <button
            v-for="(url, index) in lettersImageUrls"
            :key="url"
            class="gallery-thumb"
            :class="{ active: index === activeImageIndex }"
            @click="activeImageIndex = index"
          >
            <img :src="url" />
          </button>
        </div>
      </div>
      <div v-if="lettersFileUrls.length > 0" class="letters-files">
        <div v-for="url in lettersFileUrls" :key="url" class="letters-file">
          <el-icon class="letters-icon"><Document /></el-icon>
          <div class="letters-name">{{ fileLabelFromUrl(url) }}</div>
          <el-button link type="primary" @click="openPreviewByUrl(url)">
            {{ t("experts.actions.preview") }}
          </el-button>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import {
  ElMessage,
  ElMessageBox,
  type UploadRequestOptions,
  type UploadUserFile,
} from "element-plus";
import {
  ArrowLeft,
  ArrowRight,
  Document,
  Download,
  FullScreen,
  Plus,
  Refresh,
  RefreshLeft,
  RefreshRight,
  ZoomIn,
  ZoomOut,
} from "@element-plus/icons-vue";
import { useI18n } from "vue-i18n";

import {
  createExpert,
  deleteExpert,
  deleteExperts,
  exportExperts,
  importExperts,
  listExperts,
  updateExpert,
} from "../../services/experts";
import { uploadExpertCredential } from "../../services/uploads";
import { listCategoryTree } from "../../services/categories";
import { listOrganizationsAll } from "../../services/organizations";
import { listRegionsAll } from "../../services/regions";
import { listTitlesAll } from "../../services/titles";
import type {
  CategoryTree,
  Expert,
  Organization,
  Region,
  Title,
} from "../../types/domain";
import { maskIdCard, maskName, maskPhone } from "../../utils/mask";

interface ExpertForm {
  name: string;
  id_card_no: string;
  gender: string;
  phone: string;
  email: string;
  company: string;
  organization_id: number | null;
  region_id: number | null;
  region: string;
  title: string;
  title_id: number | null;
  specialty_ids: number[];
  appointment_letter_urls: string[];
  is_active: boolean;
}

const experts = ref<Expert[]>([]);
const tableRef = ref();
const categoryTree = ref<CategoryTree[]>([]);
const organizations = ref<Organization[]>([]);
const regions = ref<Region[]>([]);
const titles = ref<Title[]>([]);
const loading = ref(false);
const importing = ref(false);
const exporting = ref(false);
const deleting = ref(false);
const selectedIds = ref<number[]>([]);
const keyword = ref("");
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const sortBy = ref<string | undefined>();
const sortOrder = ref<"asc" | "desc" | undefined>();
const { t } = useI18n();

const dialogVisible = ref(false);
const isEditing = ref(false);
const editingId = ref<number | null>(null);
const originalSensitive = ref({ name: "", id_card_no: "", phone: "" });

const form = reactive<ExpertForm>({
  name: "",
  id_card_no: "",
  gender: "",
  phone: "",
  email: "",
  company: "",
  organization_id: null,
  region_id: null,
  region: "",
  title: "",
  title_id: null,
  specialty_ids: [],
  appointment_letter_urls: [],
  is_active: true,
});

const credentialFiles = ref<UploadUserFile[]>([]);
const previewVisible = ref(false);
const previewUrl = ref("");
const lettersVisible = ref(false);
const lettersUrls = ref<string[]>([]);
const activeImageIndex = ref(0);
const galleryRef = ref<HTMLElement | null>(null);
const isGalleryFullscreen = ref(false);
const imageScale = ref(1);
const imageRotate = ref(0);
const panX = ref(0);
const panY = ref(0);
const isDragging = ref(false);
const dragStartX = ref(0);
const dragStartY = ref(0);
const panTargetX = ref(0);
const panTargetY = ref(0);
let panRafId: number | null = null;
const credentialAccept = ".jpg,.jpeg,.png,.webp,.pdf";

const lettersImageUrls = computed(() =>
  lettersUrls.value.filter((url) => isImageFile(url)),
);
const lettersFileUrls = computed(() =>
  lettersUrls.value.filter((url) => !isImageFile(url)),
);
const activeImageUrl = computed(
  () => lettersImageUrls.value[activeImageIndex.value] ?? "",
);

const isImagePreview = computed(() => {
  const url = previewUrl.value.toLowerCase();
  return (
    url.endsWith(".jpg") ||
    url.endsWith(".jpeg") ||
    url.endsWith(".png") ||
    url.endsWith(".webp") ||
    url.endsWith(".gif")
  );
});

const dialogTitle = computed(() =>
  isEditing.value ? t("experts.dialog.edit") : t("experts.dialog.new"),
);

let keywordTimer: number | undefined;

watch(keyword, () => {
  if (keywordTimer) {
    window.clearTimeout(keywordTimer);
  }
  keywordTimer = window.setTimeout(() => {
    page.value = 1;
    refresh();
  }, 300);
});

watch(lettersImageUrls, (urls) => {
  if (activeImageIndex.value >= urls.length) {
    activeImageIndex.value = 0;
  }
  resetTransform();
});

watch(activeImageIndex, () => {
  resetTransform();
});

function resetForm() {
  form.name = "";
  form.id_card_no = "";
  form.gender = "";
  form.phone = "";
  form.email = "";
  form.company = "";
  form.organization_id = null;
  form.region_id = null;
  form.region = "";
  form.title = "";
  form.title_id = null;
  form.specialty_ids = [];
  form.appointment_letter_urls = [];
  form.is_active = true;
  credentialFiles.value = [];
  originalSensitive.value = { name: "", id_card_no: "", phone: "" };
}

function isMasked(value: string) {
  return value.includes("*");
}

function isUnchangedMasked(value: string, original: string) {
  return value === original && isMasked(value);
}

function syncCredentialFiles(urls: string[]) {
  credentialFiles.value = urls.map((url, index) => ({
    name: `credential-${index + 1}`,
    url,
    status: "success",
    uid: `credential-${index + 1}`,
  }));
}

function genderLabel(value?: string | null) {
  if (!value) {
    return "-";
  }
  if (value === "男") {
    return t("experts.gender.male");
  }
  if (value === "女") {
    return t("experts.gender.female");
  }
  return value;
}

function specialtiesLabel(expert: Expert) {
  if (!expert.specialties || expert.specialties.length === 0) {
    return "-";
  }
  return expert.specialties.map((item) => item.name).join("、");
}

async function refresh() {
  loading.value = true;
  try {
    const result = await listExperts({
      page: page.value,
      page_size: pageSize.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
      keyword: keyword.value.trim() || undefined,
    });
    experts.value = result.items;
    total.value = result.total;
    tableRef.value?.clearSelection();
    selectedIds.value = [];
  } finally {
    loading.value = false;
  }
}

async function refreshCategories() {
  categoryTree.value = await listCategoryTree();
}

async function refreshOrganizations() {
  organizations.value = await listOrganizationsAll();
}

async function refreshRegions() {
  regions.value = await listRegionsAll();
}

async function refreshTitles() {
  titles.value = await listTitlesAll();
}


const specialtyOptions = computed(() => {
  const options: { id: number; label: string }[] = [];
  categoryTree.value.forEach((category) => {
    category.subcategories?.forEach((subcategory) => {
      subcategory.specialties?.forEach((specialty) => {
        const labelParts = [
          category.name,
          subcategory.name,
          specialty.code ? `${specialty.code} ${specialty.name}` : specialty.name,
        ];
        options.push({ id: specialty.id, label: labelParts.join(" / ") });
      });
    });
  });
  return options;
});

function handleOrganizationChange() {
  const organization = organizations.value.find(
    (item) => item.id === form.organization_id,
  );
  form.company = organization?.name ?? "";
}

function handleRegionChange() {
  const region = regions.value.find((item) => item.id === form.region_id);
  form.region = region?.name ?? "";
}

function handleTitleChange() {
  const selected = titles.value.find((item) => item.id === form.title_id);
  form.title = selected?.name ?? "";
}

async function handleCredentialUpload(options: UploadRequestOptions) {
  try {
    const result = await uploadExpertCredential(options.file as File);
    const fileUid = (options.file as { uid?: string }).uid;
    const stillExists = fileUid
      ? credentialFiles.value.some((item) => item.uid === fileUid)
      : true;
    if (!stillExists) {
      return;
    }
    credentialFiles.value = credentialFiles.value.map((item) => {
      if (item.uid && item.uid === fileUid) {
        return {
          ...item,
          name: result.filename,
          url: result.url,
          status: "success",
        };
      }
      return item;
    });
    if (!form.appointment_letter_urls.includes(result.url)) {
      form.appointment_letter_urls.push(result.url);
    }
    options.onSuccess?.(result);
  } catch (error) {
    ElMessage.error(t("experts.messages.uploadFailed"));
    options.onError?.(error as Error);
  }
}

function handleCredentialRemove(file: UploadUserFile) {
  if (!file.url) {
    return;
  }
  form.appointment_letter_urls = form.appointment_letter_urls.filter(
    (item) => item !== file.url,
  );
}

function handleCredentialPreview(file: UploadUserFile) {
  if (!file.url) {
    return;
  }
  previewUrl.value = file.url;
  previewVisible.value = true;
}

function isImageFile(url: string) {
  const cleanUrl = url.split("?")[0]?.split("#")[0] ?? url;
  const lower = cleanUrl.toLowerCase();
  return (
    lower.endsWith(".jpg") ||
    lower.endsWith(".jpeg") ||
    lower.endsWith(".png") ||
    lower.endsWith(".webp") ||
    lower.endsWith(".gif")
  );
}

function openPreviewByUrl(url: string) {
  previewUrl.value = url;
  previewVisible.value = true;
}

function fileLabelFromUrl(url: string) {
  const cleanUrl = url.split("?")[0]?.split("#")[0] ?? url;
  const name = cleanUrl.split("/").pop() ?? url;
  try {
    return decodeURIComponent(name);
  } catch {
    return name;
  }
}

function openLetters(expert: Expert) {
  lettersUrls.value = expert.appointment_letter_urls ?? [];
  activeImageIndex.value = 0;
  resetTransform();
  lettersVisible.value = true;
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

function resetTransform() {
  imageScale.value = 1;
  imageRotate.value = 0;
  panX.value = 0;
  panY.value = 0;
  panTargetX.value = 0;
  panTargetY.value = 0;
}

function zoomIn() {
  imageScale.value = clamp(imageScale.value + 0.2, 0.4, 3);
}

function zoomOut() {
  imageScale.value = clamp(imageScale.value - 0.2, 0.4, 3);
}

function rotateLeft() {
  imageRotate.value = (imageRotate.value - 90 + 360) % 360;
}

function rotateRight() {
  imageRotate.value = (imageRotate.value + 90) % 360;
}

function goPrev() {
  const total = lettersImageUrls.value.length;
  if (total === 0) {
    return;
  }
  activeImageIndex.value = (activeImageIndex.value - 1 + total) % total;
}

function goNext() {
  const total = lettersImageUrls.value.length;
  if (total === 0) {
    return;
  }
  activeImageIndex.value = (activeImageIndex.value + 1) % total;
}

function downloadActiveImage() {
  const url = activeImageUrl.value;
  if (!url) {
    return;
  }
  const link = document.createElement("a");
  link.href = url;
  link.download = fileLabelFromUrl(url);
  link.click();
}

function handleDragStart(event: MouseEvent) {
  if (event.button !== 0) {
    return;
  }
  const target = event.target as HTMLElement | null;
  if (target?.closest(".gallery-toolbar")) {
    return;
  }
  event.preventDefault();
  isDragging.value = true;
  dragStartX.value = event.clientX - panX.value;
  dragStartY.value = event.clientY - panY.value;
  panTargetX.value = panX.value;
  panTargetY.value = panY.value;
  window.addEventListener("mousemove", handleDragMove);
  window.addEventListener("mouseup", handleDragEnd);
}

function handleDragMove(event: MouseEvent) {
  if (!isDragging.value) {
    return;
  }
  panTargetX.value = event.clientX - dragStartX.value;
  panTargetY.value = event.clientY - dragStartY.value;
  if (panRafId === null) {
    panRafId = window.requestAnimationFrame(() => {
      panX.value = panTargetX.value;
      panY.value = panTargetY.value;
      panRafId = null;
    });
  }
}

function handleDragEnd() {
  if (!isDragging.value) {
    return;
  }
  isDragging.value = false;
  if (panRafId !== null) {
    window.cancelAnimationFrame(panRafId);
    panRafId = null;
    panX.value = panTargetX.value;
    panY.value = panTargetY.value;
  }
  window.removeEventListener("mousemove", handleDragMove);
  window.removeEventListener("mouseup", handleDragEnd);
}

function handleWheelZoom(event: WheelEvent) {
  if (event.deltaY < 0) {
    zoomIn();
  } else {
    zoomOut();
  }
}

async function toggleGalleryFullscreen() {
  const target = galleryRef.value;
  if (!target) {
    return;
  }
  if (document.fullscreenElement === target) {
    await document.exitFullscreen();
  } else {
    await target.requestFullscreen();
  }
}

function handleFullscreenChange() {
  isGalleryFullscreen.value = document.fullscreenElement === galleryRef.value;
}


function resolveOrganizationId(expert: Expert): number | null {
  if (expert.organization_id) {
    return expert.organization_id;
  }
  if (!expert.company) {
    return null;
  }
  return organizations.value.find((item) => item.name === expert.company)?.id ?? null;
}

function resolveTitleId(expert: Expert): number | null {
  if (expert.title_id) {
    return expert.title_id;
  }
  if (!expert.title) {
    return null;
  }
  return titles.value.find((item) => item.name === expert.title)?.id ?? null;
}

function resolveRegionId(expert: Expert): number | null {
  if (expert.region_id) {
    return expert.region_id;
  }
  if (!expert.region) {
    return null;
  }
  return regions.value.find((item) => item.name === expert.region)?.id ?? null;
}

function openCreate() {
  resetForm();
  isEditing.value = false;
  editingId.value = null;
  dialogVisible.value = true;
}

function openEdit(expert: Expert) {
  isEditing.value = true;
  editingId.value = expert.id;
  form.name = expert.name;
  form.id_card_no = expert.id_card_no ?? "";
  form.gender = expert.gender ?? "";
  form.phone = expert.phone ?? "";
  form.email = expert.email ?? "";
  form.organization_id = resolveOrganizationId(expert);
  form.region_id = resolveRegionId(expert);
  form.title_id = resolveTitleId(expert);
  form.company = expert.company ?? "";
  form.region = expert.region ?? "";
  form.title = expert.title ?? "";
  form.specialty_ids =
    expert.specialty_ids ??
    expert.specialties?.map((item) => item.id) ??
    [];
  form.appointment_letter_urls = expert.appointment_letter_urls ?? [];
  syncCredentialFiles(form.appointment_letter_urls);
  form.is_active = expert.is_active;
  originalSensitive.value = {
    name: expert.name ?? "",
    id_card_no: expert.id_card_no ?? "",
    phone: expert.phone ?? "",
  };
  dialogVisible.value = true;
}

async function submitForm() {
  const trimmedIdCard = form.id_card_no.trim();
  const trimmedName = form.name.trim();
  const idCardUnchanged = isUnchangedMasked(
    trimmedIdCard,
    originalSensitive.value.id_card_no,
  );
  const nameUnchanged = isUnchangedMasked(
    trimmedName,
    originalSensitive.value.name,
  );
  if (!isEditing.value) {
    if (!trimmedIdCard) {
      ElMessage.error(t("experts.messages.idCardRequired"));
      return;
    }
    if (!trimmedName) {
      ElMessage.error(t("experts.messages.nameRequired"));
      return;
    }
  } else {
    if (!idCardUnchanged && !trimmedIdCard) {
      ElMessage.error(t("experts.messages.idCardRequired"));
      return;
    }
    if (!nameUnchanged && !trimmedName) {
      ElMessage.error(t("experts.messages.nameRequired"));
      return;
    }
  }
  try {
    if (isEditing.value && editingId.value) {
      const payload: Record<string, unknown> = {
        gender: form.gender,
        email: form.email,
        company: form.organization_id ? form.company : null,
        organization_id: form.organization_id,
        region_id: form.region_id,
        region: form.region || null,
        title: form.title_id ? form.title : null,
        title_id: form.title_id,
        specialty_ids: form.specialty_ids,
        appointment_letter_urls: form.appointment_letter_urls,
        is_active: form.is_active,
      };
      if (!nameUnchanged) {
        payload.name = form.name || null;
      }
      if (!idCardUnchanged) {
        payload.id_card_no = form.id_card_no || null;
      }
      const phoneUnchanged = isUnchangedMasked(
        form.phone.trim(),
        originalSensitive.value.phone,
      );
      if (!phoneUnchanged) {
        payload.phone = form.phone || null;
      }
      await updateExpert(editingId.value, payload);
      ElMessage.success(t("experts.messages.updated"));
    } else {
      await createExpert({
        name: form.name,
        id_card_no: form.id_card_no || null,
        gender: form.gender,
        phone: form.phone,
        email: form.email,
        company: form.organization_id ? form.company : null,
        organization_id: form.organization_id,
        region_id: form.region_id,
        region: form.region || null,
        title: form.title_id ? form.title : null,
        title_id: form.title_id,
        specialty_ids: form.specialty_ids,
        appointment_letter_urls: form.appointment_letter_urls,
        is_active: form.is_active,
      });
      ElMessage.success(t("experts.messages.created"));
    }
    dialogVisible.value = false;
    await refresh();
  } catch (error) {
    ElMessage.error(t("experts.messages.opFailed"));
  }
}

async function confirmDelete(expert: Expert) {
  try {
    await ElMessageBox.confirm(
      t("experts.messages.deleteConfirm", { name: maskName(expert.name) }),
      t("common.confirm"),
      { type: "warning" },
    );
  } catch {
    return;
  }
  await deleteExpert(expert.id);
  ElMessage.success(t("experts.messages.deleted"));
  await refresh();
}

function handleSelectionChange(rows: Expert[]) {
  selectedIds.value = rows.map((item) => item.id);
}

async function handleBatchDelete() {
  if (selectedIds.value.length === 0) {
    return;
  }
  try {
    await ElMessageBox.confirm(
      t("experts.messages.batchDeleteConfirm", { count: selectedIds.value.length }),
      t("common.confirm"),
      { type: "warning" },
    );
  } catch {
    return;
  }
  deleting.value = true;
  try {
    const result = await deleteExperts(selectedIds.value);
    ElMessage.success(
      t("experts.messages.batchDeleteSuccess", {
        deleted: result.deleted,
        skipped: result.skipped,
      }),
    );
    await refresh();
  } catch (error) {
    ElMessage.error(t("experts.messages.batchDeleteFailed"));
  } finally {
    deleting.value = false;
  }
}

async function handleImport(options: UploadRequestOptions) {
  importing.value = true;
  try {
    const result = await importExperts(options.file as File);
    ElMessage.success(
      t("experts.messages.importSuccess", {
        created: result.created,
        skipped: result.skipped,
      }),
    );
    await refresh();
    options.onSuccess?.(result);
  } catch (error) {
    ElMessage.error(t("experts.messages.importFailed"));
    options.onError?.(error as Error);
  } finally {
    importing.value = false;
  }
}

async function handleExport() {
  exporting.value = true;
  try {
    const blob = await exportExperts();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "experts_export.xlsx";
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    ElMessage.error(t("experts.messages.exportFailed"));
  } finally {
    exporting.value = false;
  }
}

onMounted(async () => {
  document.addEventListener("fullscreenchange", handleFullscreenChange);
  await Promise.all([
    refresh(),
    refreshCategories(),
    refreshOrganizations(),
    refreshRegions(),
    refreshTitles(),
  ]);
});

onBeforeUnmount(() => {
  document.removeEventListener("fullscreenchange", handleFullscreenChange);
  window.removeEventListener("mousemove", handleDragMove);
  window.removeEventListener("mouseup", handleDragEnd);
  if (panRafId !== null) {
    window.cancelAnimationFrame(panRafId);
    panRafId = null;
  }
});

function handleSortChange({
  prop,
  order,
}: {
  prop?: string;
  order?: "ascending" | "descending" | null;
}) {
  if (!prop || !order) {
    sortBy.value = undefined;
    sortOrder.value = undefined;
  } else {
    sortBy.value = prop;
    sortOrder.value = order === "ascending" ? "asc" : "desc";
  }
  page.value = 1;
  refresh();
}

function handlePageChange(value: number) {
  page.value = value;
  refresh();
}

function handlePageSizeChange(value: number) {
  pageSize.value = value;
  page.value = 1;
  refresh();
}
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

.muted {
  color: #9aa3b2;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.credential-uploader :deep(.el-upload--picture-card) {
  border-radius: 6px;
}

.upload-tip {
  margin-top: 6px;
  font-size: 12px;
  color: #8b97a7;
}

.preview-body {
  display: flex;
  justify-content: center;
  align-items: center;
}

.preview-image {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
}

.preview-frame {
  width: 100%;
  height: 70vh;
  border: none;
}

.letters-viewer {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.letters-dialog :deep(.el-dialog__body) {
  max-height: 88vh;
  overflow: auto;
}

.gallery {
  border: 1px solid var(--gov-border);
  border-radius: 8px;
  padding: 12px;
  background: #f8fafe;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.6);
}

.gallery-main {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 70vh;
  background: #f5f7fb;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--gov-border);
  cursor: grab;
  user-select: none;
}

.gallery-main:active {
  cursor: grabbing;
}

.gallery-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transition: transform 0.2s ease;
  will-change: transform;
}

.gallery-main.dragging .gallery-image {
  transition: none;
}

.gallery-toolbar {
  position: absolute;
  left: 50%;
  bottom: 12px;
  transform: translateX(-50%);
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 6px 10px;
  border-radius: 6px;
  background: rgba(17, 25, 40, 0.6);
  border: 1px solid var(--gov-border);
  box-shadow: 0 6px 16px rgba(12, 18, 28, 0.18);
  backdrop-filter: blur(6px);
}

.gallery-tools {
  display: flex;
  align-items: center;
  gap: 6px;
}

.gallery-toolbar :deep(.el-button) {
  background: rgba(255, 255, 255, 0.85);
  border-color: transparent;
}

.gallery-toolbar :deep(.el-button:hover) {
  background: #ffffff;
}

.gallery-thumbs {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.gallery-thumb {
  width: 64px;
  height: 64px;
  border: 1px solid var(--gov-border);
  border-radius: 6px;
  padding: 0;
  background: #fff;
  cursor: pointer;
}

.gallery-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
}

.gallery-thumb.active {
  border-color: var(--gov-blue-500);
  box-shadow: 0 0 0 2px rgba(46, 113, 195, 0.15);
}

.letters-files {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.letters-file {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--gov-border);
  border-radius: 6px;
  padding: 8px 10px;
  background: #fff;
}

.letters-icon {
  font-size: 20px;
  color: var(--gov-blue-600);
}

.letters-name {
  flex: 1;
  font-size: 12px;
  color: #5b6573;
  word-break: break-all;
}

.gallery:fullscreen {
  padding: 24px;
  border-radius: 0;
  background: rgba(10, 16, 26, 0.78);
  backdrop-filter: blur(2px);
}

.gallery:fullscreen .gallery-main {
  height: calc(100vh - 200px);
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.2);
}

.gallery:fullscreen .gallery-thumbs {
  display: none;
}
</style>
