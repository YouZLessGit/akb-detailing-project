<!-- src/views/AboutView.vue -->
<template>
  <div v-if="isLoading" class="loader">Загрузка...</div>
  <div v-else-if="error" class="error-message">{{ error }}</div>
  
  <div v-else class="about-page">
    <!-- 1. Эффектная шапка (Hero) - статичная, так как она задает общий тон страницы -->
    <section class="hero-section">
      <div class="hero-content">
        <h1>Наша философия. Ваше преимущество.</h1>
        <p class="hero-subtitle">Мы верим, что детейлинг — это не просто услуга, а искусство сохранения и преумножения красоты автомобиля.</p>
      </div>
    </section>

    <!-- 2. Блок основателя (данные из админки) -->
    <section class="page-section founder-section">
      <div class="section-content founder-grid">
        <div class="founder-photo">
          <img :src="founderPhotoUrl" :alt="content.founder_name || 'Основатель студии'">
        </div>
        <div class="founder-text">
          <h2>Слово основателя</h2>
          <p class="quote">"{{ content.founder_quote }}"</p>
          <div class="founder-signature">
            — {{ content.founder_name }}
          </div>
        </div>
      </div>
    </section>

    <!-- 3. Блок ценностей (данные из админки) -->
    <section class="page-section values-section">
      <div class="section-content">
        <h2 class="section-title">Три кита нашего мастерства</h2>
        <div class="values-grid">
          <div v-for="(value, index) in content.values" :key="index" class="value-card">
            <div class="value-icon">{{ value.icon || '✨' }}</div>
            <h3>{{ value.title }}</h3>
            <p>{{ value.text }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 4. Блок студии (данные из админки) -->
    <section class="page-section studio-section">
      <div class="section-content">
        <h2 class="section-title">Пространство, где рождается совершенство</h2>
        <p class="section-subtitle">Наша студия — это чистое, светлое и технологичное пространство, созданное для достижения безупречных результатов.</p>
        <img :src="studioPhotoUrl" alt="Интерьер детейлинг студии AKB Detailing" class="studio-image">
      </div>
    </section>

     <!-- 5. Призыв к действию (статичный) -->
    <section class="page-section cta-section">
       <div class="cta-block">
          <h2>Готовы доверить нам свой автомобиль?</h2>
          <p>Свяжитесь с нами для бесплатной консультации или сразу запишитесь на услугу.</p>
          <RouterLink to="/booking" class="cta-button">
            Записаться онлайн
          </RouterLink>
        </div>
    </section>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { RouterLink } from 'vue-router';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';
const SERVER_URL = 'http://localhost:8000';

const isLoading = ref(true);
const error = ref(null);

const content = ref({
  founder_photo_url: "",
  founder_quote: "",
  founder_name: "",
  values: [ 
    { icon: "🔬", title: "", text: "" },
    { icon: "🏆", title: "", text: "" },
    { icon: "🤝", title: "", text: "" }
  ],
  studio_photo_url: ""
});

const founderPhotoUrl = computed(() => {
  return content.value.founder_photo_url ? `${SERVER_URL}${content.value.founder_photo_url}` : 'https://images.unsplash.com/photo-1568602471122-7832951cc4c5?q=80&w=2070';
});

const studioPhotoUrl = computed(() => {
  return content.value.studio_photo_url ? `${SERVER_URL}${content.value.studio_photo_url}` : 'https://images.unsplash.com/photo-1616422285623-13ff0162193c?q=80&w=2070';
});

onMounted(async () => {
  isLoading.value = true;
  try {
    const response = await axios.get(`${API_URL}/public/page/about-us/`);
    content.value = response.data;
  } catch (err) {
    error.value = "Не удалось загрузить данные страницы.";
    console.error(err);
  } finally {
    isLoading.value = false;
  }
});
</script>

<style scoped>
.about-page { color: #f0f0f0; }
.page-section { padding: 80px 20px; }
.section-content { max-width: 1200px; margin: 0 auto; }
.section-title { text-align: center; font-size: 2.5rem; margin-top: 0; margin-bottom: 1rem; }
.section-subtitle { text-align: center; font-size: 1.2rem; color: #aaa; max-width: 700px; margin: 0 auto 50px auto; }

.hero-section { background: linear-gradient(rgba(18, 18, 18, 0.7), rgba(18, 18, 18, 0.7)), url(https://www.zastavki.com/pictures/originals/2020Auto___Audi_Audi_RS_5_Coupe_car_rear_view_144313_.jpg) center center/cover; min-height: 50vh; display: flex; align-items: center; justify-content: center; text-align: center; padding: 4rem 2rem; }
.hero-content h1 { font-size: 3.5rem; margin: 0; }
.hero-subtitle { font-size: 1.3rem; color: #ddd; margin-top: 1rem; max-width: 600px; }

.founder-section { background-color: #1a1a1a; }
.founder-grid { display: grid; grid-template-columns: 1fr 2fr; gap: 50px; align-items: center; }
.founder-photo img { width: 100%; border-radius: 12px; aspect-ratio: 1 / 1; object-fit: cover; }
.founder-text h2 { font-size: 2.5rem; margin-top: 0; }
.founder-text p.quote { font-size: 1.2rem; color: #bbb; line-height: 1.8; font-style: italic; border-left: 3px solid #007BFF; padding-left: 1.5rem; }
.founder-signature { margin-top: 2rem; color: #007BFF; font-weight: bold; }

.values-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; margin-top: 50px; }
.value-card { background-color: #1e1e1e; border: 1px solid #333; padding: 2rem; border-radius: 12px; text-align: center; transition: transform 0.3s, box-shadow 0.3s; }
.value-card:hover { transform: translateY(-10px); box-shadow: 0 10px 20px rgba(0, 123, 255, 0.1); }
.value-icon { font-size: 3rem; margin-bottom: 1rem; }
.value-card h3 { font-size: 1.5rem; margin: 0 0 1rem 0; color: #fff; }
.value-card p { color: #aaa; font-size: 1rem; line-height: 1.6; margin: 0; }

.studio-section { background-color: #1a1a1a; }
.studio-image { width: 100%; border-radius: 12px; margin-top: 2rem; }

.cta-section { padding-bottom: 100px; }
.cta-block { max-width: 700px; margin: 0 auto; background: linear-gradient(45deg, #007bff, #0056b3); color: #fff; padding: 3rem; border-radius: 12px; text-align: center; }
.cta-block h2 { font-size: 2rem; margin: 0 0 1rem 0; }
.cta-block p { color: #e0e0e0; margin: 0 0 2rem 0; }
.cta-button { display: inline-block; background-color: #fff; color: #007BFF; padding: 14px 30px; border-radius: 30px; text-decoration: none; font-weight: 700; transition: all 0.3s ease; }
.cta-button:hover { background-color: #f0f0f0; transform: translateY(-3px); }

@media (max-width: 992px) {
  .founder-grid { grid-template-columns: 1fr; }
  .values-grid { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .hero-content h1 { font-size: 2.5rem; }
  .section-title, .founder-text h2 { font-size: 2rem; }
}
.loader, .error-message { text-align: center; padding: 50px 20px; font-size: 1.2rem; }
</style>