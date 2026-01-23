<template>
  <div class="register-page">
    <div class="register-shell">
      <section class="hero-panel">
        <div class="hero-header">
          <div class="hero-badge">
            <span>{{ t("expertRegister.instructions.title") }}</span>
          </div>
          <h1 class="hero-title">{{ t("expertRegister.title") }}</h1>
          <p class="hero-subtitle">{{ t("expertRegister.subtitle") }}</p>
          <p class="hero-note">{{ t("expertRegister.instructions.subtitle") }}</p>
        </div>
        <div class="hero-highlights">
          <div class="highlight-card">
            <div class="highlight-title">
              {{ t("expertRegister.instructions.points.requiredTitle") }}
            </div>
            <div class="highlight-text">
              {{ t("expertRegister.instructions.points.requiredText") }}
            </div>
          </div>
          <div class="highlight-card">
            <div class="highlight-title">
              {{ t("expertRegister.instructions.points.selectTitle") }}
            </div>
            <div class="highlight-text">
              {{ t("expertRegister.instructions.points.selectText") }}
            </div>
          </div>
        </div>
        <div class="hero-footer">
          <div class="hero-footer-item">
            <span class="dot"></span>
            <span>{{ t("expertRegister.tips.letters") }}</span>
          </div>
        </div>
      </section>

      <section class="form-panel">
        <div class="form-header">
          <h2>{{ t("expertRegister.sections.basic") }}</h2>
          <p>{{ t("expertRegister.note") }}</p>
        </div>

        <div v-if="submitted" class="success-panel">
          <el-result
            icon="success"
            :title="t('expertRegister.success.title')"
            :sub-title="t('expertRegister.success.description')"
          />
          <div class="success-status">{{ t("expertRegister.success.status") }}</div>
          <el-button type="primary" @click="handleNew">
            {{ t("expertRegister.actions.new") }}
          </el-button>
        </div>

        <el-form
          v-else
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          class="register-form"
          v-loading="loadingMeta"
        >
          <div class="section-title">
            <span>{{ t("expertRegister.sections.basic") }}</span>
          </div>
          <el-form-item :label="t('experts.form.name')" prop="name" required>
            <el-input
              v-model="form.name"
              :placeholder="t('expertRegister.placeholders.name')"
            />
          </el-form-item>
          <el-form-item :label="t('experts.form.idCard')" prop="id_card_no" required>
            <el-input
              v-model="form.id_card_no"
              :placeholder="t('expertRegister.placeholders.idCard')"
            />
          </el-form-item>
          <el-form-item :label="t('experts.form.gender')">
            <el-radio-group v-model="form.gender">
              <el-radio-button label="male">
                {{ t("experts.gender.male") }}
              </el-radio-button>
              <el-radio-button label="female">
                {{ t("experts.gender.female") }}
              </el-radio-button>
            </el-radio-group>
          </el-form-item>

          <div class="section-title">
            <span>{{ t("expertRegister.sections.contact") }}</span>
          </div>
          <el-form-item :label="t('experts.form.phone')" prop="phone" required>
            <el-input
              v-model="form.phone"
              :placeholder="t('expertRegister.placeholders.phone')"
            />
          </el-form-item>

          <div class="section-title">
            <span>{{ t("expertRegister.sections.professional") }}</span>
          </div>
          <el-form-item :label="t('experts.form.company')">
            <el-select
              v-model="companyValue"
              filterable
              allow-create
              default-first-option
              clearable
              :placeholder="t('expertRegister.placeholders.company')"
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
              v-model="regionValue"
              filterable
              clearable
              :placeholder="t('expertRegister.placeholders.region')"
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
              v-model="titleValue"
              filterable
              clearable
              :placeholder="t('expertRegister.placeholders.title')"
            >
              <el-option
                v-for="title in titleOptions"
                :key="title.id"
                :label="title.label"
                :value="title.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('experts.form.specialties')">
            <el-tree-select
              v-model="form.specialty_ids"
              :data="specialtyTreeOptions"
              :props="treeProps"
              multiple
              filterable
              check-strictly
              collapse-tags
              collapse-tags-tooltip
              :placeholder="t('expertRegister.placeholders.specialty')"
            />
          </el-form-item>

          <div class="section-title">
            <span>{{ t("expertRegister.sections.credentials") }}</span>
          </div>
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

          <div class="form-actions">
            <el-button @click="handleReset">
              {{ t("expertRegister.actions.reset") }}
            </el-button>
            <el-button type="primary" :loading="submitting" @click="handleSubmit">
              {{ t("expertRegister.actions.submit") }}
            </el-button>
          </div>
        </el-form>
      </section>
    </div>

    <el-dialog v-model="previewVisible" :title="t('experts.form.previewTitle')" width="720px">
      <div v-if="previewUrl" class="preview-body">
        <img v-if="isImagePreview" :src="previewUrl" class="preview-image" />
        <iframe v-else :src="previewUrl" class="preview-frame" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import {
  ElMessage,
  type FormInstance,
  type FormRules,
  type UploadRequestOptions,
  type UploadUserFile,
} from "element-plus";
import { Plus } from "@element-plus/icons-vue";
import { useI18n } from "vue-i18n";

import { fetchExpertPublicMetadata, submitExpertPublicRegistration } from "../services/public";
import { uploadExpertCredentialPublic } from "../services/uploads";
import type { Category, ExpertPublicCreate, Organization, Region, Title } from "../types/domain";
import { resolveErrorMessage } from "../utils/errors";

interface TreeSource {
  id: number;
  name: string;
  code?: string | null;
  is_active?: boolean;
  children?: TreeSource[];
}

interface TreeOption {
  id: number;
  label: string;
  is_leaf: boolean;
  children?: TreeOption[];
}

interface SelectOption {
  id: number;
  label: string;
  name: string;
}

const { t } = useI18n();
const formRef = ref<FormInstance>();
const loadingMeta = ref(false);
const submitting = ref(false);
const submitted = ref(false);

const organizations = ref<Organization[]>([]);
const regions = ref<Region[]>([]);
const titleTree = ref<Title[]>([]);
const specialtyTree = ref<Category[]>([]);
const companyValue = ref<string | number | null>(null);
const regionValue = ref<string | number | null>(null);
const titleValue = ref<string | number | null>(null);

const form = reactive<ExpertPublicCreate>({
  name: "",
  id_card_no: "",
  gender: "",
  phone: "",
  company: "",
  organization_id: null,
  region_id: null,
  region: "",
  title: "",
  title_id: null,
  specialty_ids: [],
  appointment_letter_urls: [],
});

const rules: FormRules = {
  name: [
    { required: true, message: t("experts.messages.nameRequired"), trigger: "blur" },
  ],
  id_card_no: [
    { required: true, message: t("experts.messages.idCardRequired"), trigger: "blur" },
  ],
  phone: [
    { required: true, message: t("experts.messages.phoneRequired"), trigger: "blur" },
  ],
};

const credentialFiles = ref<UploadUserFile[]>([]);
const previewVisible = ref(false);
const previewUrl = ref("");
const credentialAccept = ".jpg,.jpeg,.png,.webp,.pdf";

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

const treeProps = {
  value: "id",
  label: "label",
  children: "children",
  disabled: (data: TreeOption) => !data.is_leaf,
};

function buildTreeOptions(nodes: TreeSource[]): TreeOption[] {
  const result: TreeOption[] = [];
  (nodes ?? []).forEach((node) => {
    const children = buildTreeOptions(node.children ?? []);
    const isActive = node.is_active !== false;
    if (!isActive && children.length === 0) {
      return;
    }
    result.push({
      id: node.id,
      label: node.code ? `${node.code} ${node.name}` : node.name,
      is_leaf: children.length === 0,
      children: children.length > 0 ? children : undefined,
    });
  });
  return result;
}

function collectLeafNodes<T extends TreeSource>(nodes: T[]): T[] {
  const result: T[] = [];
  nodes.forEach((node) => {
    const children = node.children ?? [];
    if (children.length === 0) {
      result.push(node);
      return;
    }
    result.push(...collectLeafNodes(children as T[]));
  });
  return result;
}

const specialtyTreeOptions = computed<TreeOption[]>(() =>
  buildTreeOptions(specialtyTree.value),
);

const titleOptions = computed<SelectOption[]>(() => {
  const leafNodes = collectLeafNodes(titleTree.value).filter(
    (item) => item.is_active !== false,
  );
  return leafNodes.map((item) => ({
    id: item.id,
    label: item.code ? `${item.code} ${item.name}` : item.name,
    name: item.name,
  }));
});

watch(companyValue, (value) => {
  if (typeof value === "number") {
    const selected = organizations.value.find((item) => item.id === value);
    form.organization_id = value;
    form.company = selected?.name ?? "";
    return;
  }
  if (typeof value === "string") {
    form.organization_id = null;
    form.company = value.trim();
    return;
  }
  form.organization_id = null;
  form.company = "";
});

watch(regionValue, (value) => {
  if (typeof value === "number") {
    const selected = regions.value.find((item) => item.id === value);
    form.region_id = value;
    form.region = selected?.name ?? "";
    return;
  }
  if (typeof value === "string") {
    form.region_id = null;
    form.region = value.trim();
    return;
  }
  form.region_id = null;
  form.region = "";
});

watch(titleValue, (value) => {
  if (typeof value === "number") {
    const selected = titleOptions.value.find((item) => item.id === value);
    form.title_id = value;
    form.title = selected?.name ?? "";
    return;
  }
  if (typeof value === "string") {
    form.title_id = null;
    form.title = value.trim();
    return;
  }
  form.title_id = null;
  form.title = "";
});

async function loadMetadata() {
  loadingMeta.value = true;
  try {
    const data = await fetchExpertPublicMetadata();
    organizations.value = (data.organizations ?? []).filter(
      (item) => item.is_active,
    );
    regions.value = (data.regions ?? []).filter((item) => item.is_active);
    titleTree.value = data.titles ?? [];
    specialtyTree.value = data.specialties ?? [];
  } catch (error) {
    ElMessage.error(t("expertRegister.messages.loadFailed"));
  } finally {
    loadingMeta.value = false;
  }
}

async function handleCredentialUpload(options: UploadRequestOptions) {
  try {
    const result = await uploadExpertCredentialPublic(options.file as File);
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
    if (!form.appointment_letter_urls?.includes(result.url)) {
      form.appointment_letter_urls = [
        ...(form.appointment_letter_urls ?? []),
        result.url,
      ];
    }
    options.onSuccess?.(result);
  } catch (error) {
    ElMessage.error(t("expertRegister.messages.uploadFailed"));
    options.onError?.(error as Error);
  }
}

function handleCredentialRemove(file: UploadUserFile) {
  if (!file.url) {
    return;
  }
  form.appointment_letter_urls = (form.appointment_letter_urls ?? []).filter(
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

async function handleSubmit() {
  if (!formRef.value) {
    return;
  }
  const valid = await formRef.value.validate().catch(() => false);
  if (!valid) {
    ElMessage.error(t("expertRegister.messages.formInvalid"));
    return;
  }
  submitting.value = true;
  try {
    await submitExpertPublicRegistration({
      name: form.name,
      id_card_no: form.id_card_no,
      gender: form.gender || null,
      phone: form.phone.trim(),
      company: form.company || null,
      organization_id: form.organization_id,
      region_id: form.region_id,
      region: form.region || null,
      title: form.title || null,
      title_id: form.title_id,
      specialty_ids: form.specialty_ids ?? [],
      appointment_letter_urls: form.appointment_letter_urls ?? [],
    });
    submitted.value = true;
  } catch (error) {
    ElMessage.error(
      resolveErrorMessage(
        error,
        t("expertRegister.messages.submitFailed"),
        translateExpertDetail,
      ),
    );
  } finally {
    submitting.value = false;
  }
}

function translateExpertDetail(detail: string) {
  switch (detail) {
    case "ID card already exists":
      return t("experts.messages.idCardExists");
    case "Phone already exists":
      return t("experts.messages.phoneExists");
    case "ID card is required":
      return t("experts.messages.idCardRequired");
    case "Phone is required":
      return t("experts.messages.phoneRequired");
    default:
      return null;
  }
}

function handleReset() {
  formRef.value?.resetFields();
  companyValue.value = null;
  regionValue.value = null;
  titleValue.value = null;
  form.company = "";
  form.organization_id = null;
  form.region = "";
  form.region_id = null;
  form.title = "";
  form.title_id = null;
  form.specialty_ids = [];
  form.appointment_letter_urls = [];
  credentialFiles.value = [];
}

function handleNew() {
  submitted.value = false;
  handleReset();
}

onMounted(loadMetadata);
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  padding: clamp(18px, 3vw, 36px);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.register-page::before {
  content: "";
  position: absolute;
  width: 420px;
  height: 420px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(63, 134, 192, 0.18), transparent 70%);
  top: -160px;
  right: -120px;
  filter: blur(2px);
}

.register-page::after {
  content: "";
  position: absolute;
  width: 320px;
  height: 320px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(212, 179, 91, 0.18), transparent 70%);
  bottom: -160px;
  left: -120px;
  filter: blur(2px);
}

.register-shell {
  width: min(1120px, 100%);
  display: grid;
  grid-template-columns: minmax(260px, 0.95fr) minmax(320px, 1.25fr);
  gap: 28px;
  position: relative;
  z-index: 1;
}

.hero-panel {
  background: linear-gradient(165deg, #15385f 0%, #1f4f82 55%, #2f6fa5 100%);
  border-radius: 18px;
  color: #f5f8fc;
  padding: clamp(20px, 3vw, 36px);
  box-shadow: 0 18px 32px rgba(10, 18, 32, 0.2);
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  font-size: 12px;
  letter-spacing: 0.4px;
}

.hero-title {
  font-size: clamp(24px, 3vw, 34px);
  margin: 10px 0 4px;
  color: #ffffff;
}

.hero-subtitle {
  font-size: 14px;
  margin: 0;
  color: rgba(255, 255, 255, 0.78);
}

.hero-note {
  font-size: 13px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
}

.hero-highlights {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.highlight-card {
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.16);
}

.highlight-title {
  font-weight: 600;
  font-size: 13px;
  margin-bottom: 6px;
}

.highlight-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.hero-footer {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.hero-footer-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.hero-footer .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #d4b35b;
  box-shadow: 0 0 0 4px rgba(212, 179, 91, 0.2);
}

.form-panel {
  background: var(--gov-card);
  border-radius: 18px;
  border: 1px solid var(--gov-border);
  box-shadow: var(--gov-shadow);
  padding: clamp(20px, 3vw, 36px);
}

.form-header h2 {
  margin: 0;
  font-size: 20px;
}

.form-header p {
  margin: 6px 0 0;
  color: var(--gov-muted);
  font-size: 13px;
}

.section-title {
  margin: 16px 0 6px;
  font-weight: 600;
  color: #233b57;
  letter-spacing: 0.2px;
}

.register-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.credential-uploader :deep(.el-upload--picture-card) {
  border-radius: 10px;
}

.upload-tip {
  margin-top: 6px;
  font-size: 12px;
  color: #8b97a7;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 8px;
}

.success-panel {
  text-align: center;
  padding: 18px 0 6px;
}

.success-status {
  margin: 12px 0 18px;
  font-size: 13px;
  color: var(--gov-muted);
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

@media (max-width: 960px) {
  .register-shell {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column-reverse;
    align-items: stretch;
  }
}

@media (max-width: 600px) {
  .hero-panel {
    border-radius: 14px;
  }

  .form-panel {
    border-radius: 14px;
  }
}
</style>
