<!-- src/views/admin/PortfolioManagementView.vue -->
<template>
  <div class="portfolio-management">
    <div class="header">
      <h1>Управление Портфолио</h1>
      <button @click="openModal()" class="add-btn">Добавить работу</button>
    </div>
    <div v-if="isLoading">Загрузка проектов...</div>
    <div v-else class="projects-grid">
       <div v-for="project in projects" :key="project._id" class="project-card">
        <img :src="`http://localhost:8000${project.main_image_url}`" alt="Обложка проекта">
        <div class="card-content">
          <h3>{{ project.title }}</h3>
          <p>{{ project.category }}</p>
          <div class="card-actions">
            <button @click="openModal(project)" class="edit-btn">Редактировать</button>
            <button @click="deleteProject(project._id)" class="delete-btn">Удалить</button>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="isModalVisible" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h2>{{ editingProject._id ? 'Редактировать работу' : 'Новая работа' }}</h2>
        <form @submit.prevent="saveProject">
          <div class="form-row">
            <div class="form-group">
              <label>Название автомобиля</label>
              <!-- 
                ---
                ИЗМЕНЕНИЕ: Убран placeholder
                ---
              -->
              <input type="text" v-model="editingProject.title" required>
            </div>
            <div class="form-group">
              <label>Название услуги</label>
              <!-- 
                ---
                ИЗМЕНЕНИЕ: Убран placeholder
                ---
              -->
              <input type="text" v-model="editingProject.category" required>
            </div>
          </div>

          <div class="form-group">
            <label>Дата выполнения</label>
            <input type="date" v-model="editingProject.date_completed" required>
          </div>

          <div class="form-group">
            <label>Изображения</label>
            <input type="file" @change="handleFileChange" multiple accept="image/*" class="file-input">
          </div>
          <div class="previews-container">
            <div v-if="editingProject.existing_images && editingProject.existing_images.length > 0">
              <h4>Текущие изображения</h4>
              <div class="image-grid">
                <div v-for="(img, index) in editingProject.existing_images" :key="index" class="img-preview">
                  <img :src="`http://localhost:8000${img}`">
                  <button type="button" @click="removeExistingImage(index)" class="remove-img-btn">&times;</button>
                </div>
              </div>
            </div>
            <div v-if="newImagePreviews.length > 0">
              <h4>Новые изображения</h4>
              <div class="image-grid">
                <div v-for="(img, index) in newImagePreviews" :key="index" class="img-preview">
                  <img :src="img">
                  <button type="button" @click="removeNewImage(index)" class="remove-img-btn">&times;</button>
                </div>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>Описание</label>
            <Editor :api-key="TINYMCE_API_KEY" v-model="editingProject.description" :init="tinymceConfig" />
          </div>

          <div class="modal-actions">
            <button type="submit" class="save-btn">Сохранить</button>
            <button type="button" class="cancel-btn" @click="closeModal">Отмена</button>
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

const API_URL = 'http://localhost:8000/api';
const projects = ref([]);
const isLoading = ref(true);
const isModalVisible = ref(false);
const editingProject = ref({});
const newImageFiles = ref([]);
const newImagePreviews = ref([]);
const TINYMCE_API_KEY = 'qm2jvf2rtb8o25awdkwtlfoo20vssnypfe4odow2tbl7h64v';

const tinymceConfig = {
  plugins: 'lists link image table code help wordcount autoresize',
  toolbar: 'undo redo | blocks | bold italic forecolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help',
  content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:16px }',
  height: 400,
};

const fetchData = async () => {
  isLoading.value = true;
  try {
    const response = await axios.get(`${API_URL}/portfolio/`);
    projects.value = response.data;
  } catch (error) {
    alert('Не удалось загрузить проекты.');
  } finally {
    isLoading.value = false;
  }
};

const openModal = (project = null) => {
  if (project) {
    editingProject.value = { 
      _id: project._id,
      title: project.title,
      category: project.category,
      description: project.description || '',
      date_completed: project.date_completed ? project.date_completed.split('T')[0] : new Date().toISOString().split('T')[0],
      existing_images: [...project.gallery_images]
    };
  } else {
    editingProject.value = { 
      title: '', 
      category: '', 
      description: '',
      date_completed: new Date().toISOString().split('T')[0],
      existing_images: [] 
    };
  }
  newImageFiles.value = [];
  newImagePreviews.value = [];
  isModalVisible.value = true;
};

const closeModal = () => {
  isModalVisible.value = false;
};

const handleFileChange = (event) => {
  const files = Array.from(event.target.files);
  if (!files.length) return;
  newImageFiles.value.push(...files);
  const previews = files.map(file => URL.createObjectURL(file));
  newImagePreviews.value.push(...previews);
  event.target.value = '';
};

const removeExistingImage = (index) => {
  if (editingProject.value && editingProject.value.existing_images) {
    editingProject.value.existing_images.splice(index, 1);
  }
};

const removeNewImage = (index) => {
  newImageFiles.value.splice(index, 1);
  newImagePreviews.value.splice(index, 1);
};

const saveProject = async () => {
  if (!editingProject.value) return;
  const formData = new FormData();
  formData.append('title', editingProject.value.title);
  formData.append('category', editingProject.value.category);
  formData.append('description', editingProject.value.description);
  formData.append('date_completed', editingProject.value.date_completed);

  for (const file of newImageFiles.value) {
    formData.append('gallery_images', file);
  }
  if (editingProject.value._id) {
    for (const imageUrl of editingProject.value.existing_images) {
      formData.append('existing_images', imageUrl);
    }
  }

  try {
    const headers = { 'Content-Type': 'multipart/form-data' };
    if (editingProject.value._id) {
      await axios.post(`${API_URL}/portfolio/update/${editingProject.value._id}/`, formData, { headers });
    } else {
      await axios.post(`${API_URL}/portfolio/create/`, formData, { headers });
    }
    closeModal();
    await fetchData();
  } catch (error) {
    console.error("ОШИБКА ПРИ СОХРАНЕНИИ:", error);
    const errorMsg = error.response?.data?.error || 'Неизвестная ошибка сервера.';
    alert('Ошибка при сохранении проекта: ' + errorMsg);
  }
};

const deleteProject = async (projectId) => {
  if (!confirm('Вы уверены, что хотите удалить этот проект?')) return;
  try {
    await axios.delete(`${API_URL}/portfolio/delete/${projectId}/`);
    await fetchData();
  } catch (error) {
    alert('Ошибка при удалении проекта.');
  }
};

onMounted(fetchData);
</script>

<style scoped>
.form-row { display: flex; gap: 1rem; }
.form-row .form-group { flex: 1; }
.portfolio-management{padding:2rem;background-color:#f4f7fa}.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:2rem}.header h1{font-size:2rem;color:#333}.projects-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:1.5rem}.project-card{background:#fff;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,.08);overflow:hidden;display:flex;flex-direction:column;transition:transform .2s ease,box-shadow .2s ease}.project-card:hover{transform:translateY(-5px);box-shadow:0 8px 20px rgba(0,0,0,.12)}.project-card img{width:100%;height:220px;object-fit:cover;border-bottom:1px solid #eee}.card-content{padding:1.5rem;flex-grow:1;display:flex;flex-direction:column}.card-content h3{margin:0 0 .5rem 0;font-size:1.25rem;color:#333}.card-content p{color:#666;flex-grow:1;margin:0 0 1.5rem 0;font-size:.9rem;background-color:#f0f0f0;padding:.25rem .5rem;border-radius:4px;align-self:flex-start}.card-actions{display:flex;gap:.75rem;margin-top:auto}button{padding:.6rem 1.2rem;border:none;border-radius:6px;font-weight:700;cursor:pointer;transition:background-color .2s,color .2s}.add-btn{background-color:#007bff;color:#fff}.add-btn:hover{background-color:#0056b3}.edit-btn,.save-btn{background-color:#28a745;color:#fff}.edit-btn:hover,.save-btn:hover{background-color:#218838}.delete-btn{background-color:#dc3545;color:#fff}.delete-btn:hover{background-color:#c82333}.cancel-btn{background-color:#6c757d;color:#fff}.cancel-btn:hover{background-color:#5a6268}.modal-overlay{position:fixed;top:0;left:0;width:100%;height:100%;background-color:rgba(0,0,0,.6);display:flex;justify-content:center;align-items:center;z-index:1000}.modal-content{background:#fff;padding:2rem;border-radius:12px;width:90%;max-width:800px;max-height:90vh;overflow-y:auto;box-shadow:0 10px 30px rgba(0,0,0,.2)}.modal-content h2{margin-top:0;margin-bottom:2rem;color:#333}.form-group{margin-bottom:1.5rem}.form-group label{display:block;margin-bottom:.5rem;font-weight:700;color:#555}.form-group input{width:100%;padding:.75rem;border:1px solid #ccc;border-radius:6px;font-size:1rem;box-sizing:border-box}.modal-actions{display:flex;justify-content:flex-end;gap:1rem;margin-top:2rem}.file-input{width:100%;padding:10px;border:1px solid #ccc;border-radius:6px}.previews-container{margin:1.5rem 0;padding:1rem;background-color:#f7f7f7;border-radius:8px}.previews-container h4{margin-top:0;margin-bottom:1rem;color:#333}.image-grid{display:flex;flex-wrap:wrap;gap:1rem}.img-preview{position:relative;width:120px;height:80px}.img-preview img{width:100%;height:100%;object-fit:cover;border-radius:6px}.remove-img-btn{position:absolute;top:-5px;right:-5px;width:24px;height:24px;background-color:#dc3545;color:#fff;border:none;border-radius:50%;cursor:pointer;font-size:14px;font-weight:700;display:flex;align-items:center;justify-content:center;line-height:1;padding:0}
</style>