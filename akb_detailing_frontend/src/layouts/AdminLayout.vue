<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'

const router = useRouter()

const logout = () => {
  sessionStorage.removeItem('user-token')
  sessionStorage.removeItem('user-data') // <-- Не забудьте очистить
  router.push('/login')
}
</script>
<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <h2>CRM "AKB Detailing"</h2>
      <nav>
        <RouterLink to="/admin/dashboard">Главная</RouterLink>
        <RouterLink to="/admin/services">Управление услугами</RouterLink>
        <RouterLink to="/admin/clients">Клиенты</RouterLink>
        <RouterLink to="/admin/calendar">Календарь</RouterLink>
        <RouterLink to="/admin/employees">Сотрудники</RouterLink>
        <RouterLink to="/admin/inventory">Склад</RouterLink>
        <RouterLink to="/admin/portfolio">Портфолио</RouterLink>
        <RouterLink to="/admin/blog">Блог</RouterLink>
        <!-- 
          ---
          ВОТ ДОБАВЛЕННАЯ ССЫЛКА
          ---
        -->
        <RouterLink to="/admin/about">Страница "О нас"</RouterLink>
        <RouterLink to="/admin/reports">Отчеты</RouterLink>
      </nav>
      <button @click="logout" class="logout-btn">Выход</button>
    </aside>
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>
<style scoped> /* Стили только для админки */
.admin-layout { display: flex; height: 100vh; }
.sidebar {
  width: 250px;
  background-color: #2c3e50;
  color: white;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}
.sidebar h2 { text-align: center; }
.sidebar nav {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  margin-top: 2rem;
}
.sidebar nav a {
  color: white;
  padding: 0.75rem;
  text-decoration: none;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}
.sidebar nav a:hover, .sidebar nav a.router-link-exact-active {
  background-color: #34495e;
}
.logout-btn { background-color: #e74c3c; color: white; border: none; padding: 0.75rem; cursor: pointer; }
.content { flex-grow: 1; padding: 2rem; overflow-y: auto; background-color: #f4f6f9; }
</style>