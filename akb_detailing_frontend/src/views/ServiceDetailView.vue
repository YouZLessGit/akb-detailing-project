<!-- src/views/ServiceDetailView.vue -->
<template>
  <div v-if="isLoading" class="loader-container"><div class="loader">Загрузка...</div></div>
  <div v-else-if="error" class="error-container"><div class="error-message">{{ error }}</div></div>
  <div v-else-if="service" class="service-page">
    
    <!-- Секция с главным изображением и заголовком -->
    <section class="hero-section" :style="{ backgroundImage: `url(${service.main_image_url || defaultImageUrl})` }">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <h1 class="hero-title">{{ service.name }}</h1>
            <p class="hero-subtitle">{{ service.short_description }}</p>
        </div>
    </section>

    <!-- Основной контент страницы -->
    <main class="main-content">
      <div class="content-wrapper">
        <!-- Левая колонка с подробным описанием -->
        <article class="service-article">
          <div class="prose-content" v-html="renderedContent"></div>
        </article>
        
        <!-- Правый "липкий" сайдбар с ценой и кнопкой -->
        <aside class="sidebar">
            <div class="price-box">
                <div class="price-label">Стоимость услуги</div>
                <div class="price-value">от {{ service.price_from }} BYN</div>
                <div class="price-note">Точная цена зависит от класса и состояния автомобиля</div>
                <RouterLink to="/booking" class="cta-button">Записаться на услугу</RouterLink>
            </div>
        </aside>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import axios from 'axios'
import MarkdownIt from 'markdown-it'

const route = useRoute()
const service = ref(null)
const isLoading = ref(true)
const error = ref(null)

const defaultImageUrl = 'https://images.unsplash.com/photo-1605559424843-9e4c228bf1c2?q=80&w=1964'
const md = new MarkdownIt({ html: true, linkify: true, typographer: true });

const renderedContent = computed(() => {
  if (service.value && typeof service.value.rich_content === 'string') {
    return md.render(service.value.rich_content);
  }
  return '<p>Подробное описание для этой услуги еще не добавлено.</p>'
})

const fetchServiceDetails = async () => {
  const slug = route.params.slug
  isLoading.value = true
  error.value = null
  try {
    // Этот эндпоинт должен быть правильным согласно вашей структуре роутера
    const response = await axios.get(`http://localhost:8000/api/public/service-detail/${slug}/`)
    service.value = response.data
  } catch (err) {
    error.value = "Не удалось найти запрашиваемую услугу."
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchServiceDetails)
</script>

<style scoped>
/* Стили шапки и основной структуры без изменений */
.hero-section{position:relative;display:flex;align-items:center;justify-content:center;min-height:45vh;padding:4rem 2rem;background-size:cover;background-position:center;color:#fff;text-align:center}.hero-overlay{position:absolute;top:0;left:0;right:0;bottom:0;background-color:rgba(0,0,0,.6);z-index:1}.hero-content{position:relative;z-index:2;max-width:800px}.hero-title{font-size:3.5rem;margin:0;text-shadow:2px 2px 8px rgba(0,0,0,.7)}.hero-subtitle{font-size:1.3rem;color:#ddd;margin-top:1rem;line-height:1.6}.main-content{max-width:1200px;margin:60px auto;padding:0 20px}.content-wrapper{display:grid;grid-template-columns:2fr 1fr;gap:50px;align-items:flex-start}.sidebar{position:sticky;top:100px}

/* ---
   ИСПРАВЛЕНИЕ ЗДЕСЬ
   --- */
.price-box {
  background-color: #1e1e1e;
  border: 1px solid #333;
  border-radius: 12px;
  padding: 2rem;
  
  /* Используем Flexbox для идеального центрирования */
  display: flex;
  flex-direction: column; /* Элементы друг под другом */
  align-items: center;   /* Центрирование по горизонтали */
}
/* --- КОНЕЦ ИСПРАВЛЕНИЯ --- */

.price-label { color: #aaa; font-size: 1rem; margin-bottom: 0.5rem; }
.price-value { color: #fff; font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; }
.price-note { color: #888; font-size: 0.9rem; margin-bottom: 2rem; text-align: center; /* Добавим на всякий случай */}
.cta-button {
  display: block;
  width: 100%;
  padding: 14px;
  background-color: #007BFF;
  color: white;
  border: none;
  border-radius: 8px;
  text-decoration: none;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  text-align: center; /* И центрируем текст внутри кнопки */
  transition: background-color 0.3s, transform 0.2s;
}
.cta-button:hover { background-color: #0056b3; transform: translateY(-2px); }

@media (max-width: 992px) {
  .content-wrapper { grid-template-columns: 1fr; }
  .sidebar { position: static; margin-top: 40px; }
}

/* Стили для контента из Markdown (prose) без изменений */
.prose-content{color:#ccc;line-height:1.8;font-size:1.1rem}.prose-content :deep(h2),.prose-content :deep(h3){font-size:2rem;color:#e5e5e5;margin-top:2.5rem;margin-bottom:1.5rem;padding-bottom:.75rem;border-bottom:2px solid #007bff}.prose-content :deep(p){margin-bottom:1.5rem;color:#bbb}.prose-content :deep(strong){color:#e5e5e5}.prose-content :deep(ul){list-style-type:none;padding-left:1.5rem;margin-bottom:1.5rem}.prose-content :deep(ul li){position:relative;margin-bottom:.8rem;padding-left:1rem}.prose-content :deep(ul li::before){content:"✓";position:absolute;left:-.5rem;top:2px;color:#007bff;font-size:1.2em;font-weight:700}.prose-content :deep(a){color:#0099ff;text-decoration:none}.prose-content :deep(a:hover){text-decoration:underline}.prose-content :deep(iframe){display:block;width:100%;max-width:100%;aspect-ratio:16 / 9;height:auto;border:none;border-radius:12px;margin:2rem 0}
</style>