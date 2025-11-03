<!-- src/views/PortfolioDetailView.vue -->
<template>
  <div v-if="isLoading" class="loader-container"><div class="loader">Загрузка...</div></div>
  <div v-else-if="error" class="error-container"><div class="error-message">{{ error }}</div></div>
  <div v-else-if="project">

    <div class="project-header" :style="{ backgroundImage: `url(${headerImageUrl})` }">
      <div class="header-content">
        <h1>{{ project.title }}</h1>
        <p class="category">{{ project.category }}</p>
      </div>
    </div>

    <div class="content-grid">
      <!-- Левая колонка с информацией -->
      <div class="project-info">
        <div class="details-card">
          <h3>Детали проекта</h3>
          <ul>
            <li><strong>Услуга:</strong><span>{{ project.category }}</span></li>
            <li><strong>Автомобиль:</strong><span>{{ project.title }}</span></li>
            <li><strong>Дата выполнения:</strong><span>{{ formattedDate }}</span></li>
          </ul>
        </div>
        <div class="project-description prose-content" v-html="project.description"></div>
      </div>

      <!-- Правая колонка с галереей и CTA -->
      <div class="project-gallery">
        <h3>Результаты работы</h3>
        <ImageSlider :images="project.gallery_images.map(url => `http://localhost:8000${url}`)" />
        
        <div class="cta-block">
          <h2>Хотите такой же результат?</h2>
          <p>Мы готовы преобразить и ваш автомобиль.</p>
          <!-- 
            ---
            ИЗМЕНЕНИЕ: Ссылка теперь ведет на /booking
            ---
          -->
          <RouterLink to="/booking" class="cta-button">
            Записаться на услугу
          </RouterLink>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import ImageSlider from '@/components/ImageSlider.vue';

const route = useRoute();
const project = ref(null);
const isLoading = ref(true);
const error = ref(null);

const headerImageUrl = computed(() => project.value?.main_image_url ? `http://localhost:8000${project.value.main_image_url}` : '');

const formattedDate = computed(() => {
  if (!project.value?.date_completed) return 'Дата не указана';
  return new Date(project.value.date_completed).toLocaleDateString('ru-RU', {
    year: 'numeric', month: 'long', day: 'numeric'
  });
});

onMounted(async () => {
  const slug = route.params.slug;
  try {
    const response = await axios.get(`http://localhost:8000/api/public/portfolio/${slug}/`);
    project.value = response.data;
  } catch (err) {
    error.value = "Не удалось загрузить проект.";
  } finally {
    isLoading.value = false;
  }
});
</script>

<style scoped>
.project-header{background-size:cover;background-position:center;min-height:50vh;padding:120px 20px;position:relative;display:flex;align-items:center;justify-content:center;text-align:center;border-bottom:1px solid #333}.project-header::before{content:'';position:absolute;top:0;left:0;right:0;bottom:0;background-color:rgba(0,0,0,.6);z-index:1}.header-content{position:relative;z-index:2;max-width:900px;margin:0 auto;color:#fff}h1{font-size:3.5rem;margin:0;text-shadow:2px 2px 8px rgba(0,0,0,.7)}.category{font-size:1.2rem;color:#007bff;font-weight:700;margin-top:10px;text-transform:uppercase;background-color:rgba(0,0,0,.5);padding:5px 15px;border-radius:5px;display:inline-block}.content-grid{display:grid;grid-template-columns:1fr 1.5fr;gap:50px;max-width:1300px;margin:60px auto;padding:0 20px}.details-card{background-color:#1c1c1c;border:1px solid #333;padding:2rem;border-radius:12px;margin-bottom:2.5rem}.details-card h3{margin-top:0;margin-bottom:1.5rem;font-size:1.5rem;color:#e5e5e5;padding-bottom:.75rem;border-bottom:2px solid #007bff}.details-card ul{list-style:none;padding:0;margin:0}.details-card li{display:flex;justify-content:space-between;margin-bottom:1rem;font-size:1rem;color:#ccc}.details-card li:last-child{margin-bottom:0}.details-card li strong{color:#a0a0a0;margin-right:1rem}.details-card li span{text-align:right}.project-gallery h3{font-size:1.8rem;color:#e5e5e5;margin-top:0;margin-bottom:1.5rem}.project-gallery{position:sticky;top:40px;align-self:start}
.cta-block {
  background-color: #1c1c1c;
  border: 1px solid #333;
  color: #fff;
  padding: 2rem;
  border-radius: 12px;
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.cta-block h2 { font-size: 1.5rem; margin: 0 0 0.5rem 0; }
.cta-block p { color: #a0a0a0; margin: 0 0 1.5rem 0; font-size: 0.9rem; max-width: 90%; }
.cta-button{display:inline-block;background-color:#007bff;color:#fff;padding:12px 25px;border-radius:30px;text-decoration:none;font-weight:700;font-size:1rem;transition:all .3s ease;width:100%}.cta-button:hover{background-color:#0056b3;transform:translateY(-2px)}

@media (max-width: 992px){.content-grid{grid-template-columns:1fr;gap:0}.project-gallery{position:static;margin-top:40px}.project-gallery h3{text-align:center}}
.project-description{color:#ccc;line-height:1.8;font-size:1.1rem}
.prose-content :deep(h2),.prose-content :deep(h3){font-size:2.2rem;color:#e5e5e5;margin-top:3rem;margin-bottom:1.5rem;padding-bottom:.75rem;border-bottom:3px solid #007bff}
.prose-content :deep(p) { margin-bottom: 1.5rem; color: #bbb; }
.prose-content :deep(strong) { color: #e5e5e5; }
.prose-content :deep(ul) { list-style-type: none; padding-left: 1.5rem; margin-bottom: 1.5rem; }
.prose-content :deep(ul li) { position: relative; margin-bottom: .8rem; }
.prose-content :deep(ul li::before) { content: "•"; position: absolute; left: -1.5rem; color: #007BFF; font-size: 1.5em; line-height: 1; }
.prose-content :deep(ol) { list-style: none; counter-reset: list-counter; padding-left: 2rem; margin-bottom: 1.5rem; }
.prose-content :deep(ol li) { position: relative; counter-increment: list-counter; margin-bottom: 1rem; }
.prose-content :deep(ol li::before) { content: counter(list-counter) "."; position: absolute; left: -2.5rem; color: #007BFF; font-weight: bold; font-size: 1.1rem; }
.prose-content :deep(a) { color: #0099ff; text-decoration: none; }
.prose-content :deep(a:hover) { text-decoration: underline; }
.prose-content :deep(iframe) { display: block; width: 100%; max-width: 100%; aspect-ratio: 16 / 9; height: auto; border: none; border-radius: 12px; margin: 2rem 0; }
</style>