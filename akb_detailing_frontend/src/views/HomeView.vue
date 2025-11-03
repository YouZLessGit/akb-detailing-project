<template>
  <div class="home-view">
    <!-- ======================= 1. HERO SECTION ======================= -->
    <section class="hero-section">
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <h1 class="hero-title">Искусство детейлинга для вашего автомобиля</h1>
        <p class="hero-subtitle">Превосходя ожидания. Воплощая совершенство в каждой детали.</p>
        <RouterLink to="/booking" class="cta-button">Записаться онлайн</RouterLink>
      </div>
    </section>

    <!-- ======================= 2. БЛОК ПРЕИМУЩЕСТВ ======================= -->
    <section class="features-section">
      <h2 class="section-title">Почему выбирают AKB Detailing</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">✨</div>
          <h3>Премиум материалы</h3>
          <p>Мы используем только сертифицированную автохимию и оборудование от ведущих мировых брендов.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">👨‍🔧</div>
          <h3>Опытные мастера</h3>
          <p>Наша команда — профессионалы с многолетним опытом, влюбленные в свое дело.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🔍</div>
          <h3>Внимание к деталям</h3>
          <p>Мы гарантируем безупречное качество и проработку каждого сантиметра вашего автомобиля.</p>
        </div>
      </div>
    </section>

    <!-- ======================= 3. ГАЛЕРЕЯ РАБОТ ======================= -->
    <section class="gallery-section">
      <h2 class="section-title">Наши работы</h2>
      <p class="section-subtitle">Лучше слов за нас говорит результат.</p>
      <div class="gallery-grid">
        <!-- Замените # на ссылки на ваши изображения -->
        <img src="https://images.unsplash.com/photo-1616422285623-13ff0162193c?q=80&w=2070" alt="Полировка кузова автомобиля">
        <img src="https://images.unsplash.com/photo-1616422285623-13ff0162193c?q=80&w=2070" alt="Полировка кузова автомобиля">
        <img src="https://images.unsplash.com/photo-1552519507-da3b142c6e3d?q=80&w=2070" alt="Яркий спортивный автомобиль после детейлинга">
        <img src="https://images.unsplash.com/photo-1605559424843-9e4c228bf1c2?q=80&w=1964" alt="Чистый салон автомобиля">
      </div>
    </section>
    
    <!-- ======================= 4. МЕСТОПОЛОЖЕНИЕ ======================= -->
    <section class="location-section">
        <h2 class="section-title">Как нас найти</h2>
        <div class="location-content">
            <div class="location-info">
                <h3>Наш адрес:</h3>
                <p>г. Минск, ул. Примерная, д. 123</p>
                <h3>Время работы:</h3>
                <p>Пн - Сб: 09:00 - 20:00</p>
                <p>Вс: Выходной</p>
                <h3>Телефон:</h3>
                <p>+375 (29) 123-45-67</p>
            </div>
            <div class="map-container">
                <!-- ВАЖНО: Замените этот iframe на код с Яндекс.Карт или Google Maps -->
                <iframe 
                    src="https://yandex.ru/map-widget/v1/?um=constructor%3A9a8d9272b38cb788647069177114b76c8c36ac2897299e525a7401968875326a&amp;source=constructor" 
                    width="100%" 
                    height="400" 
                    frameborder="0">
                </iframe>
            </div>
        </div>
    </section>

    <!-- ======================= 5. ФИНАЛЬНЫЙ ПРИЗЫВ К ДЕЙСТВИЮ ======================= -->
    <section class="final-cta-section">
        <h2>Готовы преобразить ваш автомобиль?</h2>
        <p>Не откладывайте уход за вашей машиной. Запишитесь онлайн за 2 минуты.</p>
        <RouterLink to="/booking" class="cta-button">Записаться онлайн</RouterLink>
    </section>

  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.home-view {
  width: 100%;
}

/* Общие стили для секций */
.section-title {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 20px;
  color: #fff;
}
.section-subtitle {
  text-align: center;
  font-size: 1.1rem;
  color: #aaa;
  margin-top: -15px;
  margin-bottom: 40px;
}

/* 1. Hero Section */
.hero-section {
  position: relative;
  height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #fff;
  background-image: url('https://www.thecarexpert.co.uk/wp-content/uploads/2022/09/33159-RS7Sportbackperformance-1920x960.jpeg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
}
.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
}
.hero-content {
  position: relative;
  z-index: 2;
  max-width: 800px;
  padding: 20px;
}
.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}
.hero-subtitle {
  font-size: 1.4rem;
  color: #ccc;
  margin-bottom: 2.5rem;
}
.cta-button {
  background-color: #007BFF;
  color: #fff;
  padding: 15px 35px;
  border-radius: 5px;
  text-decoration: none;
  font-size: 1.2rem;
  font-weight: bold;
  transition: background-color 0.3s, transform 0.3s;
  display: inline-block;
}
.cta-button:hover {
  background-color: #0056b3;
  transform: scale(1.05);
}

/* 2. Features Section */
.features-section {
  padding: 80px 20px;
  background-color: #1a1a1a;
}
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
}
.feature-card {
  background-color: #242424;
  padding: 30px;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #333;
  transition: transform 0.3s;
}
.feature-card:hover {
  transform: translateY(-10px);
}
.feature-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}
.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 10px;
}
.feature-card p {
  color: #aaa;
}

/* 3. Gallery Section */
.gallery-section {
  padding: 80px 20px;
}
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  max-width: 1200px;
  margin: 0 auto;
}
.gallery-grid img {
  width: 100%;
  height: 350px; /* <-- ЗАДАЕМ ФИКСИРОВАННУЮ ВЫСОТУ ДЛЯ ВСЕХ ИЗОБРАЖЕНИЙ */
  object-fit: cover; /* <-- ГЛАВНОЕ СВОЙСТВО, КОТОРОЕ ПРЕДОТВРАЩАЕТ ИСКАЖЕНИЕ */
  border-radius: 8px;
  transition: transform 0.3s, filter 0.3s;
}
.gallery-grid img:hover {
  transform: scale(1.03);
  filter: brightness(1.1);
}

/* 4. Location Section */
.location-section {
    padding: 80px 20px;
    background-color: #1a1a1a;
}
.location-content {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 40px;
    max-width: 1200px;
    margin: 0 auto;
    align-items: center;
}
.location-info h3 {
    font-size: 1.5rem;
    color: #007BFF;
}
.location-info p {
    font-size: 1.1rem;
    color: #ccc;
    margin-bottom: 1.5rem;
}
.map-container iframe {
    border-radius: 8px;
    border: 1px solid #333;
}

/* 5. Final CTA Section */
.final-cta-section {
    padding: 80px 20px;
    text-align: center;
    background-color: #242424;
}
.final-cta-section h2 {
    font-size: 2.2rem;
}
.final-cta-section p {
    color: #aaa;
    margin-bottom: 30px;
}

/* Адаптивность */
@media (max-width: 768px) {
  .hero-title { font-size: 2.5rem; }
  .hero-subtitle { font-size: 1.1rem; }
  .gallery-grid { grid-template-columns: 1fr; }
  .location-content { grid-template-columns: 1fr; }
}
</style>