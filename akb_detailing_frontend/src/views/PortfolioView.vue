<!-- src/views/PortfolioView.vue -->
<template>
  <div class="page-container">
    <div class="header-section">
      <h1>Наше портфолио</h1>
      <p>Примеры работ, которыми мы гордимся</p>
    </div>

    <!-- НОВЫЙ БЛОК: Фильтры по категориям -->
    <div v-if="projects.length > 0" class="filter-bar">
      <button 
        @click="selectedCategory = 'Все'" 
        :class="{ active: selectedCategory === 'Все' }">
        Все
      </button>
      <button 
        v-for="category in uniqueCategories" 
        :key="category" 
        @click="selectedCategory = category"
        :class="{ active: selectedCategory === category }">
        {{ category }}
      </button>
    </div>

    <div v-if="isLoading" class="loader">Загрузка...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <!-- ИЗМЕНЕНИЕ: v-for теперь работает с отфильтрованными проектами -->
    <div v-else-if="filteredProjects.length > 0" class="portfolio-grid">
      <RouterLink v-for="project in filteredProjects" :key="project._id" :to="`/portfolio/${project.slug}`" class="card">
        
        <!-- Вся магия теперь внутри этой обертки -->
        <div class="card-image-wrapper">
          <img :src="`http://localhost:8000${project.main_image_url}`" class="card-image" alt="Обложка проекта">
          
          <!-- Оверлей, который появляется при наведении -->
          <div class="card-overlay">
            <div class="overlay-content">
              <span class="card-category">{{ project.category }}</span>
              <h3>{{ project.title }}</h3>
            </div>
          </div>
        </div>

      </RouterLink>
    </div>
    
    <div v-else class="empty-state">
      <p>Нет работ в выбранной категории.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

const projects = ref([]);
const isLoading = ref(true);
const error = ref(null);

const selectedCategory = ref('Все');

const uniqueCategories = computed(() => {
  if (!projects.value) return [];
  return [...new Set(projects.value.map(p => p.category))];
});

const filteredProjects = computed(() => {
  if (selectedCategory.value === 'Все') {
    return projects.value;
  }
  return projects.value.filter(p => p.category === selectedCategory.value);
});


onMounted(async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/public/portfolio/');
    projects.value = response.data;
  } catch(err) {
    error.value = "Не удалось загрузить портфолио.";
    console.error(err);
  } finally {
    isLoading.value = false;
  }
});
</script>

<style scoped>
.page-container {
  max-width: 1400px;
  margin: 40px auto;
  padding: 0 20px;
  color: #f0f0f0;
}
.header-section {
  text-align: center;
  margin-bottom: 40px;
}
.header-section h1 {
  font-size: 3rem;
}
.header-section p {
  font-size: 1.2rem;
  color: #aaa;
}

.filter-bar {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 60px;
}
.filter-bar button {
  background-color: transparent;
  border: 1px solid #444;
  color: #ccc;
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
}
.filter-bar button:hover {
  background-color: #007BFF;
  border-color: #007BFF;
  color: #fff;
}
.filter-bar button.active {
  background-color: #007BFF;
  border-color: #007BFF;
  color: #fff;
  font-weight: 700;
}

.portfolio-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
}
.card {
  display: block;
  overflow: hidden;
  border-radius: 8px;
  position: relative;
  aspect-ratio: 4 / 3;
  background-color: #2a2a2a;
}
.card-image-wrapper {
  width: 100%;
  height: 100%;
}
.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease-out;
}
.card:hover .card-image {
  transform: scale(1.05);
}

.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.1) 100%);
  display: flex;
  align-items: flex-end;
  padding: 1.5rem;
  box-sizing: border-box;
  opacity: 0;
  transition: opacity 0.4s ease-out;
}
.card:hover .card-overlay {
  opacity: 1;
}
.overlay-content {
  transform: translateY(15px);
  transition: transform 0.4s ease-out;
  color: #fff;
}
.card:hover .overlay-content {
  transform: translateY(0);
}
.card-category {
  font-size: 0.8rem;
  font-weight: bold;
  color: #00AFFF;
  text-transform: uppercase;
}
.card h3 {
  margin: 0.25rem 0 0 0;
  font-size: 1.4rem;
  line-height: 1.2;
}
.loader, .error-message, .empty-state {
  text-align: center;
  padding: 50px 20px;
  font-size: 1.2rem;
}
</style>