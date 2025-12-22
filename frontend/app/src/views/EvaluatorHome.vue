<template>
  <div class="container-bg">
    <!-- Header -->
    <Header :breadcrumbs="breadcrumbs" />
    <div class="container">
      <h2>{{ $t("aiEvaluationExecution") }}</h2>
      <div class="card">
        <div class="form-group-row">
          <label>{{ $t("targetAI") }}</label>
          <select v-model="selectedTargetAI">
            <option v-for="model in models" :key="model.id" :value="model.id">
              {{ model.name }}
            </option>
          </select>
        </div>
        <div class="form-group-row">
          <label>{{ $t("judgeAI") }}</label>
          <select v-model="selectedJudgeAI">
            <option v-for="model in models" :key="model.id" :value="model.id">
              {{ model.name }}
            </option>
          </select>
        </div>
        <div class="form-group-row">
          <label>{{ $t("evaluationDefinition") }}</label>
          <select v-model="selectedDefinition">
            <option v-for="def in definitions" :key="def.id" :value="def.id">
              {{ def.name }}
            </option>
          </select>
        </div>
        <div class="form-group-row">
          <label>{{ $t("evaluateName") }}</label>
          <textarea
            v-model="evaluationName"
            rows="1"
            :placeholder="$t('evaluationNamePlaceholder')"
            required
          ></textarea>
        </div>
        <button class="regist-btn" @click="runEvaluation">
          {{ $t("executeEvaluation") }}
        </button>
      </div>
      <div>
        <button
          style="margin-top: 1.5rem"
          class="regist-btn"
          @click="goToModelManagement"
        >
          {{ $t("modelManagementScreen") }}
        </button>
        <button
          style="margin-top: 1.5rem"
          class="regist-btn"
          @click="goToResult"
        >
          {{ $t("viewEvaluationResults") }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import Header from "../components/Header.vue";

const { t } = useI18n();

// Breadcrumbs
const breadcrumbs = [
  { label: "home", link: "/" },
  { label: "evaluatorHomeTitle" },
];

const models = ref<any[]>([]);
const definitions = ref<any[]>([]);

// Retrieve AI model list from API
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
    selectedJudgeAI.value = models.value[0]?.id || null;
  } catch (e) {
    console.error(t("aiModelListGetFailed"), e);
    models.value = [];
  }
}

// Retrieve evaluation definitions from API
async function fetchDefinitions() {
  try {
    const res = await fetch("http://localhost:8000/evaluations", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    const data = await res.json();
    definitions.value = Array.isArray(data.evaluations)
      ? data.evaluations
      : Array.isArray(data)
      ? data
      : [];
    selectedDefinition.value = definitions.value[0]?.id || null;
  } catch (e) {
    console.error(t("evaluationDefinitionListGetFailed"), e);
    definitions.value = [];
  }
}

const selectedTargetAI = ref(models.value[0]?.id || null);
const selectedJudgeAI = ref(models.value[1]?.id || null);
const selectedDefinition = ref(definitions.value[0]?.id || null);
const evaluationName = ref("");

const router = useRouter();

async function runEvaluation() {
  const payload = {
    name: evaluationName.value,
    evaluation_id: selectedDefinition.value,
    target_ai_model_id: selectedTargetAI.value,
    evaluator_ai_model_id: selectedJudgeAI.value,
  };
  try {
    const res = await fetch("http://localhost:8000/evaluation_result", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    console.log("Evaluation request sent:", payload);

    if (!res.ok) throw new Error(t("apiRequestFailed"));
    // Retrieve evaluation execution ID from response
    const resultId = await res.json();

    if (!resultId) throw new Error(t("evaluationIdNotObtained"));
    // Pass evaluation execution ID and AI model ID as query parameters during navigation

    router.push({
      path: "/eval-execution",
      query: {
        resultId: resultId,
        evaluationId: selectedDefinition.value,
        modelId: selectedTargetAI.value,
        judgeModelId: selectedJudgeAI.value,
      },
    });
  } catch (err) {
    alert(t("evaluationExecutionFailed"));
    console.error(err);
  }
}
function goToResult() {
  router.push("/eval-result-summary");
}
function goToModelManagement() {
  router.push("/model-management");
}

onMounted(() => {
  fetchModels();
  fetchDefinitions();
});
</script>

<style scoped>
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
</style>
