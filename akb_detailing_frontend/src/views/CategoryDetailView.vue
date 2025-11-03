<template>
  <div class="page-container">
    <div v-if="isLoading" class="loader">Загрузка...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="pageData" class="content">
      <div class="header-section">
        <h1>{{ pageData.category.name }}</h1>
        <p v-if="pageData.category.description">{{ pageData.category.description }}</p>
      </div>
      
      <div class="grid">
        <RouterLink 
          v-for="service in pageData.services" 
          :key="service._id" 
          :to="`/service/${service.slug}`" 
          class="card"
        >
           <img v-if="service.main_image_url" :src="service.main_image_url" class="card-image">
           <div v-else class="card-image-placeholder">AKB</div>
           <div class="card-content">
              <h3>{{ service.name }}</h3>
              <p>{{ service.short_description }}</p>
              <div class="card-footer">
                  <span class="price">от {{ service.price_from }} BYN</span>
                  <span class="details-link">Подробнее →</span>
              </div>
           </div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
// Скрипт из предыдущего ответа полностью корректен, здесь нет изменений
import { ref, onMounted, watch } from 'vue';
import { useRoute, RouterLink } from 'vue-router';
import axios from 'axios';
const route = useRoute();
const pageData = ref(null);
const isLoading = ref(true);
const error = ref(null);
const fetchCategoryData = async (slug) => {
  if (!slug) return;
  isLoading.value = true;
  error.value = null;
  pageData.value = null;
  try {
    const response = await axios.get(`http://localhost:8000/api/public/service-category/${slug}/`);
    pageData.value = response.data;
  } catch (err) {
    error.value = "Не удалось загрузить данные категории."
  } finally {
    isLoading.value = false;
  }
};
onMounted(() => fetchCategoryData(route.params.slug));
watch(() => route.params.slug, (newSlug) => fetchCategoryData(newSlug));
</script>

<style scoped>
/* Используются те же стили, что и в ServicesView, но с добавлением футера карточки */
.page-container { max-width: 1200px; margin: 40px auto; padding: 0 20px; color: #f0f0f0; }
.header-section { text-align: center; margin-bottom: 60px; }
.header-section h1 { font-size: 3rem; margin-bottom: 10px; }
.header-section p { font-size: 1.2rem; color: #aaa; max-width: 700px; margin: 0 auto; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 25px; }
.card {
  background-color: #2a2a2a; border: 1px solid #444; border-radius: 8px; text-decoration: none;
  color: #f0f0f0; display: flex; flex-direction: column; overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
}
.card:hover { transform: translateY(-8px); box-shadow: 0 10px 20px rgba(0, 123, 255, 0.2); border-color: #007BFF; }
.card-image { width: 100%; height: 200px; object-fit: cover; }
.card-image-placeholder { 
    width: 100%; height: 200px; background-color: #333; display: flex; align-items: center; 
    justify-content: center; font-size: 2rem; font-weight: bold; color: #555;
}
.card-content { padding: 20px; display: flex; flex-direction: column; flex-grow: 1; }
.card h3 { margin-top: 0; font-size: 1.4rem; }
.card p { color: #aaa; flex-grow: 1; margin-bottom: 20px; }
.card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: auto; }
.price { font-size: 1.3rem; font-weight: bold; color: #007BFF; }
.details-link { color: #aaa; font-weight: 500; transition: color 0.3s; }
.card:hover .details-link { color: #fff; }
</style>