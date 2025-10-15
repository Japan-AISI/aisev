<template>
  <div class="container-bg">
    <Header class="print-hide" :breadcrumbs="breadcrumbs" />
    <div class="container">
      <h2>{{ $t("evaluationResultReport") }}</h2>
      <button
        class="regist-btn print-hide"
        @click="exportPDF"
        style="margin-bottom: 1.5rem"
      >
        {{ $t("exportPDF") }}
      </button>
      <div
        id="pdf-content"
        style="background: white; color: black; padding: 2rem"
      >
        <!-- Radar Chart -->
        <section class="card top-section">
          <RadarChartSection :charts="selectedCharts" :isPdfMode="true" />
        </section>
        <div class="page-break"></div>
        <!-- Detailed Information -->
        <section class="card middle-section">
          <div
            v-for="detail in selectedDetails"
            :key="detail.id"
            class="pdf-detail-block"
          >
            <div>
              <b>{{ $t("evaluationName") }}:</b> {{ detail.name }}
            </div>
            <div>
              <b>{{ $t("targetModelName") }}:</b> {{ detail.modelName }}
            </div>
            <div>
              <b>{{ $t("judgeModelName") }}:</b> {{ detail.judgeModelName }}
            </div>
            <div>
              <b>{{ $t("definitionName") }}:</b> {{ detail.definitionName }}
            </div>
            <div>
              <b>{{ $t("evaluatedAt") }}:</b> {{ detail.evaluatedAt }}
            </div>
          </div>
        </section>
        <div class="page-break"></div>
        <!-- Details by perspective -->
        <section class="card bottom-section">
          <div
            v-for="(perspective, idx) in perspectives"
            :key="idx"
            class="perspective-section"
          >
            <h3>
              {{
                t(perspective) !== perspective ? t(perspective) : perspective
              }}
            </h3>
            <div class="scroll-table-wrapper">
              <table class="detail-table">
                <thead>
                  <tr>
                    <th v-if="showFirstSubgoal(idx)">
                      {{ $t("secondGoal") }}
                    </th>
                    <th v-if="showLeafSubgoal(idx)">{{ $t("gsnLeaf") }}</th>
                    <th>{{ t("classification") }}</th>
                    <th>{{ t("question") }}</th>
                    <th>{{ t("answer") }}</th>
                    <th>{{ t("score") }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in detailData[idx]" :key="item.id">
                    <td v-if="showFirstSubgoal(idx)">
                      {{ item.secondGoal }}
                    </td>
                    <td v-if="showLeafSubgoal(idx)">{{ item.gsnLeaf }}</td>
                    <td>{{ item.category }}</td>
                    <td>{{ item.question }}</td>
                    <td>{{ item.answer }}</td>
                    <td>{{ item.score }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>
        <div class="page-break"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import Header from "../components/Header.vue";
import RadarChartSection from "../components/RadarChartSection.vue";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import { useI18n } from "vue-i18n";
import {
  getPerspectiveListByLocale,
  toJapanesePerspective,
} from "../utils/perspectiveMapping";

const { t, locale } = useI18n();

import { computed } from "vue";

// i18n support: Switch viewpoint list by language
const perspectives = computed(() => getPerspectiveListByLocale(locale.value));

const breadcrumbs = computed(() => [
  { label: t("home"), link: "/" },
  { label: t("evaluatorHomeTitle"), link: "/evaluator-home" },
  { label: t("evaluationResultsSummary"), link: "/eval-result-summary" },
  {
    label: t("evaluationResultDetail"),
    link: `/eval-result-detail?resultId=${new URLSearchParams(
      window.location.search
    ).get("resultId")}`,
  },
  { label: t("evaluationResultReport") },
]);

const selectedCharts = ref<any[]>([]);
const selectedDetails = ref<any[]>([]);
const detailData = ref<any[][]>([]);

async function fetchSummaryAndDetail() {
  try {
    const urlParams = new URLSearchParams(window.location.search);
    const resultId = urlParams.get("resultId");
    if (!resultId) return;
    const res = await fetch("http://localhost:8000/evaluation_results/");
    if (!res.ok) throw new Error("API取得失敗");
    const data = await res.json();
    const get_scores = async (id: number) => {
      const a_scores_promise = await fetch(
        `http://localhost:8000/evaluation_results/${id}/10perspective_scores`,
        {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        }
      );
      const a_scores = await a_scores_promise.json();
      const japaneseKeys = perspectives.value.map(
        (label: string) => toJapanesePerspective(label) || label
      );
      const a_scores_list = japaneseKeys.map((key: string) => a_scores[key]);
      return a_scores_list;
    };
    const target = data.find((r: any) => String(r.id) === String(resultId));
    if (!target) return;
    const scores = await get_scores(target.id);
    const result = {
      id: target.id,
      name: target.name,
      modelName: target.target_ai_model_name,
      judgeModelName: target.evaluator_ai_model_name,
      definitionName: target.evaluation_name,
      evaluatedAt: target.created_date,
      status:
        target.quantitative_results != null &&
        target.qualitative_results != null
          ? t("evaluationCompleted")
          : t("evaluationInProgress"),
      radarData: scores,
    };
    selectedCharts.value = [result];
    selectedDetails.value = [
      {
        id: result.id,
        name: result.name,
        modelName: result.modelName,
        judgeModelName: result.judgeModelName,
        definitionName: result.definitionName,
        evaluatedAt: result.evaluatedAt,
      },
    ];
    await fetchDetailData(result.id);
  } catch (e) {
    selectedCharts.value = [];
    selectedDetails.value = [];
    detailData.value = [];
  }
}

// --- Display decision function for subgoal columns ---
function showFirstSubgoal(idx: number) {
  const arr = (detailData.value[idx] as any[]) || [];
  return arr.some((item) => item.secondGoal && item.secondGoal !== "");
}
function showLeafSubgoal(idx: number) {
  const arr = (detailData.value[idx] as any[]) || [];
  return arr.some(
    (item) => item.gsnLeaf && item.gsnLeaf !== "" && item.gsnLeaf !== [null]
  );
}

async function fetchDetailData(resultId: number) {
  if (!resultId) return;
  try {
    const res = await fetch(
      `http://localhost:8000/evaluation_results/${resultId}/detail`,
      {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      }
    );
    if (!res.ok) throw new Error("API取得失敗");
    const apiData = await res.json();
    // Merge quantitative and qualitative data based on the logic from
    // EvaluationResultDetail.vue and store them.
    const newDetailData = perspectives.value.map(() => []);
    const newDetailDataQualitative = perspectives.value.map(() => []);

    perspectives.value.forEach((perspective, perspective_idx) => {
      const perspectiveKey = toJapanesePerspective(perspective) || perspective;
      const items = apiData[perspectiveKey] as any[];
      if (!items) return;

      // quantitative
      if (Array.isArray(items[0])) {
        newDetailData[perspective_idx] = items[0].map(
          (item: any, i: number) => ({
            id: i + 1,
            secondGoal:
              item.type === "quantitative"
                ? item.secondGoal?.[0] ?? item.secondGoal
                : item.secondGoal,
            gsnLeaf:
              item.type === "quantitative"
                ? item.gsnLeaf?.[0] ?? item.gsnLeaf
                : item.gsnLeaf,
            category:
              item.type === "quantitative"
                ? t("quantitative")
                : t("qualitative"),
            question: item.question,
            answer: item.answer,
            score: item.score,
            metadata:
              typeof item.metadata === "object"
                ? JSON.stringify(item.metadata)
                : item.metadata,
          })
        );
      } else {
        newDetailData[perspective_idx] = [];
      }

      // qualitative
      newDetailDataQualitative[perspective_idx] = items
        .map((item: any, i: number) => ({
          id: i + 1,
          secondGoal: item.secondGoal,
          gsnLeaf: item.gsnLeaf,
          category: t("qualitative"),
          question: item.question,
          answer: item.answer,
          score: item.score,
          metadata:
            typeof item.metadata === "object"
              ? JSON.stringify(item.metadata)
              : item.metadata,
        }))
        .filter(
          (item: any) => item.answer !== null && item.answer !== undefined
        );

      // Combining quantitative and qualitative
      newDetailData[perspective_idx] = newDetailData[perspective_idx].concat(
        newDetailDataQualitative[perspective_idx]
      );
    });
    detailData.value = newDetailData;
  } catch (e) {
    detailData.value = perspectives.value.map(() => []);
  }
}

onMounted(() => {
  fetchSummaryAndDetail();
});


async function exportPDF() {
  window.print();
}
</script>

<style scoped>
.container-bg {
  background: #f8f8f8;
  min-height: 100vh;
}
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}
.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
  padding: 1.5rem;
}
.regist-btn {
  background: #1976d2;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 0.7rem 2rem;
  font-size: 1.1rem;
  cursor: pointer;
}
.regist-btn:hover {
  background: #1565c0;
}
.perspective-section {
  margin-bottom: 1.5rem;
  width: 100%;
  margin-left: 0px;
  margin-right: 0px;
  box-sizing: border-box;
  padding-left: 2px;
  padding-right: 2px;
}
.scroll-table-wrapper {
  width: 100%;
  margin-top: 1rem;
  box-sizing: border-box;
  padding-left: 4px;
  padding-right: 4px;
}
.detail-table {
  table-layout: fixed;
  width: 95%;
  padding: 0px;
  margin: 0px;
}
.detail-table th,
.detail-table td {
  border: 1px solid #ddd;
  padding: 0.5rem;
  font-size: 0.9rem;
  word-break: break-all;
  white-space: pre-line;
  overflow-wrap: break-word;
  text-overflow: ellipsis;
  overflow: hidden;
}
.detail-table th {
  background: #f0f0f0;
}
.detail-table tr:nth-child(even) td {
  background: #fafafa;
}
/* Hover effect for table rows */
.detail-table tbody tr:hover td {
  background: #1976d2;
  color: #fff;
}

.detail-table th:nth-child(1) {
  width: 95px;
}
.detail-table td:nth-child(1) {
  width: 95px;
  text-align: left;
}
.detail-table th:nth-child(2) {
  width: 95px;
}
.detail-table td:nth-child(2) {
  width: 95px;
  text-align: left;
}
.detail-table th:nth-child(3),
.detail-table td:nth-child(3) {
  width: 30px;
}
.detail-table th:nth-child(4) {
  width: 95px;
}
.detail-table td:nth-child(4) {
  width: 95px;
  text-align: left;
}
.detail-table th:nth-child(5) {
  width: 520px;
}
.detail-table td:nth-child(5) {
  width: 520px;
  text-align: left;
}
.detail-table th:nth-child(6),
.detail-table td:nth-child(6) {
  width: 30px;
}

/* Apply only when printing. */
@media print {
  .page-break {
    display: block;
    page-break-before: always;
    break-before: page;
  }
  .card,
  .perspective-section {
    page-break-inside: avoid;
    break-inside: avoid;
  }
  .print-hide {
    display: none !important;
  }
}
</style>
