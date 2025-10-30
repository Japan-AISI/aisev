<template>
  <div id="container-bg">
    <!-- Header section -->
    <Header :breadcrumbs="breadcrumbs" />
    <main class="container">
      <section class="card">
        <!-- Evaluation List section -->
        <div>
          <h2>{{ $t("evaluationDefinitionList") }}</h2>
          <div class="table-header">
            <button
              class="delete-btn"
              @click="deleteDefinition(selectedEvaluationId)"
            >
              {{ $t("deleteDefinition") }}
            </button>
          </div>
          <div>
            <table class="eval-table">
              <thead>
                <tr>
                  <th style="text-align: center">
                    {{ $t("evaluationSelect") }}
                  </th>
                  <th style="text-align: left">
                    {{ $t("evaluationDefinitionName") }}
                  </th>
                  <th style="text-align: left">
                    {{ $t("evaluationCreationDate") }}
                  </th>
                  <th style="text-align: left">
                    {{ $t("usedDatasetQuestions") }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="evaluation in pagedEvaluations" :key="evaluation.id">
                  <td>
                    <input
                      type="radio"
                      name="evaluation"
                      :value="evaluation.id"
                      v-model="selectedEvaluationId"
                    />
                  </td>
                  <td>{{ evaluation.name }}</td>
                  <td>{{ formatDateTime(evaluation.createdAt) }}</td>
                  <td>
                    <div 
                      class="dataset-cell"
                      :title="getUsedDatasetsText(evaluation)"
                    >
                      {{
                        Array.isArray(evaluation.usedDatasets)
                          ? evaluation.usedDatasets
                              .map((ds) =>
                                typeof ds === "object" &&
                                ds !== null &&
                                "name" in ds
                                  ? ds.name
                                  : ds
                              )
                              .join(", \n")
                          : evaluation.usedDatasets
                      }}
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <!-- Pagination controls -->
          <div class="pagination" v-if="totalPages > 1">
            <button
              :disabled="currentPage === 1"
              @click="goToPage(currentPage - 1)"
            >
              {{ $t("previousPage") }}
            </button>
            <span> {{ currentPage }} / {{ totalPages }} </span>
            <button
              :disabled="currentPage === totalPages"
              @click="goToPage(currentPage + 1)"
            >
              {{ $t("nextPage") }}
            </button>
          </div>
        </div>
      </section>

      <hr />

      <!-- Create Evaluation Definition section -->
      <section class="card">
        <div>
          <h2>{{ $t("evaluationDefinitionCreation") }}</h2>
          <div class="form-group">
            <label for="evaluation-name">{{
              $t("evaluationDefinitionNameLabel")
            }}</label>
            <input
              id="evaluation-name"
              class="eval-name-input"
              v-model="evaluationName"
              type="text"
              :placeholder="$t('evaluationDefinitionNamePlaceholder')"
              required
            />
          </div>
        </div>
        <div class="evals-list">
          <div class="">
            <div
                v-for="(criterion, index) in evaluationCriteria"
              :key="index"
              class="eval-block"
            >
              <details>
                <summary>{{ criterion }}</summary>
                <div class="eval-item-content">
                  <label>
                    {{ $t("useGsnLabel") }}
                    <input
                      type="checkbox"
                      v-model="selectedGsnChecks[index]"
                      @change="onGsnCheckChange(index)"
                    />
                  </label>
                </div>
                <div class="eval-item-content" v-if="!selectedGsnChecks[index]">
                  <label>
                    {{ $t("quantitativeEvaluation") }}
                    <input
                      type="checkbox"
                      v-model="selectedQuantitativeChecks[index]"
                      @change="onQuantitativeCheckChange(index)"
                    />
                  </label>
                  <select
                    v-model="selectedQuantitativeDatasets[index]"
                    class="dataset-select scrollable-select"
                    multiple
                    size="5"
                  >
                    <option value="" disabled>{{ $t("selectDataset") }}</option>
                    <option
                      v-for="dataset in datasets"
                      :key="dataset.id"
                      :value="dataset.id"
                    >
                      {{ dataset.name }}
                    </option>
                  </select>
                  <!-- Quantitative Evaluation Percentage Slider -->
                  <label>
                    {{ $t("quantitativeEvaluationRatio") }}
                    <input
                      type="range"
                      :id="'quantitative_percentage' + index"
                      class="percentage-slider"
                      v-model.number="selectedQuantitativePercentages[index]"
                      min="0"
                      max="100"
                      step="1"
                      @input="onQuantitativeInput(index)"
                      :disabled="!selectedQuantitativeChecks[index]"
                    />
                    <p>{{ selectedQuantitativePercentages[index] }}%</p>
                  </label>
                </div>
                <div class="eval-item-content" v-if="!selectedGsnChecks[index]">
                  <!-- Removed prompt settings -->
                </div>
                <div class="eval-item-content" v-if="!selectedGsnChecks[index]">
                  <label>
                    {{ $t("qualitativeEvaluation") }}
                    <input
                      type="checkbox"
                      v-model="selectedQualitativeChecks[index]"
                      @change="onQualitativeCheckChange(index)"
                    />
                  </label>
                  <select
                    v-model="selectedQualitativeQuestions[index]"
                    class="dataset-select scrollable-select"
                    multiple
                    size="5"
                  >
                    <option value="" disabled>
                      {{ $t("selectQuestionGroup") }}
                    </option>
                    <option
                      v-for="question in questions"
                      :key="question.id"
                      :value="question.id"
                    >
                      {{ question.name }}
                    </option>
                  </select>
                  <!-- Qualitative Evaluation Percentage Slider -->
                  <label>
                    {{ $t("qualitativeEvaluationRatio") }}
                    <input
                      type="range"
                      :id="'qualitative_percentage' + index"
                      class="percentage-slider"
                      v-model.number="selectedQualitativePercentages[index]"
                      min="0"
                      max="100"
                      step="1"
                      @input="onQualitativeInput(index)"
                      :disabled="!selectedQualitativeChecks[index]"
                    />
                    <p>{{ selectedQualitativePercentages[index] }}%</p>
                  </label>
                </div>
              </details>
            </div>
          </div>
        </div>
        <button class="regist-btn" @click="registDefinition">
          {{ $t("registerEvaluationDefinition") }}
        </button>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useI18n } from "vue-i18n";
import Header from "../components/Header.vue";
import {
  getPerspectiveListByLocale,
  TEN_PERSPECTIVES_JA,
} from "../utils/perspectiveMapping";

const { locale, t } = useI18n();

const getLabels = () => getPerspectiveListByLocale(locale.value);



// Breadcrumbs
const breadcrumbs = [
  { label: "home", link: "/" },
  { label: "evaluationDefinerHomeTitle", link: "/definer-home" },
  { label: "evalDesignScreen" },
];

// Evaluation List
const evaluations = ref([]);
const datasets = ref([]);
const questions = ref([]);

// Fetch Evaluation Definitions
async function fetchEvaluations() {
  try {
    const response = await fetch("http://localhost:8000/evaluations", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    if (!response.ok) throw new Error(t("apiGetFailed"));
    const data = await response.json();
    console.log("Fetched Evaluations Data:", data);
    evaluations.value = Array.isArray(data.evaluations)
      ? data.evaluations
      : Array.isArray(data)
      ? data
      : [];

    console.log("Fetched Evaluations:", evaluations.value);
    
  } catch (err) {
    console.error(err);
    window.alert(t("evaluationDefinitionListGetFailedDefinition"));
  }
}

// Fetch Datasets and Questions
onMounted(async () => {
  try {
    await fetchEvaluations();
    const datasetResponse = await fetch(
      "http://localhost:8000/quantitative_datasets",
      {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      }
    );
    if (!datasetResponse.ok) throw new Error(t("apiGetFailed"));
    const datasetData = await datasetResponse.json();
    datasets.value = Array.isArray(datasetData.quantitative_datasets)
      ? datasetData.quantitative_datasets
      : Array.isArray(datasetData)
      ? datasetData
      : [];

    const questionResponse = await fetch(
      "http://localhost:8000/qualitative_datasets",
      {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      }
    );
    if (!questionResponse.ok) throw new Error(t("apiGetFailed"));
    const questionData = await questionResponse.json();
    questions.value = Array.isArray(questionData.qualitative_datasets)
      ? questionData.qualitative_datasets
      : Array.isArray(questionData)
      ? questionData
      : [];
  } catch (err) {
    console.error(err);
    window.alert(t("dataGetFailed"));
  }
});

// Setup Pagination
const itemsPerPage = 5;
const currentPage = ref(1);
const totalPages = computed(() =>
  Math.ceil(evaluations.value.length / itemsPerPage)
);
const pagedEvaluations = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return evaluations.value.slice(start, start + itemsPerPage);
});

// Pagination Functions
function goToPage(page) {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
}

function prevPage() {
  if (currentPage.value > 1) currentPage.value--;
}

function nextPage() {
  if (currentPage.value < totalPages.value) currentPage.value++;
}

// Currently selected evaluation ID
const selectedEvaluationId = ref(null);

// Delete Evaluation Definition
const deleteDefinition = async (id) => {
  if (!id) {
    window.alert(t("noEvaluationDefinitionSelected"));
    return;
  }
  const confirmed = window.confirm(t("confirmDelete"));
  if (!confirmed) return;
  try {
    const response = await fetch(
      `http://localhost:8000/evaluation/${encodeURIComponent(id)}`,
      {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
      }
    );
    if (!response.ok) {
      throw new Error(t("deletionFailedDefinition"));
    }
    // when deletion is successful, fetch evaluations again
    await fetchEvaluations();
    // Reset selected evaluation ID
    selectedEvaluationId.value = null;
    window.alert(t("deletionCompleted"));
  } catch (err) {
    console.error(err);
    window.alert(t("deletionFailedDefinition"));
  }
};

// Register Evaluation Definition
const registDefinition = async () => {
  if (!evaluationName.value || evaluationName.value.trim() === "") {
    window.alert(
      t("evaluationDefinitionNameRequired") || "評価定義名を入力してください。"
    );
    return;
  }
  
  const definition = {
    evaluationName: evaluationName.value,
    // criteria: evaluationCriteria.value.map((criterion, index) => {
    criteria: TEN_PERSPECTIVES_JA.map((criterion, index) => {
      // ID of the dataset
      const selectedDatasetIds =
        selectedQuantitativeDatasets.value[index] || [];
      // ID of the question
      const selectedQuestionIds =
        selectedQualitativeQuestions.value[index] || [];
      const criterionData = {
        criterion,
        quantitative: {
          checked: selectedQuantitativeChecks.value[index] || false,
          datasets: selectedDatasetIds,
          percentage: selectedQuantitativePercentages.value[index] || 0,
          text: quantitativeTexts.value[index] || "",
        },
        qualitative: {
          checked: selectedQualitativeChecks.value[index] || false,
          questions: selectedQuestionIds,
          percentage: selectedQualitativePercentages.value[index] || 0,
        },
      };

      // If GSN usage is checked, add use_gsn=true
      if (selectedGsnChecks.value[index]) {
        criterionData.use_gsn = true;
      }

      return {
        ...criterionData,
        criterion,
      };
    }),
  };

  console.log("Evaluation Definition:", definition);

  try {
    const response = await fetch("http://localhost:8000/evaluation", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(definition),
    });
    if (!response.ok) {
      throw new Error(t("registrationFailedDefinition"));
    }
    window.alert(t("creationCompleted"));
    // Reset form fields
    await fetchEvaluations();
  } catch (err) {
    console.error(err);
    window.alert(t("registrationFailedDefinition"));
  }
};

// percentage input handling for quantitative and qualitative evaluations
function onQuantitativeInput(index) {
  selectedQuantitativePercentages.value[index] = Math.min(
    100,
    Math.max(0, selectedQuantitativePercentages.value[index])
  );
  if (
    selectedQuantitativeChecks.value[index] &&
    selectedQualitativeChecks.value[index]
  ) {
    // When both are checked, ensure the total is 100%
    selectedQualitativePercentages.value[index] =
      100 - selectedQuantitativePercentages.value[index];
  } else if (
    selectedQuantitativeChecks.value[index] &&
    !selectedQualitativeChecks.value[index]
  ) {
    selectedQualitativePercentages.value[index] =
      100 - selectedQuantitativePercentages.value[index];
  }
}
function onQualitativeInput(index) {
  selectedQualitativePercentages.value[index] = Math.min(
    100,
    Math.max(0, selectedQualitativePercentages.value[index])
  );
  if (
    selectedQuantitativeChecks.value[index] &&
    selectedQualitativeChecks.value[index]
  ) {
    // When both are checked, linked so that the total is 100%
    selectedQuantitativePercentages.value[index] =
      100 - selectedQualitativePercentages.value[index];
  } else if (
    selectedQualitativeChecks.value[index] &&
    !selectedQuantitativeChecks.value[index]
  ) {
    selectedQuantitativePercentages.value[index] =
      100 - selectedQualitativePercentages.value[index];
  }
}

function onQuantitativeCheckChange(index) {
  if (
    selectedQuantitativeChecks.value[index] &&
    !selectedQualitativeChecks.value[index]
  ) {
    // When only quantitative is checked
    selectedQuantitativePercentages.value[index] = 100;
    selectedQualitativePercentages.value[index] = 0;
  } else if (
    !selectedQuantitativeChecks.value[index] &&
    selectedQualitativeChecks.value[index]
  ) {
    // When only qualitative is checked
    selectedQuantitativePercentages.value[index] = 0;
    selectedQualitativePercentages.value[index] = 100;
  } else if (
    !selectedQuantitativeChecks.value[index] &&
    !selectedQualitativeChecks.value[index]
  ) {
    // When both are unchecked
    selectedQuantitativePercentages.value[index] = 0;
    selectedQualitativePercentages.value[index] = 0;
  }
  // Do nothing when both are checked
}
function onQualitativeCheckChange(index) {
  if (
    selectedQualitativeChecks.value[index] &&
    !selectedQuantitativeChecks.value[index]
  ) {
    // When only qualitative is checked
    selectedQualitativePercentages.value[index] = 100;
    selectedQuantitativePercentages.value[index] = 0;
  } else if (
    !selectedQualitativeChecks.value[index] &&
    selectedQuantitativeChecks.value[index]
  ) {
    // When only quantitative is checked
    selectedQualitativePercentages.value[index] = 0;
    selectedQuantitativePercentages.value[index] = 100;
  } else if (
    !selectedQualitativeChecks.value[index] &&
    !selectedQuantitativeChecks.value[index]
  ) {
    // When both are unchecked
    selectedQualitativePercentages.value[index] = 0;
    selectedQuantitativePercentages.value[index] = 0;
  }
  // Do nothing when both are checked
}

// data for evaluation definition
const evaluationName = ref("");
// standard evaluation criteria - computed to be reactive to locale changes
const evaluationCriteria = computed(() => getLabels());
const selectedCriteria = ref(
  Array(getLabels().length).fill(false)
);

// selected datasets and questions
const selectedQuantitativeDatasets = ref(
  Array(getLabels().length)
    .fill()
    .map(() => [])
);
const selectedQualitativeQuestions = ref(
  Array(getLabels().length)
    .fill()
    .map(() => [])
);
const selectedQuantitativePercentages = ref(
  Array(getLabels().length).fill(0)
);
const selectedQualitativePercentages = ref(
  Array(getLabels().length).fill(0)
);
const selectedQuantitativeChecks = ref(
  Array(getLabels().length).fill(false)
);
const selectedQualitativeChecks = ref(
  Array(getLabels().length).fill(false)
);
const selectedGsnChecks = ref(
  Array(getLabels().length).fill(false)
);
const quantitativeTexts = ref(Array(getLabels().length).fill(""));

// GSN checkbox change handler
function onGsnCheckChange(index) {
  if (selectedGsnChecks.value[index]) {
    // If GSN is checked, uncheck quantitative and qualitative
    selectedQuantitativeChecks.value[index] = false;
    selectedQualitativeChecks.value[index] = false;
    selectedQuantitativePercentages.value[index] = 0;
    selectedQualitativePercentages.value[index] = 0;
  }
}

// Watch for locale changes to reset form arrays when language changes
watch(locale, () => {
  const newLength = getLabels().length;
  selectedCriteria.value = Array(newLength).fill(false);
  selectedQuantitativeDatasets.value = Array(newLength).fill().map(() => []);
  selectedQualitativeQuestions.value = Array(newLength).fill().map(() => []);
  selectedQuantitativePercentages.value = Array(newLength).fill(0);
  selectedQualitativePercentages.value = Array(newLength).fill(0);
  selectedQuantitativeChecks.value = Array(newLength).fill(false);
  selectedQualitativeChecks.value = Array(newLength).fill(false);
  selectedGsnChecks.value = Array(newLength).fill(false);
  quantitativeTexts.value = Array(newLength).fill("");
});

// Helper function to get full dataset text for tooltip
function getUsedDatasetsText(evaluation) {
  return Array.isArray(evaluation.usedDatasets)
    ? evaluation.usedDatasets
        .map((ds) =>
          typeof ds === "object" &&
          ds !== null &&
          "name" in ds
            ? ds.name
            : ds
        )
        .join(", \n")
    : evaluation.usedDatasets || '';
}

// Date-time formatting function
function formatDateTime(dateString) {
  if (!dateString) return "";
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return dateString;
  const pad = (n) => n.toString().padStart(2, "0");
  return (
    date.getFullYear() +
    "-" +
    pad(date.getMonth() + 1) +
    "-" +
    pad(date.getDate()) +
    " " +
    pad(date.getHours()) +
    ":" +
    pad(date.getMinutes()) +
    ":" +
    pad(date.getSeconds())
  );
}
</script>

<style scoped>
/* Table Styles */
.eval-table {
  table-layout: fixed;
  width: 100%;
  overflow-wrap: break-word;
}

.eval-table th:nth-child(1),
.eval-table td:nth-child(1) {
  width: 10%;
  text-align: center;
}

.eval-table th:nth-child(2),
.eval-table td:nth-child(2) {
  width: 25%;
  text-align: left;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.eval-table th:nth-child(3),
.eval-table td:nth-child(3) {
  width: 20%;
  text-align: left;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.eval-table th:nth-child(4),
.eval-table td:nth-child(4) {
  width: 45%;
  text-align: left;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: normal;
}

.eval-table tr:last-child td {
  border-bottom: none;
}

/* Dataset cell styling for text truncation */
.dataset-cell {
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dataset-cell:hover {
  white-space: pre-line;
  overflow: visible;
  word-wrap: break-word;
  border-radius: 4px;
  padding: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 10;
}

/* Make table responsive on smaller screens */
@media (max-width: 768px) {
  .eval-table {
    font-size: 0.9rem;
  }

  .eval-table th,
  .eval-table td {
    padding: 8px 6px;
  }
}

/* Evaluation Define */
.evals-list {
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
}

.eval-block {
  border: 0.2rem solid var(--color-border);
  background-color: var(--color-bg-accent);
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 2rem;
  margin-left: 5rem;
  margin-right: 5rem;
}

.eval-item-content {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 15px;
}

.eval-item-content label {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-shrink: 0;
  min-width: 120px;
}

.eval-item-content select {
  padding: 5px;
  background-color: var(--color-bg-main);
  color: var(--color-text-main);
  flex-shrink: 0;
}

.eval-textarea {
  width: 65%;
  min-height: 3em;
  max-width: 100%;
  margin-left: 7.5rem;
  margin-bottom: 20px;
  padding: 6px 8px;
  border-radius: 4px;
  border: 1px solid var(--color-border);
  background-color: var(--color-bg-main);
  color: var(--color-text-main);
  resize: vertical;
  font-size: 1em;
}

details .eval-item-content {
  overflow: hidden;
  max-height: 0;
  transition: max-height 0.3s ease;
}

details[open] .eval-item-content {
  max-height: 500px;
}

.dataset-select {
  width: 180px;
  max-width: 180px;
  margin-right: 10px;
  margin-bottom: 10px;
  padding: 5px;
  background-color: var(--color-bg-main);
  color: var(--color-text-main);
  flex-shrink: 0;
}

.scrollable-select {
  overflow-x: auto;
  white-space: nowrap;
  max-width: 180px;
  min-width: 150px;
  resize: horizontal;
  scrollbar-width: auto;
  display: inline-block;
}
.scrollable-select option {
  white-space: pre;
}

.percentage-slider {
  width: 150px;
  min-width: 150px;
}

/* Evaluation ratio label styling */
.eval-item-content label:has(.percentage-slider) {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 180px;
  gap: 5px;
}

.eval-item-content label:has(.percentage-slider) p {
  margin: 0;
  font-weight: bold;
  color: var(--color-text-accent);
}

/* Responsive adjustments for evaluation items */
@media (max-width: 1024px) {
  .eval-item-content {
    flex-direction: column;
    align-items: stretch;
  }

  .dataset-select {
    width: 100%;
    max-width: none;
  }

  .scrollable-select {
    max-width: 100%;
  }

  .eval-item-content label:has(.percentage-slider) {
    min-width: 100%;
  }

  .percentage-slider {
    width: 100%;
  }
}

/* details */
details summary {
  font-size: 16px;
  cursor: pointer;
  transition: color 0.3s ease, transform 0.3s ease;
}

details[open] summary {
  color: var(--color-text-main);
  transform: rotate(0deg);
}
</style>
