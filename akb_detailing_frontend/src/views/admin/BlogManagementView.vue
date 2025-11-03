<template>
  <div class="blog-management">
    <h1>Управление блогом</h1>
    <button @click="openPostModal()" class="btn-primary">Написать статью</button>

    <table class="table">
      <thead>
        <tr>
          <th>Заголовок</th>
          <th>Автор</th>
          <th>Статус</th>
          <th>Дата создания</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="post in posts" :key="post._id">
          <td>{{ post.title }}</td>
          <td>{{ post.author_name }}</td>
          <td>
            <span :class="['status', post.status]">{{ post.status === 'published' ? 'Опубликовано' : 'Черновик' }}</span>
          </td>
          <td>{{ new Date(post.created_at).toLocaleDateString() }}</td>
          <td>
            <button @click="openPostModal(post)" class="btn-secondary">Редактировать</button>
            <button @click="deletePost(post._id)" class="btn-danger">Удалить</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Модальное окно для создания/редактирования -->
    <div v-if="isModalOpen" class="modal-overlay" @click.self="closePostModal">
      <div class="modal-content">
        <h2>{{ isEditing ? 'Редактировать статью' : 'Новая статья' }}</h2>
        <form @submit.prevent="savePost">
          <div class="form-group">
            <label>Заголовок</label>
            <input type="text" v-model="currentPost.title" required>
          </div>
          <div class="form-group">
            <label>Имя автора</label>
            <input type="text" v-model="currentPost.author_name" required>
          </div>
          <div class="form-group">
            <label>Статус</label>
            <select v-model="currentPost.status">
              <option value="draft">Черновик</option>
              <option value="published">Опубликовано</option>
            </select>
          </div>
          <div class="form-group">
            <label>Теги (через запятую)</label>
            <input type="text" v-model="currentPost.tags">
          </div>
          <div class="form-group">
            <label>Главное изображение</label>
            <input type="file" @change="handleImageUpload" accept="image/*">
            <img v-if="imagePreview" :src="imagePreview" class="image-preview" />
          </div>
          <div class="form-group">
            <label>Содержимое статьи</label>
            <!-- === ИЗМЕНЕНИЕ ЗДЕСЬ === -->
            <Editor
              v-if="isModalOpen"
              api-key="qm2jvf2rtb8o25awdkwtlfoo20vssnypfe4odow2tbl7h64v"
              v-model="currentPost.content"
              :init="tinymceConfig"
            />
          </div>
          <div class="modal-actions">
            <button type="button" @click="closePostModal" class="btn-secondary">Отмена</button>
            <button type="submit" class="btn-primary">Сохранить</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import Editor from '@tinymce/tinymce-vue';

// === ИЗМЕНЕНИЕ ЗДЕСЬ ===
// Добавляем полнофункциональную конфигурацию для редактора
const tinymceConfig = {
  height: 500,
  menubar: true, // Включаем верхнее меню (File, Edit, View, Tools...)
  plugins: [
    'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
    'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
    'insertdatetime', 'media', 'table', 'help', 'wordcount'
  ],
  toolbar: 'undo redo | blocks | ' +
    'bold italic forecolor | alignleft aligncenter ' +
    'alignright alignjustify | bullist numlist outdent indent | ' +
    'removeformat | code | help', // Добавили кнопку 'code' для быстрого доступа
  content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }'
};

const API_BASE_URL = 'http://localhost:8000/api';

const posts = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentPost = ref({});
const newImageFile = ref(null);
const imagePreview = ref('');

// Получение всех статей
const fetchPosts = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/blog/posts/`);
    posts.value = response.data;
  } catch (error) {
    console.error("Ошибка при загрузке статей:", error);
  }
};

onMounted(fetchPosts);

// Открытие модального окна
const openPostModal = (post = null) => {
  if (post) {
    isEditing.value = true;
    currentPost.value = { 
      ...post,
      tags: Array.isArray(post.tags) ? post.tags.join(', ') : ''
    };
    imagePreview.value = post.main_image_url;
  } else {
    isEditing.value = false;
    currentPost.value = {
      title: '',
      author_name: '',
      status: 'draft',
      content: '',
      tags: ''
    };
    imagePreview.value = '';
  }
  newImageFile.value = null;
  isModalOpen.value = true;
};

// Закрытие модального окна
const closePostModal = () => {
  isModalOpen.value = false;
};

// Обработка загрузки изображения
const handleImageUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    newImageFile.value = file;
    imagePreview.value = URL.createObjectURL(file);
  }
};

// Сохранение статьи
const savePost = async () => {
  const formData = new FormData();
  formData.append('title', currentPost.value.title);
  formData.append('content', currentPost.value.content);
  formData.append('status', currentPost.value.status);
  formData.append('author_name', currentPost.value.author_name);
  formData.append('tags', currentPost.value.tags);

  if (newImageFile.value) {
    formData.append('main_image', newImageFile.value);
  }
  
  try {
    if (isEditing.value) {
      await axios.post(`${API_BASE_URL}/blog/posts/update/${currentPost.value._id}/`, formData);
    } else {
      await axios.post(`${API_BASE_URL}/blog/posts/create/`, formData);
    }
    closePostModal();
    fetchPosts(); // Обновить список после сохранения
  } catch (error) {
    console.error("Ошибка при сохранении статьи:", error);
    alert('Произошла ошибка. Проверьте, что все поля заполнены, особенно изображение.');
  }
};

// Удаление статьи
const deletePost = async (postId) => {
  if (confirm("Вы уверены, что хотите удалить эту статью?")) {
    try {
      await axios.delete(`${API_BASE_URL}/blog/posts/delete/${postId}/`);
      fetchPosts(); // Обновить список
    } catch (error) {
      console.error("Ошибка при удалении статьи:", error);
    }
  }
};
</script>

<style scoped>
/* Стили для страницы управления */
.blog-management {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
.btn-primary, .btn-secondary, .btn-danger {
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin-right: 10px;
  font-size: 14px;
}
.btn-primary { background-color: #007bff; color: white; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-danger { background-color: #dc3545; color: white; }
.table { width: 100%; margin-top: 20px; border-collapse: collapse; }
.table th, .table td { border: 1px solid #ddd; padding: 12px; text-align: left; }
.table th { background-color: #f2f2f2; }
.status { padding: 5px 10px; border-radius: 15px; color: white; font-size: 12px; }
.status.published { background-color: #28a745; }
.status.draft { background-color: #ffc107; color: black; }

/* Стили для модального окна */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0, 0, 0, 0.6); display: flex;
  justify-content: center; align-items: center; z-index: 1000;
}
.modal-content {
  background-color: white; padding: 30px; border-radius: 8px;
  width: 90%; max-width: 800px; max-height: 90vh; overflow-y: auto;
}
.form-group { margin-bottom: 20px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
.form-group input, .form-group select {
  width: 100%; padding: 10px; border: 1px solid #ccc;
  border-radius: 4px; box-sizing: border-box;
}
.modal-actions { display: flex; justify-content: flex-end; margin-top: 20px; }
.image-preview { max-width: 200px; margin-top: 10px; border-radius: 5px; }
</style>