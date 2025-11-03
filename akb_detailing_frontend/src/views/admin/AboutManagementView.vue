<!-- src/views/admin/AboutManagementView.vue -->
<template>
  <div class="about-management">
    <div class="header">
      <h1>Управление страницей "О нас"</h1>
      <button @click="saveContent" class="save-btn" :disabled="isSaving">
        {{ isSaving ? 'Сохранение...' : 'Сохранить изменения' }}
      </button>
    </div>

    <div v-if="isLoading" class="loader">Загрузка данных...</div>

    <form v-else class="form-layout" @submit.prevent="saveContent">
      <!-- Блок 1: Основатель -->
      <div class="form-section">
        <h2>Блок "Основатель"</h2>
        <div class="form-group">
          <label>Фотография основателя</label>
          <input type="file" @change="handleFileChange($event, 'founder_photo')" accept="image/*">
          <div v-if="previews.founder_photo_url" class="image-preview">
            <img :src="previews.founder_photo_url" alt="Предпросмотр фото основателя">
          </div>
        </div>
        <div class="form-group">
          <label>Цитата</label>
          <textarea v-model="content.founder_quote" rows="4" placeholder="Введите цитату..."></textarea>
        </div>
        <div class="form-group">
          <label>Имя основателя</label>
          <input type="text" v-model="content.founder_name" placeholder="Имя Фамилия, должность...">
        </div>
      </div>

      <!-- Блок 2: Ценности -->
      <div class="form-section">
        <h2>Блок "Наши ценности"</h2>
        <div class="values-grid">
          <div v-for="(value, index) in content.values" :key="index" class="value-card-editor">
            <h4>Карточка #{{ index + 1 }}</h4>
            <div class="form-group">
              <label>Иконка (Emoji)</label>
              <input type="text" v-model="value.icon" placeholder="Например: 🏆">
            </div>
            <div class="form-group">
              <label>Заголовок</label>
              <input type="text" v-model="value.title" :placeholder="`Заголовок ${index + 1}`">
            </div>
            <div class="form-group">
              <label>Текст</label>
              <textarea v-model="value.text" rows="3" :placeholder="`Описание ${index + 1}`"></textarea>
            </div>
          </div>
        </div>
      </div>

      <!-- Блок 3: Студия -->
      <div class="form-section">
        <h2>Блок "Студия"</h2>
        <div class="form-group">
          <label>Фотография студии</label>
          <input type="file" @change="handleFileChange($event, 'studio_photo')" accept="image/*">
          <div v-if="previews.studio_photo_url" class="image-preview">
            <img :src="previews.studio_photo_url" alt="Предпросмотр фото студии">
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

const content = ref({
  founder_photo_url: "",
  founder_quote: "",
  founder_name: "",
  values: [
    { icon: "", title: "", text: "" },
    { icon: "", title: "", text: "" },
    { icon: "", title: "", text: "" }
  ],
  studio_photo_url: ""
});

const newFiles = reactive({
  founder_photo: null,
  studio_photo: null
});

const previews = reactive({
  founder_photo_url: "",
  studio_photo_url: ""
});

const isLoading = ref(true);
const isSaving = ref(false);

const fetchContent = async () => {
  isLoading.value = true;
  try {
    const response = await axios.get(`${API_URL}/public/page/about-us/`);
    // Убедимся, что структура данных всегда полная
    const data = response.data;
    if (!data.values || data.values.length < 3) {
      data.values = [
        { icon: "🔬", title: "", text: "" },
        { icon: "🏆", title: "", text: "" },
        { icon: "🤝", title: "", text: "" },
      ];
    }
    content.value = data;
    
    previews.founder_photo_url = data.founder_photo_url ? `http://localhost:8000${data.founder_photo_url}` : '';
    previews.studio_photo_url = data.studio_photo_url ? `http://localhost:8000${data.studio_photo_url}` : '';
  } catch (error) {
    alert('Не удалось загрузить данные страницы.');
  } finally {
    isLoading.value = false;
  }
};

const handleFileChange = (event, key) => {
  const file = event.target.files[0];
  if (!file) return;
  newFiles[key] = file;
  previews[`${key}_url`] = URL.createObjectURL(file);
};

const saveContent = async () => {
  isSaving.value = true;
  const formData = new FormData();
  
  formData.append('founder_quote', content.value.founder_quote);
  formData.append('founder_name', content.value.founder_name);
  
  content.value.values.forEach((value, index) => {
    formData.append(`values[${index}][icon]`, value.icon);
    formData.append(`values[${index}][title]`, value.title);
    formData.append(`values[${index}][text]`, value.text);
  });

  if (newFiles.founder_photo) {
    formData.append('founder_photo', newFiles.founder_photo);
  }
  if (newFiles.studio_photo) {
    formData.append('studio_photo', newFiles.studio_photo);
  }

  try {
    await axios.post(`${API_URL}/page/about-us/update/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    alert('Страница успешно сохранена!');
    await fetchContent(); 
  } catch (error) {
    alert('Ошибка при сохранении страницы.');
    console.error(error);
  } finally {
    isSaving.value = false;
  }
};

onMounted(fetchContent);
</script>

<style scoped>
.about-management { padding: 2rem; background-color: #f4f7fa; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.header h1 { font-size: 2rem; color: #333; }
.save-btn { padding: .8rem 1.5rem; border: none; border-radius: 6px; font-weight: 700; cursor: pointer; transition: background-color .2s; background-color: #28a745; color: #fff; }
.save-btn:hover { background-color: #218838; }
.save-btn:disabled { background-color: #6c757d; cursor: not-allowed; }
.loader { text-align: center; font-size: 1.2rem; padding: 2rem; }

.form-layout { display: flex; flex-direction: column; gap: 2rem; }
.form-section { background-color: #fff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 1.5rem; }
.form-section h2 { margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 0.5rem; margin-bottom: 1.5rem; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
.form-group input[type="text"], .form-group textarea { width: 100%; padding: 0.7rem; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
.form-group input[type="file"] { border: 1px solid #ccc; padding: 0.5rem; border-radius: 4px; }

.image-preview { margin-top: 1rem; }
.image-preview img { max-width: 200px; max-height: 200px; border-radius: 6px; border: 1px solid #ddd; }

.values-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
.value-card-editor { background-color: #f9f9f9; padding: 1rem; border-radius: 6px; border: 1px solid #e0e0e0; }
.value-card-editor h4 { margin: 0 0 1rem 0; }

@media (max-width: 992px) {
  .values-grid { grid-template-columns: 1fr; }
}
</style>