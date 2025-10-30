<template>
  <div class="radar-chart-section">
    <canvas ref="radarChart" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from "vue";
import Chart from "chart.js/auto";
import { useI18n } from "vue-i18n";
import { getPerspectiveListByLocale } from "../utils/perspectiveMapping";

const props = defineProps<{
  charts: Array<{ name: string; radarData: number[] }>;
}>();
const emit = defineEmits(["select"]);
const radarChart = ref<HTMLCanvasElement | null>(null);
let chartInstance: Chart | null = null;

// i18n support: Switch label list based on language
const { locale, t } = useI18n();
const getLabels = () => getPerspectiveListByLocale(locale.value);

// Added: Adjust label length based on window size
function getResponsiveLabels() {
  const width = window.innerWidth;
  const labels = getLabels();
  if (width < 600) {
    // For smartphones, etc.: First 4 characters + …
    return labels.map((l) => (l.length > 4 ? l.slice(0, 4) + "…" : l));
  } else if (width < 900) {
    // For tablets, etc.: First 7 characters + …
    return labels.map((l) => (l.length > 7 ? l.slice(0, 7) + "…" : l));
  } else {
    // For PCs: Full label
    return labels;
  }
}

function renderChart() {
  if (!radarChart.value) return;
  if (chartInstance) chartInstance.destroy();
  const colorPalette = [
    "rgba(54, 162, 235, 0.5)", // blue
    "rgba(255, 99, 132, 0.5)", // red
    "rgba(255, 206, 86, 0.5)", // yellow
    "rgba(75, 192, 192, 0.5)", // green
    "rgba(153, 102, 255, 0.5)", // purple
    "rgba(255, 159, 64, 0.5)", // orange
    "rgba(0, 200, 83, 0.5)", // green2 (for 3rd chart)
  ];
  const borderPalette = [
    "rgba(54, 162, 235, 1)",
    "rgba(255, 99, 132, 1)",
    "rgba(255, 206, 86, 1)",
    "rgba(75, 192, 192, 1)",
    "rgba(153, 102, 255, 1)",
    "rgba(255, 159, 64, 1)",
    "rgba(0, 200, 83, 1)", // green2 (for 3rd chart)
  ];
  chartInstance = new Chart(radarChart.value, {
    type: "radar",
    data: {
      labels: getResponsiveLabels(),
      datasets: props.charts.map((c, i) => ({
        label: c.name,
        data: c.radarData,
        fill: true,
        backgroundColor: colorPalette[i % colorPalette.length],
        borderColor: borderPalette[i % borderPalette.length],
        borderWidth: 3,
        pointBackgroundColor: borderPalette[i % borderPalette.length],
        pointRadius: 3, // smaller
        pointHoverRadius: 5, // smaller
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "top",
          labels: {
            color: "#000",
            font: { size: 16, weight: "bold" },
          },
        },
        title: { display: false },
        tooltip: {
          enabled: true,
          callbacks: {
            title: function (context) {
              return context[0].dataset.label;
            },
            label: function (context) {
              // i18n: Translate label names using the t function
              const labels = getLabels();
              const labelKey = labels[context.dataIndex];
              // Translate using the t function. If no translation exists, display as is
              const labelName =
                t(labelKey) !== labelKey ? t(labelKey) : labelKey;
              const value = context.formattedValue;
              return `${labelName}: ${value}`;
            },
          },
          backgroundColor: "#000",
          titleColor: "#fff",
          bodyColor: "#fff",
          borderColor: "#888",
          borderWidth: 1,
        },
      },
      scales: {
        r: {
          angleLines: { color: "#bbb" },
          grid: { color: "#ddd" },
          pointLabels: {
            color: "#000",
            font: { size: 16, weight: "bold" },
          },
          ticks: {
            display: true, // Hide values
            stepSize: 20,
            backdropColor: "rgba(255,255,255,0.2)",
            z: 1,
          },
          min: 0,
          max: 100,
        },
      },
      onClick: (_event, elements) => {
        if (elements.length > 0) {
          emit("select", elements[0].datasetIndex);
        }
      },
    },
  });
}

onMounted(() => {
  renderChart();
  window.addEventListener("resize", renderChart);
});
// When charts data changes
watch(() => props.charts, renderChart, { deep: true });
// Re-render when language changes
watch(locale, renderChart);
console.log(props);
</script>

<style scoped>
.radar-chart-section {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
canvas {
  max-width: 100%;
  max-height: 350px;
}
</style>
