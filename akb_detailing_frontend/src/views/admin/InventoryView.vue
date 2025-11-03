<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

// --- Состояния ---
const inventoryItems = ref([]);
const categories = ref([]); // Плоский список с API
const isLoading = ref(true);

const newItem = ref({
    name: '',
    quantity: 0,
    unit: 'мл.',
    cost: null,
    category_id: null,
    low_stock_threshold: 10
});
const unitOptions = ['шт.', 'мл.', 'л.', 'м.', 'уп.'];

// Для модальных окон Товаров
const isEditItemModalVisible = ref(false);
const editingItem = ref(null);
const isMovementModalVisible = ref(false);
const selectedItem = ref(null);
const movementData = ref({ quantity: null, type: 'withdrawal' }); // withdrawal | replenishment

// Состояния для Категорий
const newCategory = ref({ name: '', parent_id: null });
const isEditCategoryModalVisible = ref(false);
const editingCategory = ref(null);

const currentUser = computed(() => {
  const data = sessionStorage.getItem('user-data');
  return data ? JSON.parse(data) : null;
});

// --- Computed: Построение дерева категорий ---
const categoryTree = computed(() => {
  const map = {};
  const roots = [];
  // Сначала создаем карту всех категорий по их ID
  categories.value.forEach(cat => {
    map[cat._id] = { ...cat, children: [] };
  });
  // Затем проходимся по карте и строим иерархию
  Object.values(map).forEach(cat => {
    if (cat.parent_id && map[cat.parent_id]) {
      map[cat.parent_id].children.push(cat);
    } else {
      roots.push(cat); // Это корневая категория
    }
  });
  return roots;
});

const fetchData = async () => {
  isLoading.value = true;
  try {
    const [itemsRes, categoriesRes] = await Promise.all([
      axios.get('http://localhost:8000/api/inventory/'),
      axios.get('http://localhost:8000/api/inventory/categories/')
    ]);
    inventoryItems.value = itemsRes.data;
    categories.value = categoriesRes.data;
  } catch (error) { 
    // --- УЛУЧШЕННАЯ ОБРАБОТКА ОШИБОК ---
    console.error("Произошла ошибка при загрузке данных склада:", error);
    if (error.response) {
      // Ошибка пришла с сервера (например, 404, 500)
      alert(`Не удалось загрузить данные склада. Сервер ответил: ${error.response.status} ${error.response.statusText}`);
    } else if (error.request) {
      // Запрос был сделан, но ответа не было (например, сервер не запущен)
      alert('Не удалось загрузить данные склада. Сервер не отвечает.');
    } else {
      // Что-то пошло не так при настройке запроса
      alert('Не удалось загрузить данные склада. Произошла ошибка в запросе.');
    }
  } 
  finally { isLoading.value = false; }
};

const getCategoryName = (categoryId) => categories.value.find(c => c._id === categoryId)?.name || 'Без категории';

// --- Функции Управления Категориями ---
const createCategory = async () => {
    if (!newCategory.value.name.trim()) return alert('Название категории не может быть пустым.');
    try {
        await axios.post('http://localhost:8000/api/inventory/categories/create/', newCategory.value);
        newCategory.value = { name: '', parent_id: null };
        await fetchData();
    } catch (error) { 
        alert(error.response?.data?.error || 'Ошибка при создании категории.'); 
    }
};

const openEditCategoryModal = (category) => {
    editingCategory.value = { ...category };
    isEditCategoryModalVisible.value = true;
};

const saveCategoryChanges = async () => {
    if (!editingCategory.value || !editingCategory.value.name.trim()) return alert('Название не может быть пустым.');
    try {
        await axios.put(`http://localhost:8000/api/inventory/categories/update/${editingCategory.value._id}/`, editingCategory.value);
        isEditCategoryModalVisible.value = false;
        await fetchData();
    } catch (error) { 
        alert(error.response?.data?.error || 'Ошибка при обновлении категории.'); 
    }
};

const deleteCategory = async (categoryId) => {
    if (!confirm('Вы уверены, что хотите удалить эту категорию? Она будет удалена, только если в ней нет подкатегорий.')) return;
    try {
        await axios.delete(`http://localhost:8000/api/inventory/categories/delete/${categoryId}/`);
        await fetchData();
    } catch (error) { 
        alert(error.response?.data?.error || 'Ошибка при удалении категории.'); 
    }
};

// --- Функции Управления Товарами ---
const createItem = async () => {
    if (!newItem.value.name || newItem.value.quantity < 0 || !newItem.value.cost || !newItem.value.category_id) {
        return alert('Все поля, кроме порога остатка, обязательны.');
    }
    try {
        await axios.post('http://localhost:8000/api/inventory/create/', newItem.value);
        newItem.value = { name: '', quantity: 0, unit: 'мл.', cost: null, category_id: null };
        await fetchData();
    } catch (error) {
        alert('Ошибка при создании позиции.');
    }
};

const openEditItemModal = (item) => {
    editingItem.value = { ...item };
    isEditItemModalVisible.value = true;
};

const saveItemChanges = async () => {
    if (!editingItem.value) return;
    try {
        await axios.put(`http://localhost:8000/api/inventory/update/${editingItem.value._id}/`, editingItem.value);
        isEditItemModalVisible.value = false;
        await fetchData();
    } catch (error) {
        alert('Ошибка при сохранении изменений товара.');
    }
};

// --- Функции Управления Движением (Списание/Пополнение) ---
const openMovementModal = (item, type) => {
  selectedItem.value = item;
  movementData.value = { quantity: null, type: type };
  isMovementModalVisible.value = true;
};

const submitMovement = async () => {
  if (!selectedItem.value || !movementData.value.quantity || movementData.value.quantity <= 0) {
    return alert('Введите корректное количество.');
  }
  if (!currentUser.value?._id) {
    return alert('Не удалось определить пользователя.');
  }

  try {
    const payload = {
      item_id: selectedItem.value._id,
      change_quantity: movementData.value.quantity,
      type: movementData.value.type,
      employee_id: currentUser.value._id,
    };
    await axios.post('http://localhost:8000/api/inventory/movement/', payload);
    
    isMovementModalVisible.value = false;
    await fetchData();
  } catch (error) {
    alert(error.response?.data?.error || 'Ошибка при выполнении операции.');
  }
};

onMounted(fetchData);
</script>

<template>
  <div class="inventory-view">
    <h1 class="view-title">Склад</h1>
    
    <div class="category-manager">
        <div class="form-container">
            <h2>Управление категориями</h2>
            <form @submit.prevent="createCategory" class="create-form">
                <input type="text" v-model="newCategory.name" placeholder="Название..." required>
                <select v-model="newCategory.parent_id">
                    <option :value="null">-- Корневая категория --</option>
                    <option v-for="cat in categories" :key="cat._id" :value="cat._id">{{ cat.name }}</option>
                </select>
                <button type="submit">Добавить категорию</button>
            </form>
            
            <ul class="category-list">
                <p v-if="categories.length === 0">Категории еще не созданы.</p>
                <template v-for="cat in categoryTree" :key="cat._id">
                    <li>
                        <span>{{ cat.name }}</span>
                        <div class="actions">
                            <button class="btn-edit" @click="openEditCategoryModal(cat)">Изм.</button>
                            <button class="btn-delete" @click="deleteCategory(cat._id)">Уд.</button>
                        </div>
                    </li>
                    <li v-for="subCat in cat.children" :key="subCat._id" class="subcategory">
                        <span>{{ subCat.name }}</span>
                        <div class="actions">
                            <button class="btn-edit" @click="openEditCategoryModal(subCat)">Изм.</button>
                            <button class="btn-delete" @click="deleteCategory(subCat._id)">Уд.</button>
                        </div>
                    </li>
                </template>
            </ul>
        </div>
    </div>
    
    <div class="items-manager">
        <div class="form-container">
        <h2>Добавить новую позицию на склад</h2>
        <form @submit.prevent="createItem" class="create-form">
            <input type="text" v-model="newItem.name" placeholder="Название материала" required>
            <select v-model="newItem.category_id" required>
                <option :value="null" disabled>Выберите категорию</option>
                <template v-for="cat in categoryTree" :key="cat._id">
                    <optgroup :label="cat.name">
                        <option :value="cat._id">{{ cat.name }}</option>
                        <option v-for="subCat in cat.children" :key="subCat._id" :value="subCat._id">
                            - {{ subCat.name }}
                        </option>
                    </optgroup>
                </template>
                <option v-if="categories.length === 0" disabled>Сначала создайте категорию</option>
            </select>
            <input type="number" v-model.number="newItem.cost" placeholder="Стоимость (BYN)" required min="0" step="any">
            <input type="number" v-model.number="newItem.quantity" placeholder="Начальное кол-во" required min="0" step="any">
            <select v-model="newItem.unit">
                <option v-for="unit in unitOptions" :key="unit" :value="unit">{{ unit }}</option>
            </select>
            <button type="submit">Добавить товар</button>
        </form>
        </div>
        
        <h2>Список позиций</h2>
        <div v-if="isLoading">Загрузка...</div>
        <div v-else-if="inventoryItems.length === 0" class="no-items-message">На складе пока нет товаров.</div>
        <ul v-else class="inventory-list">
        <li v-for="item in inventoryItems" :key="item._id">
            <div class="item-info">
            <strong>{{ item.name }}</strong>
            <small>{{ getCategoryName(item.category_id) }} - {{ item.cost }} BYN</small>
            </div>
            <div class="item-quantity">
            <span>{{ item.quantity }} {{ item.unit }}</span>
            </div>
            <div class="item-actions">
            <button class="btn-edit" @click="openEditItemModal(item)">Изм.</button>
            <button class="btn-withdraw" @click="openMovementModal(item, 'withdrawal')">Списать</button>
            <button class="btn-replenish" @click="openMovementModal(item, 'replenishment')">Пополнить</button>
            </div>
        </li>
        </ul>
    </div>

    <!-- Модальное окно Редактирования Категории -->
    <div v-if="isEditCategoryModalVisible" class="modal-overlay" @click.self="isEditCategoryModalVisible = false">
      <div class="modal-content" v-if="editingCategory">
        <h2>Редактировать категорию</h2>
        <form @submit.prevent="saveCategoryChanges">
            <div class="form-group">
                <label>Название категории</label>
                <input type="text" v-model="editingCategory.name" required>
            </div>
            <div class="form-group">
                <label>Родительская категория</label>
                <select v-model="editingCategory.parent_id">
                    <option :value="null">-- Корневая категория --</option>
                    <option v-for="cat in categories" :key="cat._id" :value="cat._id" :disabled="cat._id === editingCategory._id">
                        {{ cat.name }}
                    </option>
                </select>
            </div>
          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="isEditCategoryModalVisible = false">Отмена</button>
            <button type="submit" class="save-btn">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно Редактирования Товара -->
    <div v-if="isEditItemModalVisible" class="modal-overlay" @click.self="isEditItemModalVisible = false">
      <div class="modal-content" v-if="editingItem">
        <h2>Редактировать: {{ editingItem.name }}</h2>
        <form @submit.prevent="saveItemChanges">
            <div class="form-group">
                <label>Название</label>
                <input type="text" v-model="editingItem.name" required>
            </div>
            <div class="form-group">
                <label>Категория</label>
                <select v-model="editingItem.category_id" required>
                    <option v-for="cat in categories" :key="cat._id" :value="cat._id">{{ cat.name }}</option>
                </select>
            </div>
            <div class="form-group">
                <label>Стоимость (BYN)</label>
                <input type="number" v-model.number="editingItem.cost" required min="0" step="any">
            </div>
            <div class="form-group">
                <label>Единица изм.</label>
                <select v-model="editingItem.unit">
                    <option v-for="unit in unitOptions" :key="unit" :value="unit">{{ unit }}</option>
                </select>
            </div>
          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="isEditItemModalVisible = false">Отмена</button>
            <button type="submit" class="save-btn">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно Списания/Пополнения -->
    <div v-if="isMovementModalVisible" class="modal-overlay" @click.self="isMovementModalVisible = false">
      <div class="modal-content">
        <h2 v-if="movementData.type === 'withdrawal'">Списать: {{ selectedItem.name }}</h2>
        <h2 v-else>Пополнить: {{ selectedItem.name }}</h2>
        <form @submit.prevent="submitMovement">
          <div class="form-group">
            <label>Количество ({{ selectedItem.unit }})</label>
            <input type="number" v-model.number="movementData.quantity" required min="0.01" step="any">
          </div>
          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="isMovementModalVisible = false">Отмена</button>
            <button type="submit" class="save-btn">Подтвердить</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<style scoped>
.inventory-view { display: grid; grid-template-columns: 350px 1fr; gap: 2rem; align-items: start; }
.view-title { grid-column: 1 / -1; border-bottom: 1px solid #eee; padding-bottom: 1rem; margin-bottom: 0; margin-top: 0; }
.category-manager { grid-column: 1; position: sticky; top: 20px; }
.items-manager { grid-column: 2; }
.form-container { background-color: #fff; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 1rem;}
.create-form { display: flex; flex-direction: column; gap: 1rem; }
.create-form input, .create-form select { width: 100%; box-sizing: border-box; padding: 0.75rem; border: 1px solid #ccc; border-radius: 4px; }
.create-form button { background-color: #007bff; color: white; border: none; padding: 0.75rem; cursor: pointer; border-radius: 4px; }
.category-list { list-style: none; padding: 0; margin-top: 1rem; max-height: 40vh; overflow-y: auto; }
.category-list li { display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; border-bottom: 1px solid #eee; }
.category-list li:hover { background-color: #f9f9f9; }
.category-list .actions { display: flex; }
.category-list .actions button { margin-left: 0.5rem; padding: 0.2rem 0.5rem; font-size: 0.75rem; }
.subcategory { padding-left: 1.5rem !important; background-color: #f8fafc; font-size: 0.9rem; }
h2 { margin-top: 0; margin-bottom: 1.5rem; }
.inventory-list { list-style: none; padding: 0; margin: 0; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.inventory-list li { display: flex; align-items: center; padding: 1rem; border-bottom: 1px solid #eee; }
.item-info { flex-grow: 1; font-weight: 500; }
.item-info small { display: block; color: #666; font-size: 0.8rem; }
.item-quantity { width: 150px; text-align: right; font-size: 1.1rem; }
.item-actions { margin-left: 20px; display: flex; }
.item-actions button { margin-left: 0.5rem; padding: 0.4rem 0.8rem; font-size: 0.8rem; border: none; cursor: pointer; border-radius: 4px; }
.no-items-message { background-color: #fff; padding: 2rem; text-align: center; color: #666; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.btn-edit { background-color: #ffc107; color: #212529; }
.btn-delete { background-color: #dc3545; color: white; }
.btn-withdraw { background-color: #f97316; color: white; }
.btn-replenish { background-color: #22c55e; color: white; }
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background-color: white; padding: 2rem; border-radius: 8px; width: 90%; max-width: 500px; }
.modal-actions { display: flex; justify-content: flex-end; margin-top: 1.5rem; gap: 0.5rem; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
.form-group input, .form-group select { width: 100%; padding: 0.5rem; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
.save-btn { background-color: #28a745; color: white; }
.cancel-btn { background-color: #6c757d; color: white; }
</style>