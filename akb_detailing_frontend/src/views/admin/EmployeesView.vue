<!-- src/views/admin/EmployeesView.vue -->
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const employees = ref([]);
const newEmployee = ref({
  full_name: '',
  username: '',
  password: '',
  role: 'Detailer' // Роль по умолчанию
});
const isLoading = ref(true);
const availableRoles = ['Admin', 'Detailer', 'Manager'];

const fetchEmployees = async () => {
  isLoading.value = true;
  try {
    const response = await axios.get('http://localhost:8000/api/employees/');
    employees.value = response.data;
  } catch (error) {
    alert('Не удалось загрузить список сотрудников.');
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};

const addEmployee = async () => {
  if (!newEmployee.value.full_name || !newEmployee.value.username || !newEmployee.value.password || !newEmployee.value.role) {
    alert('Все поля обязательны для заполнения!');
    return;
  }
  try {
    // Используем эндпоинт, который мы определили в urls.py
    await axios.post('http://localhost:8000/api/employees/create/', newEmployee.value);
    newEmployee.value = { full_name: '', username: '', password: '', role: 'Detailer' };
    await fetchEmployees(); // Обновляем список
  } catch (error) {
    const errorMsg = error.response?.data?.error || 'Произошла ошибка при добавлении сотрудника.';
    alert(errorMsg);
    console.error(error);
  }
};

onMounted(fetchEmployees);
</script>

<template>
  <div class="employees-view">
    <h1>Управление сотрудниками</h1>
    
    <div class="form-container">
      <h2>Добавить нового сотрудника</h2>
      <form @submit.prevent="addEmployee">
        <div class="form-group">
          <label for="fullName">ФИО</label>
          <input type="text" id="fullName" v-model="newEmployee.full_name" required>
        </div>
        <div class="form-group">
          <label for="username">Логин (для входа)</label>
          <input type="text" id="username" v-model="newEmployee.username" required>
        </div>
        <div class="form-group">
          <label for="password">Пароль</label>
          <input type="password" id="password" v-model="newEmployee.password" required>
        </div>
        <div class="form-group">
          <label for="role">Должность</label>
          <select id="role" v-model="newEmployee.role" required>
            <option v-for="role in availableRoles" :key="role" :value="role">{{ role }}</option>
          </select>
        </div>
        <button type="submit">Добавить сотрудника</button>
      </form>
    </div>

    <hr>

    <h2>Список сотрудников</h2>
    <div v-if="isLoading">Загрузка...</div>
    <ul v-else class="employees-list">
      <li v-for="employee in employees" :key="employee._id">
        <div class="employee-info">
          <strong>{{ employee.full_name }}</strong> ({{ employee.username }})
        </div>
        <div class="employee-role">
          <span>{{ employee.role }}</span>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
/* Стили похожи на другие страницы админки для консистентности */
.employees-view { max-width: 900px; margin: 0 auto; padding: 1.5rem; }
h1, h2 { border-bottom: 1px solid #eee; padding-bottom: 0.5rem; margin-bottom: 1.5rem; }
.form-container { background-color: #f9f9f9; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: bold; }
.form-group input, .form-group select { width: 100%; padding: 0.75rem; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
button[type="submit"] { background-color: #007bff; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 4px; cursor: pointer; }
hr { margin: 3rem 0; border: 0; border-top: 1px solid #eee; }
.employees-list { list-style: none; padding: 0; }
.employees-list li { display: flex; justify-content: space-between; align-items: center; padding: 1rem; border-bottom: 1px solid #eee; }
.employee-role span { background-color: #e2e8f0; color: #4a5568; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 500; }
</style>