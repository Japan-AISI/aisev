<template>
  <div class="container-bg">
    <Header :breadcrumbs="breadcrumbs" />
    <div class="container">
      <section class="card">
        <h2>{{ $t("questionList") }}</h2>
        <div class="table-header">
          <button
            class="delete-btn"
            :disabled="selectedQuestionId === null"
            @click="deleteSelectedQuestion"
          >
            {{ $t("deleteBtn") }}
          </button>
        </div>
        <table class="eval-table">
          <thead>
            <tr>
              <th></th>
              <th>{{ $t("questionName") }}</th>
              <th>{{ $t("evaluationPerspective") }}</th>
              <th>{{ $t("questionCount") }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="q in pagedQuestions" :key="q.id">
              <td>
                <input
                  type="radio"
                  name="selectedQuestion"
                  :value="q.id"
                  v-model="selectedQuestionId"
                />
              </td>
              <td>{{ q.name }}</td>
              <td>{{ q.perspective }}</td>
              <td>{{ q.contents.length }}</td>
            </tr>
          </tbody>
        </table>
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

      <hr class="section-divider" />

      <section class="card quantatigve_card">
        <h2>{{ $t("questionCreation") }}</h2>
        <form @submit.prevent="addQuestion">
          <div>
            <label class="form-label">{{ $t("questionName") }}：</label>
            <input
              style="margin-left: 35px; margin-bottom: 20px"
              v-model="newQuestion.name"
              class="eval-name-input"
              required
            />
          </div>
          <div class="form-group-row">
            <label class="form-label" style="display: block; top: 0ch"
              >{{ $t("evaluationPerspective") }}：</label
            >
            <select v-model="newQuestion.perspective" required>
              <option v-for="c in criteria" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div class="form-group-row-qualitative">
            <label class="form-label">{{ $t("questionContent") }}：</label>
            <div style="flex: 1">
              <div
                v-for="(_, idx) in newQuestion.contents"
                :key="idx"
                style="margin-bottom: 8px"
              >
                <textarea
                  v-model="newQuestion.contents[idx]"
                  rows="2"
                  class="content-textarea"
                ></textarea>
              </div>
              <button
                type="button"
                class="regist-btn textarea-add-btn"
                @click="addContent"
              >
                {{ $t("addContent") }}
              </button>
            </div>
          </div>
          <button type="submit" class="regist-btn" style="margin-top: 50px">
            {{ $t("create") }}
          </button>
        </form>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from "vue";
import { useI18n } from "vue-i18n";
import Header from "../components/Header.vue";
import {
  getPerspectiveListByLocale,
  toEnglishPerspective,
  toJapanesePerspective,
} from "../utils/perspectiveMapping";

const { t, locale } = useI18n();

const breadcrumbs = [
  { label: "home", link: "/" },
  { label: "evaluationDefinerHomeTitle", link: "/definer-home" },
  { label: "qualitativeDefinitionScreen" },
];

const criteria = computed(() => getPerspectiveListByLocale(locale.value));

let nextId = 1;

interface Question {
  id: number;
  name: string;
  perspective: string;
  contents: string[];
}

const questions = ref<Question[]>([]);
const selectedQuestionId = ref<number | null>(null);

const newQuestion = ref({
  name: "",
  perspective: "",
  contents: [""],
});

watch(criteria, (newCriteria: string[]) => {
  if (newCriteria.length > 0 && !newQuestion.value.perspective) {
    newQuestion.value.perspective = newCriteria[0];
  }
});

watch(
  () => locale.value,
  (newLocale) => {
    if (!newQuestion.value.perspective) return;
    newQuestion.value.perspective = newLocale.startsWith("en")
      ? toEnglishPerspective(newQuestion.value.perspective) ||
        newQuestion.value.perspective
      : toJapanesePerspective(newQuestion.value.perspective) ||
        newQuestion.value.perspective;
  }
);

const localizedQuestions = computed(() =>
  questions.value.map((q: Question) => ({
    ...q,
    perspective: locale.value.startsWith("en")
      ? toEnglishPerspective(q.perspective) || q.perspective
      : toJapanesePerspective(q.perspective) || q.perspective,
  }))
);

const itemsPerPage = 5;
const currentPage = ref(1);

const pagedQuestions = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return localizedQuestions.value.slice(start, start + itemsPerPage);
});

const totalPages = computed(() =>
  Math.ceil(localizedQuestions.value.length / itemsPerPage)
);

async function fetchQuestions() {
  try {
    const response = await fetch("http://localhost:8000/qualitative_datasets", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    if (!response.ok) throw new Error(t("apiGetFailed"));
    const data = await response.json();
    questions.value = Array.isArray(data.qualitative_datasets)
      ? data.qualitative_datasets
      : Array.isArray(data)
      ? data
      : [];
    if (questions.value.length > 0) {
      nextId = Math.max(...questions.value.map((q: Question) => q.id)) + 1;
    } else {
      nextId = 1;
    }
    console.log("Fetched questions:", JSON.stringify(questions.value, null, 2));
  } catch (err) {
    console.error(err);
    window.alert(t("questionListGetFailed"));
  }
}

onMounted(() => {
  fetchQuestions();
  if (criteria.value.length > 0) {
    newQuestion.value.perspective = criteria.value[0];
  }
});

function goToPage(page: number) {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
}

function addContent() {
  newQuestion.value.contents.push("");
}

function addQuestion() {
  if (
    !newQuestion.value.name ||
    !newQuestion.value.perspective ||
    newQuestion.value.contents.length === 0
  )
    return;

  const payload = {
    name: newQuestion.value.name,
    criterion:
      toJapanesePerspective(newQuestion.value.perspective) ||
      newQuestion.value.perspective,
    contents: newQuestion.value.contents.filter((c: string) => c.trim() !== ""),
  };
  console.log("Add data:", JSON.stringify(payload, null, 2));
  fetch("http://localhost:8000/qualitative_dataset", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Origin: "http://localhost:8080",
      "Access-Controll-Request": "POST",
    },
    body: JSON.stringify(payload),
  })
    .then((res) => {
      if (!res.ok) throw new Error(t("registrationFailed"));
      return res.json();
    })
    .then(() => {
      window.alert(t("creationCompleted"));
      newQuestion.value.name = "";
      newQuestion.value.perspective = criteria.value[0] || "";
      newQuestion.value.contents = [""];
      fetchQuestions();
    })
    .catch((err) => {
      console.error(err);
      window.alert(t("creationFailed"));
    });
}

function deleteSelectedQuestion() {
  if (selectedQuestionId.value === null) {
    window.alert(t("noQuestionSelected"));
    return;
  }
  const confirmed = window.confirm(t("confirmDelete"));
  if (!confirmed) return;
  console.log("data:", { id: selectedQuestionId.value });
  fetch(
    `http://localhost:8000/qualitative_datasets/${selectedQuestionId.value}`,
    {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
    }
  )
    .then((res) => {
      if (!res.ok) throw new Error(t("deletionFailedQualitative"));
      return res.json();
    })
    .then(() => {
      window.alert(t("deletionCompleted"));
      selectedQuestionId.value = null;
      fetchQuestions();
    })
    .catch((err) => {
      console.error(err);
      window.alert(t("deletionFailedQualitative"));
    });
}

const totalQuestions = computed(() => questions.value.length);
const quantitativeQuestions = computed(() => []);
const qualitativeQuestions = computed(() => []);

const registerQuestions = () => {
  window.alert("Not implemented");
};
</script>

<style scoped>
/* table */
.eval-table tr:last-child td {
  border-bottom: none;
}
.eval-table th:nth-child(2),
.eval-table td:nth-child(2) {
  min-width: 220px;
  width: 30%;
  text-align: left;
}
.eval-table th:nth-child(4),
.eval-table td:nth-child(4) {
  width: auto;
  min-width: 120px;
  text-align: left;
  overflow-wrap: break-word;
}
.eval-table th:not(:nth-child(4)),
.eval-table td:not(:nth-child(4)) {
  white-space: nowrap;
  width: auto;
}

/* card */
.quantatigve_card {
  width: 70%;
  margin-left: auto;
  margin-right: auto;
}

select {
  width: 100%;
  max-width: 250px;
  padding: 8px;
  background-color: var(--color-bg-input);
  color: var(--color-input-text);
  border-radius: 4px;
  border: 1px solid var(--color-border);
  margin-top: 0.5rem;
}

.content-textarea {
  width: 100%;
  min-height: 2.5em;
  max-width: 600px;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
  background-color: var(--color-bg-main);
  color: var(--color-text-main);
  resize: vertical;
  font-size: 1em;
}

.textarea-add-btn {
  border: var(--color-border);
  background-color: var(--color-bg-accent);
  color: var(--color-text-main);
}

/* form-group-row adjustment */
.form-group-row-qualitative {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}
.form-group-row-qualitative label {
  min-width: 90px;
  font-weight: bold;
  margin-bottom: 0;
}
.form-group-row-qualitative select,
.form-group-row-qualitative > div {
  flex: 1;
}
</style>
