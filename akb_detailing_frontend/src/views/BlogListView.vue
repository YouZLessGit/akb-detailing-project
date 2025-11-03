<template>
  <div class="blog-list-page">
    <div class="container">
      <h1>Наш Блог</h1>
      <p class="subtitle">Советы, кейсы и новости из мира детейлинга</p>
      
      <div v-if="loading" class="loader">Загрузка...</div>
      
      <div v-if="!loading && posts.length" class="posts-grid">
        <RouterLink v-for="post in posts" :key="post._id" :to="'/blog/' + post.slug" class="post-card">
          <img :src="'http://localhost:8000' + post.main_image_url" :alt="post.title" class="post-image">
          <div class="post-content">
            <span class="post-date">{{ new Date(post.created_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' }) }}</span>
            <h3 class="post-title">{{ post.title }}</h3>
            <p class="post-author">Автор: {{ post.author_name }}</p>
          </div>
        </RouterLink>
      </div>
      
      <div v-if="!loading && !posts.length" class="no-posts">
        <p>Пока здесь нет ни одной статьи, но скоро мы это исправим!</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { RouterLink } from 'vue-router';

const posts = ref([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/public/blog/posts/');
    posts.value = response.data;
  } catch (error) {
    console.error("Ошибка при загрузке статей:", error);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.blog-list-page {
  padding: 60px 0;
  background-color: #1a1a1a;
  color: #f0f0f0;
}
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}
h1 {
  text-align: center;
  font-size: 3rem;
  margin-bottom: 10px;
}
.subtitle {
  text-align: center;
  font-size: 1.2rem;
  color: #aaa;
  margin-bottom: 50px;
}
.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 30px;
}
.post-card {
  background-color: #252525;
  border-radius: 8px;
  overflow: hidden;
  text-decoration: none;
  color: #f0f0f0;
  transition: transform 0.3s, box-shadow 0.3s;
}
.post-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.4);
}
.post-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}
.post-content {
  padding: 20px;
}
.post-date {
  font-size: 0.8rem;
  color: #888;
  margin-bottom: 10px;
  display: block;
}
.post-title {
  font-size: 1.4rem;
  margin: 0;
}
.post-author {
  font-size: 0.9rem;
  color: #aaa;
  margin-top: 15px;
}
.loader, .no-posts {
  text-align: center;
  font-size: 1.5rem;
  padding: 50px;
}
</style>