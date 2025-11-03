<!-- akb_detailing_frontend/src/views/ServicesView.vue -->
<template>
  <div class="page-container">
    <div class="header-section">
      <h1>Каталог услуг</h1>
    </div>

    <div v-if="isLoading" class="loader">Загрузка...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>

    <div v-else-if="topLevelCategories.length > 0" class="grid">
      <!-- 
        ИСПРАВЛЕНИЕ: v-for вынесен на тег <template>, который оборачивает 
        элемент с v-if. Это правильный паттерн для Vue 3, который гарантирует,
        что переменная `cat` будет создана циклом *перед* тем, как v-if 
        попытается ее использовать.
      -->
      <template v-for="cat in topLevelCategories" :key="cat._id">
        <RouterLink 
          v-if="cat && cat.slug"
          :to="`/services/category/${cat.slug}`"
          class="card"
        >
          <img v-if="cat.main_image_url" :src="cat.main_image_url" class="card-image">
          <div v-else class="card-image-placeholder">AKB</div>
          <div class="card-content">
            <h3>{{ cat.name }}</h3>
          </div>
        </RouterLink>
      </template>
    </div>
    
    <div v-else class="empty-state">
      <p>Категории услуг еще не созданы.</p>
      <p>Пожалуйста, добавьте родительские категории в админ-панели.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink } from 'vue-router';
import axios from 'axios';

const topLevelCategories = ref([]);
const isLoading = ref(true);
const error = ref(null);

onMounted(async () => {
  try {
    // Этот URL корректен после предыдущих исправлений
    const response = await axios.get('http://localhost:8000/api/public/services/');
    topLevelCategories.value = response.data;
  } catch(err) {
    error.value = "Не удалось загрузить каталог.";
    console.error(err);
  } finally {
    isLoading.value = false;
  }
});
</script>

<style scoped>
.page-container { max-width: 1200px; margin: 40px auto; padding: 0 20px; color: #f0f0f0; }
.header-section { text-align: center; margin-bottom: 60px; }
.header-section h1 { font-size: 3rem; margin-bottom: 10px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 25px; }
.card {
  background-color: #2a2a2a; border: 1px solid #444; border-radius: 8px; text-decoration: none;
  color: #f0f0f0; display: flex; flex-direction: column; overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
}
.card:hover { transform: translateY(-8px); box-shadow: 0 10px 20px rgba(0, 123, 255, 0.2); border-color: #007BFF; }
.card-image { width: 100%; height: 220px; object-fit: cover; }
.card-image-placeholder { 
    width: 100%; height: 220px; background-color: #333; display: flex; align-items: center; 
    justify-content: center; font-size: 2rem; font-weight: bold; color: #555;
}
.card-content { padding: 25px; flex-grow: 1; text-align: center; }
.card h3 { margin: 0; font-size: 1.6rem; }
.loader, .error-message, .empty-state {
  text-align: center; padding: 50px 20px; font-size: 1.2rem; color: #aaa;
}
.error-message { color: #ff4d4d; }
.empty-state p { margin: 5px 0; }
</style>