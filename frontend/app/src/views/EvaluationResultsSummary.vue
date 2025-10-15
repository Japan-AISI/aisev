<template>
  <div class="container-bg">
    <Header :breadcrumbs="breadcrumbs" />
    <div class="container">
      <h2>{{ $t("evaluationResultsSummary") }}</h2>
      <!-- Top: Radar chart display -->
      <section class="card top-section">
        <RadarChartSection :charts="selectedCharts" @select="onChartSelect" />
      </section>
      <!-- Middle: Detailed information (tab switching) -->
      <section class="card middle-section">
        <DetailTabs
          :details="selectedDetails"
          :activeTab="activeTab"
          @changeTab="activeTab = $event"
          @goDetail="goToDetail"
        />
      </section>
      <!-- Bottom: List of evaluation results (paging support) -->
      <section class="card bottom-section">
        <EvaluationResultList
          :results="pagedResults"
          :selectedIds="selectedIds"
          @selectResult="onResultSelect"
          :maxSelectable="3"
        />
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
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import RadarChartSection from "../components/RadarChartSection.vue";
import DetailTabs from "../components/DetailTabs.vue";
import EvaluationResultList from "../components/EvaluationResultList.vue";
import Header from "../components/Header.vue";
import {
  getPerspectiveListByLocale,
  toJapanesePerspective,
} from "../utils/perspectiveMapping";

// Type for evaluation result summary retrieved from API
interface EvaluationResult {
  id: number;
  name: string; // Evaluation name
  modelName: string; // Model name to be evaluated
  judgeModelName: string; // Evaluation judgment model name
  definitionName: string; // Evaluation definition name
  evaluatedAt: string; // Evaluation date
  status: string; // Evaluation status
  radarData: number[]; // Scores for perspectives 1-10
}

const evaluationResults = ref<EvaluationResult[]>([]);
const selectedIds = ref<number[]>([1]); // Select one by default
const activeTab = ref(0);
const itemsPerPage = 10;
const currentPage = ref(1);
// Return results sorted in descending order by date
const sortedResults = computed(() => {
  return [...evaluationResults.value].sort(
    (a, b) =>
      new Date(b.evaluatedAt).getTime() - new Date(a.evaluatedAt).getTime()
  );
});
const pagedResults = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return sortedResults.value.slice(start, start + itemsPerPage);
});
const totalPages = computed(() =>
  Math.ceil(sortedResults.value.length / itemsPerPage)
);
function goToPage(page: number) {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
}
const router = useRouter();
const { t, locale } = useI18n();

const breadcrumbs = computed(() => [
  { label: t("home"), link: "/" },
  { label: t("evaluatorHomeTitle"), link: "/evaluator-home" },
  { label: t("evaluationResultsSummary") },
]);

onMounted(async () => {
  try {
    const res = await fetch("http://localhost:8000/evaluation_results/");
    if (!res.ok) throw new Error("API取得失敗");
    const data = await res.json();
    console.log("Evaluation Results:", data);

    // Retrieve evaluation for 10 perspectives
    const get_scores = async (id: number) => {
      const a_scores_promise = await fetch(
        `http://localhost:8000/evaluation_results/${id}/10perspective_scores`,
        {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        }
      );
      const a_scores = await a_scores_promise.json();
      // Arrange perspectives in order as a list

      const orderedKeys = getPerspectiveListByLocale(locale.value).map(
        (label) => toJapanesePerspective(label) || label
      );

      const a_scores_list = orderedKeys.map(
        (key: string) => a_scores[key] ?? 0
      );
      // Convert 0-1 scale to 0-100 scale
      // for (let i = 0; i < a_scores_list.length; i++) {
      //   a_scores_list[i] = Math.round(a_scores_list[i] * 100);
      // }
      return a_scores_list;
    };
    const scores = await Promise.all(data.map((r: any) => get_scores(r.id)));
    console.log("Scores:", scores);

    // Reassign keys
    const results = data.map((r: any, index: number) => ({
      id: r.id,
      name: r.name,
      modelName: r.target_ai_model_name,
      judgeModelName: r.evaluator_ai_model_name,
      definitionName: r.evaluation_name,
      evaluatedAt: r.created_date,
      status:
        r.quantitative_results != null || r.qualitative_results != null
          ? t("evaluationCompleted")
          : t("evaluationInProgress"),
      radarData: scores[index],
    }));

    console.log("result", results);

    // Assumption returned by data.results: Array<EvaluationResult>

    evaluationResults.value = results;
    // Default Selection
    if (results && results.length > 0) {
      const sorted = [...results].sort(
        (a, b) =>
          new Date(b.evaluatedAt).getTime() - new Date(a.evaluatedAt).getTime()
      );
      selectedIds.value = [sorted[0].id];
    }
    console.log("Processed Evaluation Results:", evaluationResults.value);
    // throw new Error("Intentional error for testing purposes");
  } catch (e) {
    evaluationResults.value = [];
    selectedIds.value = [1];
  }
});

const selectedCharts = computed(() => {
  console.log("selectedCharts ", evaluationResults.value);

  return evaluationResults.value
    .filter((r: EvaluationResult) => selectedIds.value.includes(r.id))
    .slice(0, 3); // Display up to 3
});
const selectedDetails = computed(() => {
  return selectedCharts.value.map((r: EvaluationResult) => ({
    id: r.id,
    name: r.name, // Evaluation identification label
    modelName: r.modelName, // AI information to be evaluated
    judgeModelName: r.judgeModelName, // AI information for evaluation judgment
    definitionName: r.definitionName, // Evaluation Content Definition
    evaluatedAt: r.evaluatedAt,
  }));
});

function onResultSelect(ids: number[]) {
  selectedIds.value = ids.slice(0, 3); // Select up to 3
  if (activeTab.value >= ids.length) activeTab.value = 0;
}
function onChartSelect(idx: number) {
  activeTab.value = idx;
}
function goToDetail(id: number) {
  // console.log("Go to detail for ID:", id.toString());

  router.push({
    path: "/eval-result-detail",
    query: { resultId: id.toString() },
  });
}
</script>

<style scoped>
.top-section {
  border-bottom: 2px solid var(--color-shadow);
}
.middle-section {
  border-top: 1px solid var(--color-shadow);
  border-bottom: 1px solid var(--color-shadow);
}
.bottom-section {
  border-top: 2px solid var(--color-shadow);
  overflow-y: visible;
}
</style>
