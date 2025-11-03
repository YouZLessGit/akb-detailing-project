<template>
  <div class="post-detail-page">
    <div v-if="loading" class="loader">Загрузка...</div>
    
    <div v-if="post">
      <!-- Hero Section (Обложка) -->
      <div 
        class="hero-section" 
        :style="{ backgroundImage: `url(http://localhost:8000${post.main_image_url})` }"
      >
        <div class="hero-content">
          <h1 class="post-title">{{ post.title }}</h1>
          <div class="post-meta">
            <span>Автор: {{ post.author_name }}</span>
            <span>&bull;</span>
            <span>{{ new Date(post.created_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' }) }}</span>
          </div>
        </div>
      </div>

      <!-- Двухколоночный макет -->
      <div class="main-content-grid">
        <!-- Основная колонка со статьей -->
        <main class="post-article-column">
          <div class="post-content-card">
            <div class="post-content" v-html="post.content"></div>
            <RouterLink to="/blog" class="back-link">&larr; Вернуться ко всем статьям</RouterLink>
          </div>
        </main>

        <!-- Боковая колонка (сайдбар) -->
        <aside class="post-sidebar-column">
          <!-- Обертка для "липкого" эффекта -->
          <div class="sticky-sidebar-content">
            <div class="sidebar-widget">
              <h3 class="widget-title">Запишитесь к нам</h3>
              <p>Профессиональный уход для вашего автомобиля. Гарантия качества.</p>
              <RouterLink to="/booking" class="cta-button">Записаться онлайн</RouterLink>
            </div>

            <div class="sidebar-widget">
              <h3 class="widget-title">Читайте также</h3>
              <ul class="recent-posts-list">
                <li v-for="recentPost in recentPosts" :key="recentPost._id">
                  <RouterLink :to="'/blog/' + recentPost.slug" class="recent-post-link">
                    <img :src="'http://localhost:8000' + recentPost.main_image_url" alt="" class="recent-post-image">
                    <span class="recent-post-title">{{ recentPost.title }}</span>
                  </RouterLink>
                </li>
              </ul>
            </div>
          </div>
        </aside>
      </div>
    </div>

    <div v-if="error" class="error-message">
      <h2>Статья не найдена</h2>
      <p>Возможно, она была удалена или вы перешли по неверной ссылке.</p>
      <RouterLink to="/blog" class="back-link">&larr; Вернуться в блог</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, RouterLink } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const post = ref(null);
const recentPosts = ref([]);
const loading = ref(true);
const error = ref(false);

const fetchPostData = async (slug) => {
  loading.value = true;
  post.value = null;
  error.value = false;
  try {
    const [postResponse, recentResponse] = await Promise.all([
      axios.get(`http://localhost:8000/api/public/blog/post/${slug}/`),
      axios.get(`http://localhost:8000/api/public/blog/posts/`)
    ]);
    post.value = postResponse.data;
    recentPosts.value = recentResponse.data
      .filter(p => p.slug !== slug)
      .slice(0, 4);
  } catch (err) {
    console.error("Ошибка при загрузке данных:", err);
    error.value = true;
  } finally {
    loading.value = false;
  }
};

// =========================================================
// === ВОТ ВОССТАНОВЛЕННЫЙ И ИСПРАВЛЕННЫЙ БЛОК КОДА ===
// =========================================================
onMounted(() => {
  fetchPostData(route.params.slug);
});

watch(() => route.params.slug, (newSlug) => {
  if (newSlug && newSlug !== post.value?.slug) {
    fetchPostData(newSlug);
    window.scrollTo(0, 0); // Прокручиваем страницу наверх при смене статьи
  }
});
</script>

<style scoped>
.post-detail-page { background-color: #121212; padding-bottom: 60px; }
.hero-section { position: relative; width: 100%; min-height: 50vh; background-size: cover; background-position: center; display: flex; align-items: center; justify-content: center; padding: 20px; text-align: center; color: #fff; }
.hero-section::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); z-index: 1; }
.hero-content { position: relative; z-index: 2; max-width: 900px; }
.post-title { font-size: 3.5rem; font-weight: 700; line-height: 1.2; text-shadow: 0 2px 10px rgba(0,0,0,0.5); margin: 0 0 15px 0; }
.post-meta { font-size: 1rem; color: rgba(255, 255, 255, 0.8); display: flex; justify-content: center; gap: 15px; }
.main-content-grid { display: grid; grid-template-columns: 1fr 320px; gap: 40px; max-width: 1240px; margin: -80px auto 0 auto; padding: 0 20px; position: relative; z-index: 3; }
.post-article-column { grid-column: 1 / 2; }
.post-sidebar-column { grid-column: 2 / 3; }
.post-content-card { background-color: #1a1a1a; padding: 40px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); }
.post-content { line-height: 1.8; font-size: 1.1rem; color: #e0e0e0; }

.sticky-sidebar-content {
  position: sticky;
  top: 100px; 
}

.sidebar-widget { background-color: #1a1a1a; padding: 25px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); margin-bottom: 30px; }
.widget-title { font-size: 1.3rem; margin: 0 0 15px 0; color: #fff; border-bottom: 1px solid #333; padding-bottom: 10px; }
.sidebar-widget p { color: #aaa; line-height: 1.6; margin-bottom: 20px; }
.cta-button { display: block; background-color: #007BFF; color: #fff; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-size: 1rem; font-weight: 600; text-align: center; transition: background-color 0.3s; }
.cta-button:hover { background-color: #0056b3; }
.recent-posts-list { list-style: none; padding: 0; margin: 0; }
.recent-posts-list li { margin-bottom: 15px; }
.recent-post-link { display: flex; align-items: center; gap: 15px; text-decoration: none; color: #e0e0e0; transition: background-color 0.2s; border-radius: 6px; }
.recent-post-link:hover .recent-post-title { color: #0095ff; }
.recent-post-image { width: 80px; height: 60px; object-fit: cover; border-radius: 6px; flex-shrink: 0; }
.recent-post-title { font-size: 0.95rem; line-height: 1.4; }
.post-content :deep(p) { margin-bottom: 1.5em; }
.post-content :deep(h2) { font-size: 2rem; }
.post-content :deep(h3) { font-size: 1.6rem; }
.back-link { display: block; text-align: center; margin-top: 40px; color: #0095ff; }
.loader, .error-message { text-align: center; padding: 100px 20px; }
@media (max-width: 1024px) {
  .main-content-grid { grid-template-columns: 1fr; }
  .post-sidebar-column { margin-top: 40px; }
  .sticky-sidebar-content { position: static; }
}
@media (max-width: 768px) {
  .post-title { font-size: 2.5rem; }
  .post-content-card { padding: 30px 20px; }
}
</style>