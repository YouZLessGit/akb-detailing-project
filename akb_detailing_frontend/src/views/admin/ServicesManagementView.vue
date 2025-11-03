<!-- src/views/admin/ServicesManagementView.vue -->
<script setup>
import { ref, onMounted, computed } from 'vue' // <-- Добавляем computed
import axios from 'axios'

// --- СОСТОЯНИЯ КОМПОНЕНТА ---
const services = ref([])
const categories = ref([])
// ... (остальные состояния без изменений)
const newService = ref({
  category_id: null, name: '', main_image_url: '', short_description: '',
  price_from: null, duration: null, rich_content: '### Описание услуги\n\n'
})
const newCategory = ref({ name: '', parent_id: null, main_image_url: '', description: '' })
const isLoading = ref(true)
const error = ref(null)
const isServiceModalVisible = ref(false)
const editingService = ref(null)
const isCategoryModalVisible = ref(false)
const editingCategory = ref(null)

// --- API-ФУНКЦИИ ---
const API_URL = 'http://localhost:8000/api'

// --- НОВОЕ ВЫЧИСЛЯЕМОЕ СВОЙСТВО ДЛЯ ИЕРАРХИИ ---
const hierarchicalCategories = computed(() => {
  const map = new Map(categories.value.map(cat => [cat._id, { ...cat, children: [] }]));
  const roots = [];
  
  for (const cat of map.values()) {
    if (cat.parent_id && map.has(cat.parent_id)) {
      map.get(cat.parent_id).children.push(cat);
    } else {
      roots.push(cat);
    }
  }
  return roots;
});


const fetchData = async () => {
  isLoading.value = true
  try {
    const [servicesRes, categoriesRes] = await Promise.all([
      axios.get(`${API_URL}/services/admin-list/`),
      axios.get(`${API_URL}/services/categories/`)
    ]);
    services.value = servicesRes.data
    categories.value = categoriesRes.data
    error.value = null
  } catch (err) {
    error.value = 'Не удалось загрузить данные.'
    console.error(err);
  } finally {
    isLoading.value = false
  }
}

// --- Все остальные функции (addService, saveServiceChanges и т.д.) остаются без изменений ---
const addService = async () => {
  if (!newService.value.category_id) { alert('Пожалуйста, выберите категорию.'); return; }
  try {
    await axios.post(`${API_URL}/services/create/`, newService.value)
    newService.value = { category_id: null, name: '', main_image_url: '', short_description: '', price_from: null, duration: null, rich_content: '### Описание услуги\n\n' }
    await fetchData()
  } catch (err) { alert('Ошибка при добавлении услуги.') }
}
const saveServiceChanges = async () => {
  if (!editingService.value) return;
  try {
    await axios.put(`${API_URL}/services/update/${editingService.value._id}/`, editingService.value)
    isServiceModalVisible.value = false
    await fetchData()
  } catch (error) { alert("Ошибка при сохранении.") }
}
const deleteService = async (serviceId) => {
  if (!confirm('Вы уверены, что хотите удалить эту услугу?')) return;
  try {
    await axios.delete(`${API_URL}/services/delete/${serviceId}/`)
    await fetchData()
  } catch (error) { alert("Ошибка при удалении.") }
}
const openServiceModal = (service) => {
  editingService.value = JSON.parse(JSON.stringify(service));
  isServiceModalVisible.value = true
}
const addCategory = async () => {
  if (!newCategory.value.name.trim()) return;
  try {
    await axios.post(`${API_URL}/services/categories/create/`, newCategory.value)
    newCategory.value = { name: '', parent_id: null, main_image_url: '', description: '' }
    await fetchData()
  } catch (err) { alert('Ошибка при добавлении категории.') }
}
const saveCategoryChanges = async () => {
  if (!editingCategory.value) return;
  try {
    await axios.put(`${API_URL}/services/categories/update/${editingCategory.value._id}/`, editingCategory.value)
    isCategoryModalVisible.value = false
    await fetchData()
  } catch(err) { 
    // <<< УЛУЧШЕННАЯ ОБРАБОТКА ОШИБОК >>>
    // Пытаемся получить текст ошибки от сервера, если он есть
    const errorMessage = err.response?.data?.error || "Ошибка при сохранении категории.";
    alert(errorMessage);
    console.error(err);
  }
}
const deleteCategory = async (catId) => {
    if (!confirm('Удалить категорию? Сначала нужно удалить все дочерние категории и услуги в ней.')) return;
    try {
        await axios.delete(`${API_URL}/services/categories/delete/${catId}/`);
        await fetchData();
    } catch (err) { alert(err.response?.data?.error || 'Ошибка при удалении категории.'); }
}
const openCategoryModal = (category) => {
  // Важно: для редактирования передаем "плоскую" категорию, а не из дерева
  const originalCategory = categories.value.find(c => c._id === category._id);
  editingCategory.value = JSON.parse(JSON.stringify(originalCategory));
  isCategoryModalVisible.value = true
}


onMounted(fetchData)
</script>

<template>
  <div class="services-management">
    <h1>Управление услугами и категориями</h1>
    
    <div class="layout-grid">
      <!-- ЛЕВАЯ КОЛОНКА: УПРАВЛЕНИЕ КАТЕГОРИЯМИ -->
      <div class="form-container">
        <h2>Категории услуг</h2>
        <!-- ИЗМЕНЕНИЕ: Используем новый иерархический список -->
        <div v-if="categories.length > 0" class="category-list-container">
          <ul class="category-list">
            <template v-for="cat in hierarchicalCategories" :key="cat._id">
              <li>
                <span>{{ cat.name }}</span>
                <div class="actions">
                  <button class="edit-btn-small" @click="openCategoryModal(cat)" title="Редактировать категорию">✏️</button>
                  <button class="delete-btn-small" @click="deleteCategory(cat._id)" title="Удалить категорию">×</button>
                </div>
              </li>
              <!-- Рендерим дочерние категории с отступом -->
              <li v-for="child in cat.children" :key="child._id" class="child-category">
                 <span> L {{ child.name }}</span>
                 <div class="actions">
                  <button class="edit-btn-small" @click="openCategoryModal(child)" title="Редактировать категорию">✏️</button>
                  <button class="delete-btn-small" @click="deleteCategory(child._id)" title="Удалить категорию">×</button>
                </div>
              </li>
            </template>
          </ul>
        </div>

        <p v-else>Категории не найдены.</p>
        <hr>
        <h3>Добавить категорию</h3>
        <form @submit.prevent="addCategory" class="category-form">
          <div class="form-group">
            <label>Название</label>
            <input type="text" v-model="newCategory.name" placeholder="Название..." required />
          </div>
          <div class="form-group">
            <label>Родительская категория</label>
            <select v-model="newCategory.parent_id">
              <option :value="null">-- Нет (Верхний уровень) --</option>
              <!-- Используем плоский список для выбора родителя -->
              <option v-for="cat in categories" :key="cat._id" :value="cat._id">{{ cat.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>URL картинки</label>
            <input type="text" v-model="newCategory.main_image_url" placeholder="https://..." />
          </div>
          <div class="form-group">
            <label>Краткое описание</label>
            <textarea v-model="newCategory.description" rows="2" placeholder="Описание для страницы..."></textarea>
          </div>
          <button type="submit">Добавить категорию</button>
        </form>
      </div>

      <!-- ПРАВАЯ КОЛОНКА: ОСТАЕТСЯ БЕЗ ИЗМЕНЕНИЙ -->
      <div class="form-container">
        <h2>Быстрое добавление услуги</h2>
        <form @submit.prevent="addService" class="pro-form">
          <div class="form-group">
            <label>Категория</label>
            <select v-model="newService.category_id" required>
              <option :value="null" disabled>-- Выберите категорию --</option>
              <option v-for="cat in categories" :key="cat._id" :value="cat._id">{{ cat.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Название услуги</label>
            <input type="text" v-model="newService.name" required>
          </div>
          <div class="form-group">
            <label>Краткое описание (для списков)</label>
            <input type="text" v-model="newService.short_description">
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Цена "от" (руб.)</label>
              <input type="number" v-model.number="newService.price_from" required>
            </div>
            <div class="form-group">
              <label>Длительность (мин.)</label>
              <input type="number" v-model.number="newService.duration" required>
            </div>
          </div>
          <button type="submit">Добавить услугу</button>
        </form>
      </div>
    </div>
    
    <hr>
    
    <h2>Список существующих услуг</h2>
    <!-- Этот блок остается без изменений -->
    <div v-if="isLoading">Загрузка данных...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else-if="services.length > 0">
      <div v-for="group in services" :key="group.category_id" class="category-group">
        <h3>{{ group.category_name }}</h3>
        <ul class="service-list">
          <li v-for="service in group.services" :key="service._id">
            <div class="service-details">
              <strong>{{ service.name }}</strong> (от {{ service.price_from }} руб.)
              <p>{{ service.short_description }}</p>
            </div>
            <div class="service-actions">
              <button @click="openServiceModal(service)" class="edit-btn">Полное редактирование</button>
              <button @click="deleteService(service._id)" class="delete-btn">Удалить</button>
            </div>
          </li>
        </ul>
      </div>
    </div>
    <div v-else>
      <p>Услуги еще не созданы.</p>
    </div>
    
    <!-- Модальные окна остаются без изменений -->
    <div v-if="isServiceModalVisible" class="modal-overlay" @click.self="isServiceModalVisible = false">
      <div class="modal-content pro-modal">
        <h2>Редактировать услугу</h2>
        <form v-if="editingService" @submit.prevent="saveServiceChanges">
          <div class="form-group"><label>Категория</label><select v-model="editingService.category_id" required><option v-for="cat in categories" :key="cat._id" :value="cat._id">{{ cat.name }}</option></select></div>
          <div class="form-group"><label>Название услуги</label><input type="text" v-model="editingService.name" required></div>
          <div class="form-group">
            <label>Slug (URL, генерируется автоматически)</label>
            <input type="text" v-model="editingService.slug" readonly class="readonly-input">
          </div>
          <div class="form-group"><label>URL главной картинки</label><input type="text" v-model="editingService.main_image_url"></div>
          <div class="form-group"><label>Краткое описание</label><input type="text" v-model="editingService.short_description"></div>
          <div class="form-row">
            <div class="form-group"><label>Цена "от"</label><input type="number" v-model.number="editingService.price_from" required></div>
            <div class="form-group"><label>Длительность (мин.)</label><input type="number" v-model.number="editingService.duration" required></div>
          </div>
          <div class="form-group"><label>Полное описание (Markdown)</label><textarea v-model="editingService.rich_content" rows="10"></textarea></div>
          <div class="modal-actions">
            <button type="submit" class="save-btn">Сохранить</button>
            <button type="button" class="cancel-btn" @click="isServiceModalVisible = false">Отмена</button>
          </div>
        </form>
      </div>
    </div>
    <div v-if="isCategoryModalVisible" class="modal-overlay" @click.self="isCategoryModalVisible = false">
      <div class="modal-content">
        <h2>Редактировать категорию</h2>
        <form v-if="editingCategory" @submit.prevent="saveCategoryChanges">
          <div class="form-group"><label>Название категории</label><input type="text" v-model="editingCategory.name" required></div>
          <div class="form-group">
            <label>Родительская категория</label>
            <select v-model="editingCategory.parent_id">
              <option :value="null">-- Нет (Верхний уровень) --</option>
              <option v-for="cat in categories.filter(c => c._id !== editingCategory._id)" :key="cat._id" :value="cat._id">{{ cat.name }}</option>
            </select>
          </div>
          <div class="form-group"><label>URL главной картинки</label><input type="text" v-model="editingCategory.main_image_url"></div>
          <div class="form-group"><label>Краткое описание</label><textarea v-model="editingCategory.description" rows="3"></textarea></div>
          <div class="modal-actions">
            <button type="submit" class="save-btn">Сохранить</button>
            <button type="button" class="cancel-btn" @click="isCategoryModalVisible = false">Отмена</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* ... (все ваши стили остаются без изменений) */
.layout-grid {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 2rem;
  align-items: flex-start;
}
h1, h2, h3 {
  margin-top: 0;
}
h1 {
  border-bottom: 2px solid #ddd;
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
}
h2 {
  margin-bottom: 1rem;
}
h3 {
  margin-top: 1.5rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}
.form-container {
  background-color: #f9f9f9;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}
.form-group input, .form-group textarea, .form-group select {
  width: 100%;
  padding: 0.7rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}
.form-row {
  display: flex;
  gap: 20px;
}
.form-row .form-group {
  flex: 1;
}
button {
  padding: 0.7rem 1.2rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}
button[type="submit"] {
  background-color: #28a745;
  color: white;
  width: 100%;
}
hr {
  margin: 2rem 0;
}
ul {
  list-style: none;
  padding: 0;
}
li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.7rem;
  border-bottom: 1px solid #eee;
}
li:last-child {
  border-bottom: none;
}
/* НОВЫЙ СТИЛЬ для дочерних категорий */
.child-category {
  padding-left: 2rem; /* Отступ */
  background-color: #f8f9fa;
}
.child-category span {
    color: #555;
}
.service-list {
  padding-left: 1rem;
  border-left: 2px solid #eee;
}
.service-details p {
  font-size: 0.9rem;
  color: #666;
  margin-top: 0.25rem;
}
.service-actions button {
  margin-left: 0.5rem;
}
.edit-btn {
  background-color: #ffc107;
}
.delete-btn {
  background-color: #dc3545;
  color: white;
}
.delete-btn-small, .edit-btn-small {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0 5px;
}
.category-list {
  margin-bottom: 1rem;
}
.category-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.category-group {
  margin-bottom: 2rem;
}
.actions {
  display: flex;
  align-items: center;
}
.readonly-input {
  background-color: #e9ecef;
  color: #6c757d;
  cursor: not-allowed;
}
/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}
.pro-modal {
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.5rem;
  gap: 0.5rem;
}
.save-btn {
  background-color: #007bff;
  color: white;
}
.cancel-btn {
  background-color: #6c757d;
  color: white;
}
</style>