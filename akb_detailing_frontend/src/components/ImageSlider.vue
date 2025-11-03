<!-- src/components/ImageSlider.vue -->
<template>
  <div class="slider-container" v-if="images && images.length">
    <div class="main-image">
      <img :src="activeImage" :key="activeImage" alt="Основное изображение" class="fade-in">
    </div>
    <div class="thumbnails" v-if="images.length > 1">
      <div
        v-for="(image, index) in images"
        :key="index"
        class="thumbnail"
        :class="{ 'active': image === activeImage }"
        @click="setActiveImage(image)"
      >
        <img :src="image" alt="Миниатюра">
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  images: {
    type: Array,
    required: true,
    default: () => []
  }
});

const activeImage = ref('');

watch(() => props.images, (newImages) => {
  if (newImages && newImages.length > 0) {
    activeImage.value = newImages[0];
  }
}, { immediate: true });

const setActiveImage = (image) => {
  activeImage.value = image;
};
</script>

<style scoped>
.slider-container {
  width: 100%;
  margin-bottom: 40px;
}

.main-image {
  width: 100%;
  padding-top: 60%; /* Соотношение сторон 10:6 */
  position: relative;
  background-color: #222;
  border-radius: 12px;
  overflow: hidden;
}

.main-image img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover; 
}

.fade-in {
  animation: fadeIn 0.4s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0.5; }
  to { opacity: 1; }
}

.thumbnails {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  overflow-x: auto;
  padding: 0.5rem 0;
}

.thumbnail {
  flex-shrink: 0;
  width: 120px;
  height: 75px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 3px solid transparent;
  transition: border-color 0.3s, transform 0.3s;
}

.thumbnail:hover {
  transform: scale(1.05);
}

.thumbnail.active {
  border-color: #007BFF;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>