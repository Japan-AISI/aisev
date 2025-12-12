<template>
  <div class="container-bg">
    <Header :breadcrumbs="breadcrumbs" />
    <main class="container">
      <!-- Quantitative evaluation status display area -->
      <section class="card">
        <h2>{{ $t("evaluationExecution.quantitativeEvaluation") }}</h2>
        <div class="status-area">
          <div
            v-if="quantitativeStatus === 'running'"
            class="loading-container"
          >
            <div class="spinner"></div>
            <span>{{ $t("evaluationExecution.evaluationRunning") }}</span>
          </div>
          <span v-else-if="quantitativeStatus === 'done'">{{
            $t("evaluationExecution.evaluationDone")
          }}</span>
          <span v-else>{{ $t("evaluationExecution.evaluationFetching") }}</span>
        </div>
      </section>

      <!-- Qualitative Evaluation Area -->
      <section class="card">
        <h2>{{ $t("evaluationExecution.qualitativeEvaluation") }}</h2>
        <div class="model-name-area">
          <span v-if="modelName"
            >{{ $t("evaluationExecution.aiModelName") }}{{ modelName }}</span
          >
          <span v-else>{{
            $t("evaluationExecution.aiModelNameFetching")
          }}</span>
        </div>
        <div>
          <div v-for="(q, idx) in questions" :key="q.id" class="question-block">
            <span class="question-label">{{
              q.text.replace(/^質問\d+：/, "")
            }}</span>
            <div class="answer-group">
              <label>
                <input
                  type="radio"
                  :name="'answer-' + q.id"
                  value="implemented"
                  v-model="answers[idx]"
                />
                {{ $t("evaluationExecution.implemented") }}
              </label>
              <label>
                <input
                  type="radio"
                  :name="'answer-' + q.id"
                  value="partially_implemented"
                  v-model="answers[idx]"
                />
                {{ $t("evaluationExecution.partiallyImplemented") }}
              </label>
              <label>
                <input
                  type="radio"
                  :name="'answer-' + q.id"
                  value="not_implemented"
                  v-model="answers[idx]"
                />
                {{ $t("evaluationExecution.notImplemented") }}
              </label>
              <label>
                <input
                  type="radio"
                  :name="'answer-' + q.id"
                  value="not_applicable"
                  v-model="answers[idx]"
                />
                {{ $t("evaluationExecution.notApplicable") }}
              </label>
            </div>
          </div>
        </div>
        <button class="regist-btn" @click="registerQualitativeResult">
          {{ $t("evaluationExecution.qualitativeResultRegister") }}
        </button>
      </section>

      <div v-if="quantitativeStatus === 'done' && qualitativeDone">
        <button class="regist-btn" @click="goToResult">
          {{ $t("evaluationExecution.evaluationResultDisplay") }}
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import Header from "../components/Header.vue";

// Receive parameters (obtained from the previous screen)
const route = useRoute();
const router = useRouter();
const evaluationId = ref(
  route.params.evaluationId || route.query.evaluationId || ""
);
const resultId = ref(route.params.resultId || route.query.resultId || "");
const modelId = ref(route.params.modelId || route.query.modelId || "");
const judgeModelId = ref(route.params.judgeModelId || route.query.judgeModelId || "");
import { useI18n } from "vue-i18n";

const { t, locale } = useI18n();

const breadcrumbs = ref([
  { label: t("home"), link: "/" },
  { label: t("evaluatorHomeTitle"), link: "/evaluator-home" },
  { label: t("evaluationExecution.evaluationExecutionTitle") },
]);

watch(locale, () => {
  breadcrumbs.value = [
    { label: t("home"), link: "/" },
    { label: t("evaluatorHomeTitle"), link: "/evaluator-home" },
    { label: t("evaluationExecution.evaluationExecutionTitle") },
  ];
});

// Execute quantitative evaluation
const execQuantitativeEvaluation = async () => {
  const requestJson = {
    evaluation_id: evaluationId.value,
    target_ai_model_id: modelId.value,
    evaluator_ai_model_id: judgeModelId.value,
  };
  console.log(
    "execQuantitativeEvaluation request:",
    JSON.stringify(requestJson)
  );
  try {
    const res = await fetch(
      `http://localhost:8000/evaluation_results/${resultId.value}/quantitative_result`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestJson),
      }
    );
    if (!res.ok) throw new Error("定量評価の実行に失敗しました");
    console.log("定量評価を実行しました");
  } catch (e) {
    console.error("定量評価実行エラー:", e);
    alert("定量評価の実行に失敗しました");
  }
};

// Quantitative evaluation status
const quantitativeStatus = ref("running"); // 'running' | 'done' | 'fetching'
let timer = null;

const fetchQuantitativeStatus = async () => {
  // Check status using resultId as the key
  console.log("status:", quantitativeStatus.value);
  if (quantitativeStatus.value != "done") {
    const requestJson = { id: resultId.value };
    console.log(
      "fetchQuantitativeStatus request:",
      JSON.stringify(requestJson)
    );
    try {
      const res = await fetch(
        `http://localhost:8000/evaluation_results/${resultId.value}/status`
      );
      const data = await res.json();
      quantitativeStatus.value = data;
      console.log("fetchQuantitativeStatus response:", data);
    } catch (e) {
      console.error("fetchQuantitativeStatus error:", e);
    }
  }
};

// Periodic retrieval of quantitative evaluation status
onMounted(() => {
  execQuantitativeEvaluation();
  fetchQuantitativeStatus();
  timer = setInterval(async () => {
    await fetchQuantitativeStatus();
    if (quantitativeStatus.value === "done" && timer) {
      clearInterval(timer);
      timer = null;
    }
  }, 10000);
  fetchModelName();
  fetchQuestions();
});
onUnmounted(() => {
  if (timer) clearInterval(timer);
});

// Retrieve AI model name
const modelName = ref("");
const fetchModelName = async () => {
  // API call
  const requestJson = { modelId: modelId.value };
  console.log("fetchModelName request:", JSON.stringify(requestJson));
  try {
    const res = await fetch(`http://localhost:8000/ai_models/${modelId.value}`);
    const data = await res.json();
    modelName.value = data.ai_model.name;
  } catch (e) {
    console.error("fetchModelName error:", e);
  }
};

// Retrieve questions
const questions = ref([]);
const fetchQuestions = async () => {
  // API call
  const requestJson = { evaluationId: evaluationId.value };
  console.log("fetchQuestions request:", JSON.stringify(requestJson));
  try {
    const res = await fetch(
      `http://localhost:8000/qualitative_datasets/by_evaluation/${evaluationId.value}`
    );
    const result = await res.json();
    const datasets = result.qualitative_datasets;
    console.log("datasets:", datasets);
    // Propagate perspective to contents
    const datasetContents = datasets.map((dataset) =>
      dataset.contents.map((content) => ({
        ...content,
        scoreRate: dataset.score_rate,
        secondGoal: dataset.second_goal,
        gsnLeaf: dataset.gsn_leaf,
        gsnName: dataset.name,
        perspective: dataset.perspective,
      }))
    );
    console.log("dataset_contents:", datasetContents);

    // contents: [[{ id: 1, text: "Question 1", perspective: ... }, ...], ...]
    // Flatten all text here
    const flattedContents = datasetContents.flat();
    console.log("flattedContents:", flattedContents);
    // id reassignment
    flattedContents.forEach((item, index) => {
      item.id = index + 1; // Sequential numbering of IDs starting from 1
    });
    console.log("flattedContents with new ids:", flattedContents);
    // Add "Question {id}:" to text
    flattedContents.forEach((item) => {
      item.text = `質問${item.id}：${item.text}`;
    });

    questions.value = flattedContents;
    console.log("questions:", questions.value);

    answers.value = Array(questions.value.length).fill("not_applicable");
  } catch (e) {
    console.error("fetchQuestions error:", e);
    questions.value = [];
    answers.value = [];
  }
};

// Answers
const answers = ref([]);
const qualitativeDone = ref(false);

// Register qualitative evaluation results
const registerQualitativeResult = async () => {
  const results = questions.value.map((q, idx) => ({
    questionId: q.id,
    answer: answers.value[idx],
    text: q.text, // Add
    perspective: q.perspective, // Add
    scoreRate: q.scoreRate, // Add
    secondGoal: q.secondGoal, // Add
    gsnLeaf: q.gsnLeaf, // Add
    gsnName: q.gsnName, // Add
  }));
  const requestJson = {
    evaluationId: evaluationId.value,
    results: results,
  };
  try {
    const res = await fetch(
      `http://localhost:8000/evaluation_results/${resultId.value}/qualitative_result`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestJson),
      }
    );
    console.log(
      "registerQualitativeResult request:",
      JSON.stringify(requestJson)
    );
    console.log("registerQualitativeResult response:", await res.json());

    if (!res.ok) throw new Error("登録に失敗しました");
    qualitativeDone.value = true;
    alert(t("alertQualitativeResultRegistered"));
  } catch (e) {
    alert(t("alertEvaluationExecutionFailed"));
    console.error(e);
  }
};

const goToResult = () => {
  router.push("/eval-result-summary");
};
</script>

<style scoped>
.status-area {
  font-size: 1.3rem;
  font-weight: bold;
  color: var(--color-text-accent);
  margin: 1.5rem 0;
  text-align: center;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.spinner {
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid #f3f3f3;
  border-top: 2px solid var(--color-text-accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
.model-name-area {
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
  color: var(--color-text-main);
}
.question-block {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--color-bg-accent);
  border-radius: 8px;
  color: var(--color-text-main);
  border-color: var(--color-border);
}
.question-label {
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  display: block;
}
.answer-group {
  display: flex;
  gap: 2rem;
  margin-top: 0.5rem;
}
.answer-group label {
  display: flex;
  align-items: center;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  padding: 0.3rem 0.7rem;
  border-radius: 6px;
  transition: background 0.2s;
}
.answer-group label:hover {
  background: #f0f4ff;
}
.answer-group input[type="radio"] {
  appearance: none;
  width: 1.2em;
  height: 1.2em;
  border: 2px solid #666666;
  border-radius: 50%;
  margin-right: 0.5em;
  background: #fff;
  position: relative;
  transition: border-color 0.2s;
  vertical-align: middle;
}
.answer-group input[type="radio"]:checked {
  border-color: #d97706;
  background: #fed7aa;
}
.answer-group input[type="radio"]:after {
  content: "";
  display: block;
  width: 0.6em;
  height: 0.6em;
  border-radius: 50%;
  background: #ea580c;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: opacity 0.2s;
  pointer-events: none;
}
.answer-group input[type="radio"]:checked:after {
  opacity: 1;
}
</style>
