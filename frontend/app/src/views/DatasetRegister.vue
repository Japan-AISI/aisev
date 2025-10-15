<template>
  <div class="container-bg">
    <Header :breadcrumbs="breadcrumbs" />
    <div class="container">
      <h2>{{ $t("datasetRegister") }}</h2>
      <div class="main-content card">
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label class="form-label" for="datasetName">{{
              $t("datasetName")
            }}</label>
            <input
              id="datasetName"
              v-model="datasetName"
              type="text"
              required
            />
          </div>
          <div class="form-group">
            <label class="form-label" for="fileUpload">{{
              $t("csvFileUpload")
            }}</label>
            <input
              id="fileUpload"
              type="file"
              accept=".csv,.parquet"
              @change="handleFileChange"
              required
            />
          </div>
          <div class="form-group">
            <label class="form-label">
              <input type="checkbox" v-model="inputAspect" />
              {{ $t("inputAspectInfo") }}
            </label>
          </div>
          <!-- 10 Perspectives Add checkboxes are not deleted, but checkboxes and radio buttons for preset data are added below them -->
          <!-- div class="form-group">
            <label class="form-label">
              <input type="checkbox" v-model="acPresetEnable" />
              {{ $t("registerACPreset") }}
            </label>
          </div>
          <div class="form-group" v-if="acPresetEnable">
            <label class="form-label">{{ $t("selectACPresetType") }}</label>
            <div>
              <label>
                <input type="radio" value="test" v-model="acPresetType" /> test
              </label>
              <label style="margin-left: 1em">
                <input type="radio" value="dev" v-model="acPresetType" /> dev
              </label>
            </div>
          </div -->
          <div v-if="inputAspect" class="form-group">
            <label class="form-label" for="aspectSelect">{{
              $t("selectAspect")
            }}</label>
            <select id="aspectSelect" v-model="selectedAspect">
              <option v-for="aspect in aspects" :key="aspect" :value="aspect">
                {{ aspect }}
              </option>
            </select>
          </div>
          <button type="submit" class="regist-btn" style="margin-top: 1.5rem">
            {{ $t("register") }}
          </button>
        </form>
        <div v-if="uploadResult" class="upload-result">
          {{ uploadResult }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useI18n } from "vue-i18n";
import Header from "../components/Header.vue";
import Papa from "papaparse";
import {
  getPerspectiveListByLocale,
  toEnglishPerspective,
  toJapanesePerspective,
} from "../utils/perspectiveMapping";

const { t, locale } = useI18n();

const breadcrumbs = [
  { label: "home", link: "/" },
  { label: "evaluationDefinerHomeTitle", link: "/definer-home" },
  { label: "datasetRegister" },
];
// i18n support: Switch viewpoint list by language
const aspects = computed(() => getPerspectiveListByLocale(locale.value));
const datasetName = ref("");
const inputAspect = ref(false);
const acPresetType = ref("");
const selectedAspect = ref("");
watch(
  () => locale.value,
  (newLocale, oldLocale) => {
    if (!selectedAspect.value) return;
    if (newLocale.startsWith("en")) {
      selectedAspect.value = toEnglishPerspective(selectedAspect.value);
    } else {
      selectedAspect.value = toJapanesePerspective(selectedAspect.value);
    }
  }
);
const file = ref<File | null>(null);
const uploadResult = ref("");
const acPresetEnable = ref(false);

function handleFileChange(e: Event) {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    file.value = target.files[0];
    const selectedFile = target.files[0];
    if (selectedFile.name.endsWith(".csv")) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const text = event.target?.result as string;
        const parsed = Papa.parse(text, { header: true });
        const previewRows = parsed.data.slice(0, 5);
        console.log("Preview first 5 rows:", previewRows);
      };
      reader.readAsText(selectedFile);
    } else if (selectedFile.name.endsWith(".parquet")) {
      (async () => {
        const buffer = await selectedFile.arrayBuffer();
        const parquet = await import(
          "https://cdn.jsdelivr.net/npm/parquet-wasm@0.6.1/esm/+esm"
        );
        await parquet.default();
        const wasmTable = parquet.readParquet(new Uint8Array(buffer));
        const arrow = await import(
          "https://cdn.jsdelivr.net/npm/apache-arrow@13/+esm"
        );
        const table = arrow.tableFromIPC(wasmTable.intoIPCStream());
        const rows = table.toArray().map((r: any) => ({ ...r }));
        const previewRows = rows.slice(0, 5);
        console.log("Preview first 5 rows:", previewRows);
        wasmTable.drop?.();
      })();
    }
  }
}

async function handleSubmit() {
  if (!file.value) {
    uploadResult.value = t("pleaseSelectFile");
    return;
  }

  let fileToSend = file.value;
  let uploadData = [];
  if (file.value.name.endsWith(".parquet")) {
    const buffer = await file.value.arrayBuffer();
    const parquet = await import(
      "https://cdn.jsdelivr.net/npm/parquet-wasm@0.6.1/esm/+esm"
    );
    await parquet.default();
    const wasmTable = parquet.readParquet(new Uint8Array(buffer));
    const arrow = await import(
      "https://cdn.jsdelivr.net/npm/apache-arrow@13/+esm"
    );
    const table = arrow.tableFromIPC(wasmTable.intoIPCStream());
    uploadData = table.toArray().map((r: any) => ({ ...r }));
    wasmTable.drop?.();
  } else {
    const reader = new FileReader();
    const readPromise = new Promise<string>((resolve) => {
      reader.onload = (event) => {
        resolve(event.target?.result as string);
      };
      reader.readAsText(file.value as File);
    });
    const csvText = await readPromise;
    const parsed = Papa.parse(csvText, { header: true });
    uploadData = parsed.data;
  }

  // Perform ID merging only when acPresetEnable is true
  let mergedData = [];
  if (acPresetEnable.value) {
    let presetCsvPath = "";
    if (acPresetType.value === "dev") {
      presetCsvPath = "/src/assets/extracted_ID_and_perspective_dev.csv";
    } else if (acPresetType.value === "test") {
      presetCsvPath = "/src/assets/extracted_ID_and_perspective_test.csv";
    }
    try {
      const presetCsvRes = await fetch(presetCsvPath);
      const presetCsvText = await presetCsvRes.text();
      const presetCsvParsed = Papa.parse(presetCsvText, { header: true });
      console.log(`${presetCsvPath} 内容:`, presetCsvParsed.data);
      mergedData = uploadData.map((row: any) => {
        const match = presetCsvParsed.data.find(
          (testRow: any) => String(testRow.ID) === String(row.ID)
        );
        // Copy the value when ID matches, add blank when it does not match
        return {
          ...row,
          ten_perspective: match ? match.ten_perspective : "",
          gsn_perspective: match ? match.gsn_perspective : "",
        };
      });
      console.log("ID一致でマージしたデータ:", mergedData);
    } catch (e) {
      console.error(`${presetCsvPath} 読み込み/マージ失敗:`, e);
      mergedData = uploadData;
    }
  } else {
    mergedData = uploadData;
  }

  // If inputAspect is true, add selectedAspect to each row
  // and if "ten_perspective" is now already present, no need to add it
  const existTenPerspective = mergedData.some(
    (row: any) => row.ten_perspective !== undefined
  );
  if (inputAspect.value && selectedAspect.value && !existTenPerspective) {
    console.log("Adding aspect to each row:", selectedAspect.value);

    const japaneseAspect =
      toJapanesePerspective(selectedAspect.value) || selectedAspect.value;

    mergedData = mergedData.map((row: any) => ({
      ...row,
      ten_perspective: japaneseAspect,
    }));

    // If "ID" is not present, add it
    if (!mergedData.some((row: any) => row.ID !== undefined)) {
      mergedData = mergedData.map((row: any, index: number) => ({
        ...row,
        ID: "ID-" + (index + 1),
      }));
    }

    // If "meta" is not present, add it
    if (!mergedData.some((row: any) => row.meta !== undefined)) {
      mergedData = mergedData.map((row: any) => ({
        ...row,
        meta: "no_meta",
      }));
    }

    // If "meta-mlmc" is not present, add it
    if (!mergedData.some((row: any) => row["meta-mlmc"] !== undefined)) {
      mergedData = mergedData.map((row: any) => ({
        ...row,
        "meta-mlmc": "no_meta",
      }));
    }

    // replaceNaN
    mergedData = mergedData.map((row: any) => {
      Object.keys(row).forEach((key) => {
        if (row[key] === null || row[key] === undefined || row[key] === "") {
          row[key] = "NaN";
        }
      });
      return row;
    });
  }

  // Normalize ten_perspective column values to Japanese labels
  mergedData = mergedData.map((row: any) => {
    if (
      typeof row.ten_perspective === "string" &&
      row.ten_perspective.trim() !== ""
    ) {
      return {
        ...row,
        ten_perspective: toJapanesePerspective(row.ten_perspective) ||
          row.ten_perspective,
      };
    }
    return row;
  });

  // Send merged data to API
  const mergedCsv = Papa.unparse(mergedData);
  const mergedBlob = new Blob([mergedCsv], { type: "text/csv" });
  const mergedFile = new File(
    [mergedBlob],
    file.value.name.replace(/\.(csv|parquet)$/, "_merged.csv"),
    { type: "text/csv" }
  );

  const formData = new FormData();
  formData.append("file", mergedFile);
  formData.append("datasetName", datasetName.value);
  if (inputAspect.value) {
    formData.append(
      "aspect",
      toJapanesePerspective(selectedAspect.value) || selectedAspect.value
    );
  }

  // API Destination Branching
  let apiUrl = "http://localhost:8000/datasets/register";
  if (acPresetEnable.value) {
    apiUrl = "http://localhost:8000/datasets/register/gsn";
  }
  console.log("apiUrl", apiUrl);

  // Preview before sending
  console.log("送信前プレビュー（最初の5行）:", mergedData.slice(0, 5));
  console.log("formData:", formData);
  

  try {
    const response = await fetch(apiUrl, {
      method: "POST",
      body: formData,
    });
    if (response.ok) {
      uploadResult.value = t("datasetRegistered");
    } else {
      uploadResult.value = t("uploadFailed");
    }
  } catch (error) {
    uploadResult.value = t("errorOccurred");
  }
  console.log("uploadResult:", uploadResult.value);
}
</script>

<style scoped>
input[type="text"],
select,
input[type="file"] {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: var(--color-bg-main);
  color: var(--color-text-main);
}
.upload-result {
  margin-top: 1rem;
  color: #388e3c;
  font-weight: bold;
}
</style>
