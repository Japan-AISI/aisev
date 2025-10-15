<template>
  <div class="container-bg">
    <!-- Header -->
    <Header :breadcrumbs="breadcrumbs" />
    <div class="container">
      <h2>{{ $t("datasetCreationAssistance") }}</h2>
      <div
        v-for="(item, idx) in questions"
        :key="item.id"
        class="card"
        style="margin-bottom: 1.5rem"
      >
        <div class="form-group-row">
          <label>{{ $t("questionInput") }}：　　　</label>
          <textarea
            v-model="item.question"
            rows="1"
            :placeholder="$t('questionPlaceholder')"
            required
          ></textarea>
        </div>
        <div class="form-group-row">
          <label>{{ $t("expectedAnswer") }}：　</label>
          <textarea
            v-model="item.expectedAnswer"
            rows="1"
            :placeholder="$t('expectedAnswerPlaceholder')"
            required
          ></textarea>
        </div>
        <div class="form-group-row">
          <label class="form-label" style="display: block"
            >{{ $t("targetAIModel") }}：</label
          >
          <select v-model="item.targetAI" required>
            <option value="">{{ $t("pleaseSelect") }}</option>
            <option v-for="model in models" :key="model.id" :value="model.id">
              {{ model.name }}
            </option>
          </select>
        </div>
        <div class="form-group-row">
          <label class="form-label" style="display: block"
            >{{ $t("tenPerspectives") }}：　</label
          >
          <select v-model="item.criterion" required class="criterion-select">
            <option value="">{{ $t("pleaseSelect") }}</option>
            <option v-for="c in criteria" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        <div class="form-group-row">
          <label>{{ $t("difficultyEvaluation") }}：</label>
          <span style="margin: 0 1rem">
            {{ $t("paraphraseAccuracy") }}　：　
            <template v-if="item.isEvaluating">
              <span class="loading-spinner"></span>
            </template>
            <template v-else-if="item.isScoring"
              >{{ item.paraphraseCorrect }}/{{ item.paraphraseTotal }}</template
            >
            <template v-else>‐/-</template>
          </span>
        </div>
        <div v-if="item.isScoring" style="margin-top: 1rem">
          <details>
            <summary>{{ $t("evaluationResultDetails") }}</summary>
            <div style="margin-top: 0.5rem">
              <table style="width: 100%; border-collapse: collapse">
                <thead>
                  <tr>
                    <th
                      style="border: 1px solid #ddd; padding: 8px; width: 70%"
                    >
                      {{ $t("paraphraseQuestion") }}
                    </th>
                    <th style="border: 1px solid #ddd; padding: 8px">
                      {{ $t("judgmentResult") }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="result in item.paraphraseResults"
                    :key="result.paraphrase"
                  >
                    <td style="border: 1px solid #ddd; padding: 8px">
                      {{ result.paraphrase }}
                    </td>
                    <td
                      style="
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: center;
                      "
                    >
                      <span
                        :style="{
                          color: result.is_correct === 'C' ? 'green' : 'red',
                          fontWeight: 'bold',
                        }"
                      >
                        {{
                          result.is_correct === "C"
                            ? $t("correct")
                            : $t("incorrect")
                        }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </details>
        </div>
        <div class="card-footer">
          <button
            class="regist-btn"
            @click="runScoring(idx)"
            style="margin-right: 0.5rem"
            :disabled="item.isEvaluating"
          >
            {{ $t("difficultyEvaluation") }}
          </button>
          <button
            class="regist-btn"
            :class="questions.length === 1 ? 'disabled-btn' : 'red-btn'"
            :disabled="questions.length === 1"
            @click="removeContent(idx)"
            :title="$t('atLeastOneRequired')"
          >
            {{ $t("deleteBtn") }}
          </button>
        </div>
      </div>
      <button
        type="button"
        class="regist-btn textarea-add-btn"
        @click="addContent"
        style="margin-bottom: 1.5rem"
      >
        {{ $t("addCard") }}
      </button>
      <div>
        <button
          style="margin-top: 1.5rem"
          class="regist-btn"
          @click="goToOutput"
        >
          {{ $t("datasetOutput") }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from "vue";
import { useI18n } from "vue-i18n";
import Header from "../components/Header.vue";
import {
  getPerspectiveListByLocale,
  toEnglishPerspective,
  toJapanesePerspective,
} from "../utils/perspectiveMapping";

const { t, locale } = useI18n();

// Breadcrumbs
const breadcrumbs = [
  { label: "home", link: "/" },
  { label: "evaluationDefinerHomeTitle", link: "/definer-home" },
  { label: "datasetCreationAssistance" },
];

// standard evaluation criteria
const criteria = computed(() => getPerspectiveListByLocale(locale.value));
const models = ref<any[]>([]);
const selectedTargetAI = ref(models.value[0]?.id || null);
const selectedJudgeAI = ref(models.value[1]?.id || null);

let uniqueId = 1;

const questions = ref([
  {
    id: uniqueId++,
    question: "",
    expectedAnswer: "",
    targetAI: "",
    criterion: "",
    isScoring: false,
    isEvaluating: false,
    paraphraseCorrect: 0,
    paraphraseTotal: 0,
    paraphraseResults: [],
  },
]);

function addContent() {
  questions.value.push({
    id: uniqueId++,
    question: "",
    expectedAnswer: "",
    targetAI: "",
    criterion: "",
    isScoring: false,
    isEvaluating: false,
    paraphraseCorrect: 0,
    paraphraseTotal: 0,
    paraphraseResults: [],
  });
}

// Get AI model list from API
async function fetchModels() {
  try {
    const res = await fetch("http://localhost:8000/ai_models", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    const data = await res.json();
    models.value = Array.isArray(data.ai_models)
      ? data.ai_models
      : Array.isArray(data)
      ? data
      : [];
    selectedTargetAI.value = models.value[0]?.id || null;
    selectedJudgeAI.value = models.value[1]?.id || null;
  } catch (e) {
    console.error(t("aiModelListGetFailed"), e);
    models.value = [];
  }
}

async function runScoring(idx: number) {
  const item = questions.value[idx];
  if (!item.question.trim() || !item.expectedAnswer.trim()) {
    alert(t("pleaseEnterQuestionAndAnswer"));
    return;
  }
  if (!item.targetAI) {
    alert(t("pleaseSelectTargetAI"));
    return;
  }

  item.isEvaluating = true;
  item.isScoring = false;
  item.paraphraseCorrect = 0;
  item.paraphraseTotal = 0;
  item.paraphraseResults = [];

  try {
    const response = await fetch("http://localhost:8000/scoring-dataset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: item.question,
        expected_answer: item.expectedAnswer,
        model_id: item.targetAI,
      }),
    });
    if (!response.ok) throw new Error(t("apiCallFailed"));
    const data = await response.json();
    item.paraphraseResults = data.results; // [{paraphrase, is_correct}, ...]
    item.paraphraseTotal =
      Object.keys(data.results).length || data.paraphraseResults?.length || 0;
    if (Array.isArray(data.results)) item.paraphraseTotal = data.results.length;
    if (typeof data.results === "object" && !Array.isArray(data.results)) {
      item.paraphraseResults = Object.values(data.results);
      item.paraphraseTotal = Object.values(data.results).length;
    }
    item.paraphraseCorrect = data.total_correct;
    item.isScoring = true;
  } catch (e: any) {
    alert(`${t("apiCallError")}：${e.message}`);
  } finally {
    item.isEvaluating = false;
  }
}

function removeContent(idx) {
  questions.value.splice(idx, 1);
}

function getDateStr() {
  // yyyyMMdd_HHmmss format
  const now = new Date();
  return (
    now.getFullYear() +
    ("0" + (now.getMonth() + 1)).slice(-2) +
    ("0" + now.getDate()).slice(-2) +
    "_" +
    ("0" + now.getHours()).slice(-2) +
    ("0" + now.getMinutes()).slice(-2) +
    ("0" + now.getSeconds()).slice(-2)
  );
}

function goToOutput() {
  const outputItems = questions.value.filter(
    (q) => q.isScoring && q.criterion !== ""
  );
  if (outputItems.length !== questions.value.length) {
    alert(t("cannotExport"));
    return;
  }
  const csvHeader = ["ID", "text", "output", "ten_perspective"];
  const csvRows = [csvHeader.join(",")];
  outputItems.forEach((item, idx) => {
    // Escape commas and line breaks
    const esc = (v: string) =>
      '"' + (v || "").replace(/"/g, '""').replace(/\n/g, " ") + '"';
    const accuracyStr = `${item.paraphraseCorrect}/${item.paraphraseTotal}`;
    const perspectiveForCsv = locale.value.startsWith("en")
      ? toEnglishPerspective(item.criterion) || item.criterion
      : toJapanesePerspective(item.criterion) || item.criterion;
    csvRows.push(
      [
        idx + 1,
        esc(item.question),
        esc(item.expectedAnswer),
        esc(perspectiveForCsv as string),
      ].join(",")
    );
  });
  const csvContent = csvRows.join("\r\n");
  const blob = new Blob([csvContent], { type: "text/csv" });
  const dtStr = getDateStr();
  const filename = `dataset_${dtStr}.csv`;
  // Download process
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

onMounted(() => {
  fetchModels();
});

watch(
  () => locale.value,
  (newLocale) => {
    questions.value = questions.value.map((item) => ({
      ...item,
      criterion: newLocale.startsWith("en")
        ? toEnglishPerspective(item.criterion)
        : toJapanesePerspective(item.criterion),
    }));
  }
);

// No per-item default selection is required, so no additional watcher needed.
</script>

<style scoped>
.card-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #f0f0f0;
}
.card {
  width: 65%;
  margin-left: auto;
  margin-right: auto;
}
select,
textarea {
  flex: 1;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 1rem;
}
.red-btn {
  background: #ff3333 !important;
  color: #fff !important;
  border: 1px solid #ff3333 !important;
  cursor: pointer;
}
.disabled-btn {
  background: #ccc !important;
  color: #999 !important;
  border: 1px solid #ccc !important;
  cursor: not-allowed !important;
}

.criterion-select {
  width: 100%;
  max-width: 100%;
  word-wrap: break-word;
  white-space: normal;
}

.criterion-select option {
  white-space: normal;
  word-wrap: break-word;
  overflow-wrap: break-word;
  max-width: 100%;
  padding: 0.25rem 0.5rem;
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  vertical-align: middle;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
