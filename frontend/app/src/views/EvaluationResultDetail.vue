<template>
  <div>
    <Header :breadcrumbs="breadcrumbs" />
    <div>
      <h2>{{ $t("evaluationResultDetail") }}</h2>
      <section style="width: 100%">
        <div style="display: flex; justify-content: center; margin-bottom: 1.5rem; gap: 0rem;">
          <button
            class="regist-btn"
            @click="goToReport"
          >
            {{ $t("reportCreation") }}
          </button>
          <button
            class="regist-btn"
            @click="exportToJson"
          >
            {{  $t("jsonExport") }}
          </button>
        </div>
        <div
          v-for="(perspective, idx) in perspectives"
          :key="idx"
          class="card perspective-section"
        >
          <details class="perspective-details" :open="idx === 0">
            <summary class="perspective-summary">
              {{
                t(perspective) !== perspective ? t(perspective) : perspective
              }}
            </summary>
            <div class="scroll-table-wrapper">
              <table class="detail-table">
                <thead>
                  <tr>
                    <th v-if="showFirstSubgoal(idx)">
                      {{ $t("secondGoal") }}
                    </th>
                    <th v-if="showLeafSubgoal(idx)">{{ $t("gsnLeaf") }}</th>
                    <th>{{ $t("classification") }}</th>
                    <th>{{ $t("question") }}</th>
                    <th>{{ $t("answer") }}</th>
                    <th>{{ $t("score") }}</th>
                    <!-- <th>{{ $t('metadata') }}</th> -->
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
                    <!-- <td>{{ item.metadata }}</td> -->
                  </tr>
                </tbody>
              </table>
            </div>
          </details>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import Header from "../components/Header.vue";
import { useI18n } from "vue-i18n";
import {
  getPerspectiveListByLocale,
  toJapanesePerspective,
} from "../utils/perspectiveMapping";

const route = useRoute();
const router = useRouter();
const { t, locale } = useI18n();

const breadcrumbs = computed(() => [
  { label: t("home"), link: "/" },
  { label: t("evaluatorHomeTitle"), link: "/evaluator-home" },
  { label: t("evaluationResultsSummary"), link: "/eval-result-summary" },
  { label: t("evaluationResultDetail") },
]);
// i18n support: Switch viewpoint list by language
const perspectives = computed(() => getPerspectiveListByLocale(locale.value));

const detailData = ref<any[][]>([]);

async function fetchDetailData() {
  const resultId = route.query.resultId;
  if (!resultId) return;
  const apiUrl = `http://localhost:8000/evaluation_results/${resultId}/detail`;
  try {
    const res = await fetch(apiUrl, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      }
    );
    if (!res.ok) throw new Error("API取得失敗");
    const apiData = await res.json();
    console.log("API:", apiUrl);
    
    console.log("resultId:", resultId);
    console.log("APIから取得した評価結果詳細データ:", apiData);

    // Empty array in order of perspectives list
    const newDetailData = perspectives.value.map(() => []);
    const newDetailDataQualitative = perspectives.value.map(() => []);
    // Mapping API data by perspective name
    interface DetailItem {
      id: number;
      secondGoal: string;
      gsnLeaf: string;
      scoreRate: number;
      gsnName: string;
      category: string;
      question: string;
      answer: string;
      score: number;
      metadata: string;
    }

    interface ApiDetailItem {
      secondGoal: string;
      gsnName: string;
      gsnLeaf: string;
      scoreRate: number;
      type: string;
      question: string;
      answer: string;
      score: number;
      metadata: any;
    }

    console.log("apiData", apiData);

    perspectives.value.forEach(
      (perspective: string, perspective_idx: number): void => {
        // API keys are Japanese so normalize perspective labels
        const perspectiveKey = toJapanesePerspective(perspective) || perspective;
        const items = apiData[perspectiveKey] as ApiDetailItem[];
        if (!items) return;

        // items[0]がリストではない場合 newDetailDataには空の配列を設定
        if (!Array.isArray(items[0])) {
          newDetailData[perspective_idx] = [];
        } else {
          newDetailData[perspective_idx] = items[0].map(
            (item: ApiDetailItem, i: number): DetailItem => ({
              id: i + 1,
              secondGoal:
                item.type === "quantitative"
                  ? (item.secondGoal?.[0] || "")
                  : (item.secondGoal || ""),
              gsnLeaf:
                item.type === "quantitative"
                  ? (item.gsnLeaf?.[0] || "")
                  : (item.gsnLeaf || ""),
              gsnName: (item.gsnName || ""),
              scoreRate: (item.scoreRate || 0.0),
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
        }

        newDetailDataQualitative[perspective_idx] = items.map(
          (item: ApiDetailItem, i: number): DetailItem => ({
            id: i + 1,
            secondGoal: item.secondGoal,
            gsnLeaf: item.gsnLeaf,
            gsnName: item.gsnName,
            scoreRate: item.scoreRate,
            category: t("qualitative"),
            question: item.question,
            answer: item.answer,
            score: item.score,
            metadata:
              typeof item.metadata === "object"
                ? JSON.stringify(item.metadata)
                : item.metadata,
          })
        );
        // newDetailDataQualitativeのanswerがnullかundefineのものは弾く
        newDetailDataQualitative[perspective_idx] = newDetailDataQualitative[
          perspective_idx
        ].filter(
          (item: DetailItem) =>
            item.answer !== null && item.answer !== undefined
        );
        // newDetailDataと直接つなぎ
        newDetailData[perspective_idx] = newDetailData[perspective_idx].concat(
          newDetailDataQualitative[perspective_idx]
        );
      }
    );
    detailData.value = newDetailData;
    console.log("評価結果詳細データ:", detailData.value);
  } catch (e) {
    console.error("評価結果詳細データ取得失敗", e);
  }
}

function goToReport() {
  if (route.query.resultId) {
    router.push({ path: "/report", query: { resultId: route.query.resultId } });
  }
}

async function exportToJson() {
  try {

    // jsonDataを整形する
    // id, metadata, gsnNameは削除, 名前の変換: econdGoal->subCategory, gsnLeaf->evaluationContent
    // secondGoal, gsnLeaf, scoreRateは存在しないかも知れないので、存在チェック
    const newJsonData = detailData.value.map((item: any[]) =>
      item.map((detail: any) => {
        return {
          subCategory: detail.secondGoal || "",
          evaluationContent: detail.gsnLeaf || "",
          scoreRate: Array.isArray(detail.scoreRate) ? (detail.scoreRate[0] || 0.0) : (detail.scoreRate || 0.0),
          category: detail.category,
          question: detail.question,
          answer: detail.answer,
          score: detail.score,
        };
      })
    );
    // この時点で10観点の詳細がlen==10の配列になっている

    console.log("Exporting JSON file:", newJsonData);

    const a_scores_promise = await fetch(
        `http://localhost:8000/evaluation_results/${route.query.resultId}/10perspective_scores`,
        {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        }
      );
    const a_scores = await a_scores_promise.json();
    console.log("Exported scores:", a_scores);

    const res = await fetch("http://localhost:8000/evaluation_results/");
    const all_results  = await res.json();
    const result = all_results.find((r: any) => String(r.id) === String(route.query.resultId));
    console.log("Exported results:", result);

    // tenPerspectivesという変数は10観点の名前、スコア、詳細リストをもつlen==10の配列
    const tenPerspectives = perspectives.value.map((perspective: string, idx: number) => {
      return {
        perspective: perspective,
        totalScore: a_scores[perspective] || 0,
        results: newJsonData[idx] || [],
      };
    });
    console.log("tenPerspectives:", tenPerspectives);
    

    const finalJson = {
      "evaluationResultName": result.name,
      "targetModelName": result.target_ai_model_name,
      "judgeModelName": result.evaluator_ai_model_name,
      "evaluationName": result.evaluation_name,
      "evaluatedDate": result.created_date,
      "tenPerspectives": tenPerspectives,
    }

    console.log("Final JSON structure:", finalJson);
    
    // detailData.valueをJSON形式に変換
    // const jsonData = JSON.stringify(detailData.value, null, 2);

    // Blobオブジェクトを作成
    const blob = new Blob([JSON.stringify(finalJson, null, 2)], { type: "application/json" });

    // ダウンロード用のURLを作成
    const url = URL.createObjectURL(blob);

    // ダウンロード用のリンクを作成
    const link = document.createElement("a");
    link.href = url;
    link.download = `evaluation_detail_${
      route.query.resultId || "data"
    }_${new Date().toISOString().slice(0, 19).replace(/:/g, "-")}.json`;

    // リンクをクリックしてダウンロードを実行
    document.body.appendChild(link);
    link.click();

    // クリーンアップ
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    console.log("JSONファイルをエクスポートしました");
  } catch (error) {
    console.error("JSONエクスポートに失敗しました:", error);
  }
}

// --- Display decision function for subgoal columns ---
function showFirstSubgoal(idx: number) {
  const arr = (detailData.value[idx] as any[]) || [];
  return arr.some((item) => item.secondGoal && item.secondGoal !== "");
}
function showLeafSubgoal(idx: number) {
  const arr = (detailData.value[idx] as any[]) || [];
  return arr.some((item) => item.gsnLeaf && item.gsnLeaf !== "");
}

onMounted(() => {
  fetchDetailData();
});
</script>

<style scoped>
.perspective-section {
  margin-bottom: 1.5rem;
  width: 90%;
  margin-right: auto;
  margin-left: auto;
}
.perspective-details {
  width: 100%;
}
.perspective-summary {
  font-size: 1.2rem;
  font-weight: bold;
  color: var(--color-text-accent);
  cursor: pointer;
  padding: 0.5rem 0;
}
.scroll-table-wrapper {
  overflow-x: auto;
  margin-top: 1rem;
}
.detail-table {
  width: 95%;
}
.detail-table th:nth-child(1) {
  width: 110px;
}
.detail-table td:nth-child(1) {
  width: 110px;
  text-align: left;
}
.detail-table th:nth-child(2) {
  width: 130px;
}
.detail-table td:nth-child(2) {
  width: 130px;
  text-align: left;
}
.detail-table th:nth-child(3),
.detail-table td:nth-child(3) {
  width: 40px;
}
.detail-table th:nth-child(4) {
  width: 160px;
}
.detail-table td:nth-child(4) {
  width: 160px;
  text-align: left;
}
.detail-table th:nth-child(5) {
  width: 530px;
}
.detail-table td:nth-child(5) {
  width: 530px;
  text-align: left;
}
.detail-table th:nth-child(6),
.detail-table td:nth-child(6) {
  width: 40px;
}
.detail-table th:nth-child(7),
.detail-table td:nth-child(7) {
  width: 260px;
}
.detail-table th {
  background: var(--color-bg-table-header);
  color: var(--color-text-main);
}
.detail-table td {
  background-color: var(--color-bg-table-row);
  color: var(--color-text-main);
  font-size: 0.9rem;
}
.detail-table tr:hover td {
  background: var(--color-bg-table-row-hover);
  color: var(--color-table-hover-text);
}
</style>
