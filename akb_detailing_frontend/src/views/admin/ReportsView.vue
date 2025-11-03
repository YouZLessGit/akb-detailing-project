<script setup>
import { ref, computed, onMounted } from 'vue'; // <-- ИСПРАВЛЕНИЕ ЗДЕСЬ
import axios from 'axios';

const reportData = ref(null);
const isLoading = ref(false);
const error = ref(null);

// Даты для фильтра (по умолчанию текущий месяц)
const getMonthRange = () => {
    const today = new Date();
    const start = new Date(today.getFullYear(), today.getMonth(), 1);
    const end = new Date(today.getFullYear(), today.getMonth() + 1, 0); // Последний день текущего месяца
    return {
        start: start.toISOString().split('T')[0],
        end: end.toISOString().split('T')[0]
    };
};
const dateRange = ref(getMonthRange());

const generateReport = async () => {
    isLoading.value = true;
    error.value = null;
    reportData.value = null;
    try {
        // Добавляем время к датам, чтобы включить весь день
        const startDate = `${dateRange.value.start}T00:00:00Z`;
        const endDate = `${dateRange.value.end}T23:59:59Z`;

        const response = await axios.get(`http://localhost:8000/api/reports/profit_summary/?start_date=${startDate}&end_date=${endDate}`);
        reportData.value = response.data;
    } catch (err) {
        error.value = "Не удалось сгенерировать отчет.";
        console.error(err);
    } finally {
        isLoading.value = false;
    }
};

// --- Computed свойства для общей сводки ---
const overallSummary = computed(() => {
    if (!reportData.value) return { revenue: 0, cost: 0, profit: 0, orders: 0 };
    return reportData.value.reduce((acc, employee) => {
        acc.revenue += employee.total_revenue;
        acc.cost += employee.total_material_cost;
        acc.profit += employee.total_profit;
        acc.orders += employee.completed_orders_count;
        return acc;
    }, { revenue: 0, cost: 0, profit: 0, orders: 0 });
});

// Форматирование валюты
const formatCurrency = (value) => {
    if (typeof value !== 'number') {
        value = 0;
    }
    return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'BYN', minimumFractionDigits: 2 }).format(value);
}

// Отслеживание раскрытых деталей по сотрудникам
const expandedEmployee = ref(null);
const toggleDetails = (employeeId) => {
    expandedEmployee.value = expandedEmployee.value === employeeId ? null : employeeId;
};

// Запускаем отчет при первой загрузке
onMounted(generateReport);
</script>

<template>
  <div class="reports-view">
    <h1>Отчет по прибыли</h1>

    <div class="filter-panel">
      <div class="date-inputs">
        <label for="start-date">Начало периода</label>
        <input type="date" id="start-date" v-model="dateRange.start">
        <label for="end-date">Конец периода</label>
        <input type="date" id="end-date" v-model="dateRange.end">
      </div>
      <button @click="generateReport" :disabled="isLoading">
        {{ isLoading ? 'Загрузка...' : 'Сформировать отчет' }}
      </button>
    </div>

    <div v-if="isLoading" class="loading-message">Формирование отчета...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="reportData" class="report-content">
      <!-- Общая сводка -->
      <div class="summary-grid">
        <div class="summary-card profit">
          <span class="label">Общая прибыль</span>
          <span class="value">{{ formatCurrency(overallSummary.profit) }}</span>
        </div>
        <div class="summary-card">
          <span class="label">Общая выручка</span>
          <span class="value">{{ formatCurrency(overallSummary.revenue) }}</span>
        </div>
        <div class="summary-card">
          <span class="label">Себестоимость материалов</span>
          <span class="value">{{ formatCurrency(overallSummary.cost) }}</span>
        </div>
        <div class="summary-card">
          <span class="label">Выполнено заказов</span>
          <span class="value">{{ overallSummary.orders }}</span>
        </div>
      </div>

      <!-- Детализация по сотрудникам -->
      <h2>Детализация по сотрудникам</h2>
      <div v-if="reportData.length === 0" class="no-data">За выбранный период нет выполненных заказов.</div>
      <div v-else class="employee-list">
        <div v-for="employee in reportData" :key="employee.employee_id" class="employee-card">
          <div class="employee-summary" @click="toggleDetails(employee.employee_id)">
            <strong class="name">{{ employee.employee_name }}</strong>
            <div class="stats">
              <span>Прибыль: <strong>{{ formatCurrency(employee.total_profit) }}</strong></span>
              <span>Заказов: <strong>{{ employee.completed_orders_count }}</strong></span>
            </div>
            <span class="toggler">{{ expandedEmployee === employee.employee_id ? '▲' : '▲' }}</span>
          </div>
          
          <div v-if="expandedEmployee === employee.employee_id" class="employee-details">
            <h4>Выполненные заказы:</h4>
            <table>
              <thead>
                <tr>
                  <th>Дата</th>
                  <th>Клиент</th>
                  <th>Выручка</th>
                  <th>Расход</th>
                  <th>Прибыль</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="order in employee.orders_details" :key="order.order_id">
                  <td>{{ new Date(order.start_time).toLocaleDateString('ru-RU') }}</td>
                  <td>{{ order.client_name }}</td>
                  <td>{{ formatCurrency(order.revenue) }}</td>
                  <td>{{ formatCurrency(order.material_cost) }}</td>
                  <td>{{ formatCurrency(order.profit) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reports-view h1 {
  border-bottom: 2px solid #ddd;
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
}
.filter-panel { 
    display: flex; 
    gap: 1rem; 
    align-items: center; 
    background-color: #fff; 
    padding: 1rem; 
    border-radius: 8px; 
    margin-bottom: 2rem; 
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.date-inputs {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}
.summary-grid { 
    display: grid; 
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
    gap: 1rem; 
    margin-bottom: 2rem; 
}
.summary-card { 
    background-color: #fff; 
    padding: 1.5rem; 
    border-radius: 8px; 
    display: flex; 
    flex-direction: column;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.summary-card.profit { 
    background-color: #e0f2fe; 
    border-left: 5px solid #0ea5e9;
}
.summary-card .label { 
    font-size: 0.9rem; 
    color: #64748b; 
    margin-bottom: 0.5rem;
}
.summary-card .value { 
    font-size: 1.8rem; 
    font-weight: 600; 
    color: #1e293b;
}
.employee-list { 
    display: flex; 
    flex-direction: column; 
    gap: 1rem; 
}
.employee-card { 
    background-color: #fff; 
    border-radius: 8px; 
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    transition: box-shadow 0.2s;
}
.employee-card:hover {
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.employee-summary { 
    display: flex; 
    align-items: center; 
    padding: 1rem 1.5rem; 
    cursor: pointer; 
}
.employee-summary .name { 
    flex-grow: 1; 
    font-size: 1.1rem; 
    font-weight: 500;
}
.employee-summary .stats { 
    display: flex; 
    gap: 1.5rem; 
    color: #475569;
}
.employee-summary .stats strong {
    color: #1e293b;
}
.toggler {
    margin-left: 1.5rem;
    color: #94a3b8;
}
.employee-details { 
    padding: 0 1.5rem 1.5rem 1.5rem; 
    border-top: 1px solid #f1f5f9;
}
table { 
    width: 100%; 
    border-collapse: collapse; 
    margin-top: 1rem;
}
th, td { 
    text-align: left; 
    padding: 0.75rem; 
    border-bottom: 1px solid #f1f5f9; 
}
th { 
    color: #64748b; 
    font-size: 0.8rem;
    text-transform: uppercase;
}
.loading-message, .error-message, .no-data {
    text-align: center;
    padding: 2rem;
    background-color: #fff;
    border-radius: 8px;
    color: #64748b;
}
.error-message {
    color: #ef4444;
}
</style>