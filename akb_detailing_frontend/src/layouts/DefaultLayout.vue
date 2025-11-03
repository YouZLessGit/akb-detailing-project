<template>
  <div class="default-layout">
    <header class="header">
      <div class="header-content">
        <RouterLink to="/" class="logo">AKB Detailing</RouterLink>
        <nav class="navigation">
          <RouterLink to="/">Главная</RouterLink>
          <RouterLink to="/booking">Онлайн-запись</RouterLink>
          <RouterLink to="/services">Услуги</RouterLink>
          <RouterLink to="/portfolio">Портфолио</RouterLink>
          <RouterLink to="/blog">Блог</RouterLink>
          <RouterLink to="/about">О нас</RouterLink>
        </nav>
      </div>
    </header>

    <!-- 
      Вот "окно", в котором будут отображаться ваши страницы.
      Оно должно находиться внутри главного контейнера контента.
    -->
    <main class="main-content-area">
      <RouterView />
    </main>

    <footer class="footer">
      <div class="footer-content">
        <p>© {{ new Date().getFullYear() }} AKB Detailing. Все права защищены.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router';
</script>

<style scoped>
.default-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh; /* Занимает всю высоту экрана */
  background-color: #121212;
  color: #f0f0f0;
}

.header {
  background-color: #1e1e1e;
  border-bottom: 1px solid #333;
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #f0f0f0;
  text-decoration: none;
}

.navigation a {
  color: #aaa;
  text-decoration: none;
  margin-left: 1.5rem;
  transition: color 0.3s;
}

.navigation a:hover,
.navigation a.router-link-exact-active {
  color: #007BFF;
}

.main-content-area {
  flex-grow: 1; /* Заставляет main занять всё доступное пространство */
}

.footer {
  background-color: #1e1e1e;
  border-top: 1px solid #333;
  padding: 1.5rem 2rem;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  text-align: center;
  color: #888;
}
</style>