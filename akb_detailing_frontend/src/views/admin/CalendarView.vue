<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { Calendar as VCalendar } from 'v-calendar'
import 'v-calendar/style.css'

// --- СОСТОЯНИЯ КОМПОНЕНТА ---
const isLoading = ref(true)
const orders = ref([])
const clients = ref([])
const cars = ref([])
const services = ref([])
const employees = ref([])
const inventoryItems = ref([]) // <-- Состояние для склада
const selectedDate = ref(new Date())

const isCreateModalVisible = ref(false)
const newOrder = ref({
  start_time: '',
  client_id: '',
  car_id: '',
  service_ids: []
})

const isDetailsModalVisible = ref(false)
const selectedOrder = ref(null)
const availableStatuses = ['Запланирован', 'Ожидает подтверждения', 'В работе', 'Выполнен', 'Отменен']

const materialToUse = ref({
  itemId: null,
  quantity: null
});

const currentUser = computed(() => {
  const data = sessionStorage.getItem('user-data');
  return data ? JSON.parse(data) : null;
});

// --- ЗАГРУЗКА ДАННЫХ ---
const fetchData = async () => {
  isLoading.value = true
  try {
    const res = await Promise.all([
      axios.get('http://localhost:8000/api/orders/'),
      axios.get('http://localhost:8000/api/clients/'),
      axios.get('http://localhost:8000/api/cars/'),
      // <<< ИСПРАВЛЕНИЕ №1: ИСПОЛЬЗУЕМ НОВЫЙ URL ДЛЯ ПОЛУЧЕНИЯ ПЛОСКОГО СПИСКА УСЛУГ >>>
      axios.get('http://localhost:8000/api/services/list/'),
      axios.get('http://localhost:8000/api/employees/'),
      axios.get('http://localhost:8000/api/inventory/')
    ])
    orders.value = res[0].data
    clients.value = res[1].data
    cars.value = res[2].data
    services.value = res[3].data // Данные теперь приходят в формате { id, name, price, ... }
    employees.value = res[4].data
    inventoryItems.value = res[5].data
  } catch (error) {
    alert("Не удалось загрузить все данные для календаря.")
    console.error("Ошибка загрузки:", error)
  } finally {
    isLoading.value = false
  }
}

// --- ЦВЕТА И АТРИБУТЫ ---
const statusColors = {
  'Запланирован': '#3b82f6',
  'Ожидает подтверждения': '#eab308', // Добавлен цвет для нового статуса
  'В работе': '#f97316',
  'Выполнен': '#22c55e',
  'Отменен': '#ef4444',
}

const attributes = computed(() => {
  return orders.value.map(order => {
    return {
      key: order._id,
      dot: statusColors[order.status] || 'gray',
      dates: new Date(order.start_time),
      customData: order,
    }
  })
})

const availableCars = computed(() => {
  if (!newOrder.value.client_id) return []
  return cars.value.filter(car => car.client_id === newOrder.value.client_id)
})

// --- COMPUTED PROPERTIES ДЛЯ ТАЙМЛАЙНА ---
const timelineSlots = computed(() => {
  const slots = []
  for (let h = 9; h <= 19; h++) {
    slots.push(`${h.toString().padStart(2, '0')}:00`)
    if (h < 19) {
      slots.push(`${h.toString().padStart(2, '0')}:30`)
    }
  }
  slots.push('20:00');
  return slots
})

const dailyOrders = computed(() => {
  if (!selectedDate.value) return []
  return orders.value
    .filter(order => {
      const orderDate = new Date(order.start_time)
      const selDate = selectedDate.value
      return orderDate.getFullYear() === selDate.getFullYear() &&
             orderDate.getMonth() === selDate.getMonth() &&
             orderDate.getDate() === selDate.getDate()
    })
    .map(order => {
      const client = clients.value.find(c => c._id === order.client_id)
      const car = cars.value.find(c => c._id === order.car_id)
      // <<< ИСПРАВЛЕНИЕ №2: ИЩЕМ УСЛУГИ ПО ПОЛЮ 'id', А НЕ '_id' >>>
      const serviceDetails = order.service_ids.map(id => services.value.find(s => s.id === id)).filter(Boolean);
      const employee = employees.value.find(e => e._id === order.employee_id)
      return {
        ...order,
        clientName: client?.full_name || 'Клиент не найден',
        carInfo: car ? `${car.make} ${car.model} (${car.license_plate})` : 'Авто не найдено',
        serviceDetails,
        employeeName: employee?.full_name || 'Не назначен'
      }
    })
    .sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
})

const formattedSelectedDate = computed(() => {
  return selectedDate.value.toLocaleString('ru-RU', {
    day: '2-digit',
    month: 'long',
    weekday: 'long'
  });
})

// --- ФУНКЦИИ ДЛЯ ТАЙМЛАЙНА ---
const getOrderPosition = (order) => {
  const start = new Date(order.start_time)
  const end = new Date(order.end_time)
  const getRowIndex = (time) => {
    const startOfDayMinutes = 9 * 60
    const currentMinutes = time.getHours() * 60 + time.getMinutes()
    const minutesFromStart = currentMinutes - startOfDayMinutes
    return (minutesFromStart / 30) + 1
  }
  const startRow = getRowIndex(start)
  const endRow = getRowIndex(end)
  return {
    gridRow: `${startRow} / ${endRow}`,
    gridColumn: 2,
    backgroundColor: statusColors[order.status] ? `${statusColors[order.status]}20` : '#eee',
    borderColor: statusColors[order.status] || '#ccc'
  }
}

const formatTime = (isoString) => {
  const date = new Date(isoString);
  return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
}

// --- ФУНКЦИИ УПРАВЛЕНИЯ ЗАКАЗАМИ ---
const handleDayClick = (day) => {
  selectedDate.value = day.date
}

const openCreateModal = () => {
    const now = new Date();
    const startTime = new Date(selectedDate.value);
    startTime.setHours(now.getHours(), Math.ceil(now.getMinutes() / 30) * 30, 0, 0);
    newOrder.value.start_time = startTime.toISOString().slice(0, 16);
    newOrder.value.client_id = '';
    newOrder.value.car_id = '';
    newOrder.value.service_ids = [];
    isCreateModalVisible.value = true;
}

const openDetailsModalFromTimeline = (order) => {
  selectedOrder.value = { ...order };
  isDetailsModalVisible.value = true;
};

const createOrder = async () => {
  if (!newOrder.value.client_id || !newOrder.value.car_id || newOrder.value.service_ids.length === 0) {
    alert("Пожалуйста, заполните все поля.");
    return;
  }
  try {
    const orderData = { ...newOrder.value, start_time: `${newOrder.value.start_time}:00Z` };
    await axios.post('http://localhost:8000/api/orders/create/', orderData);
    isCreateModalVisible.value = false;
    await fetchData();
  } catch (error) {
    if (error.response?.status === 409) {
      alert(`Ошибка: ${error.response.data.error}`);
    } else {
      alert("Произошла ошибка при создании заказа.");
    }
    console.error(error);
  }
}

const updateOrder = async () => {
  if (!selectedOrder.value) return;
  try {
    const payload = {
      status: selectedOrder.value.status,
      employee_id: selectedOrder.value.employee_id || null
    };
    await axios.put(`http://localhost:8000/api/orders/update/${selectedOrder.value._id}/`, payload);
    const orderInList = orders.value.find(o => o._id === selectedOrder.value._id);
    if (orderInList) {
      orderInList.status = selectedOrder.value.status;
      orderInList.employee_id = selectedOrder.value.employee_id;
    }
    isDetailsModalVisible.value = false;
  } catch (error) {
    alert("Ошибка при обновлении заказа.");
    console.error(error);
  }
}

const deleteOrder = async () => {
  if (!selectedOrder.value) return;
  if (!confirm('Вы уверены, что хотите удалить этот заказ?')) return;
  try {
    await axios.delete(`http://localhost:8000/api/orders/delete/${selectedOrder.value._id}/`);
    orders.value = orders.value.filter(o => o._id !== selectedOrder.value._id);
    isDetailsModalVisible.value = false;
  } catch (error) {
    alert("Ошибка при удалении заказа.");
    console.error(error);
  }
}

const useMaterialOnOrder = async () => {
  if (!materialToUse.value.itemId || !materialToUse.value.quantity || materialToUse.value.quantity <= 0) {
    return alert('Выберите материал и укажите корректное количество.');
  }
  if (!currentUser.value?._id) {
    return alert('Не удалось определить текущего пользователя. Попробуйте войти заново.');
  }
  try {
    const payload = {
      item_id: materialToUse.value.itemId,
      change_quantity: materialToUse.value.quantity,
      type: 'withdrawal',
      employee_id: currentUser.value._id,
      order_id: selectedOrder.value._id,
    };
    await axios.post('http://localhost:8000/api/inventory/movement/', payload);
    alert('Материал успешно списан!');
    const usedItem = inventoryItems.value.find(item => item._id === materialToUse.value.itemId);
    if (usedItem) {
        usedItem.quantity -= materialToUse.value.quantity;
    }
    materialToUse.value = { itemId: null, quantity: null };
  } catch (error) {
    alert(error.response?.data?.error || 'Ошибка при списании материала.');
    console.error(error);
  }
};

onMounted(fetchData);
</script>

<template>
  <div class="calendar-page">
    <div class="header">
      <h1>Календарь Записи</h1>
      <button class="create-order-btn-header" @click="openCreateModal">+ Новая Запись</button>
    </div>

    <div v-if="isLoading">Загрузка календаря...</div>

    <div v-else class="calendar-layout">
      <!-- 1. ЛЕВАЯ КОЛОНКА: КАЛЕНДАРЬ МЕСЯЦА -->
      <div class="calendar-month-container">
        <v-calendar 
          class="custom-calendar" 
          :attributes="attributes" 
          @dayclick="handleDayClick" 
          is-expanded 
          v-model="selectedDate"
        />
      </div>

      <!-- 2. ПРАВАЯ КОЛОНКА: DAILY TIMELINE -->
      <div class="timeline-container">
        <h2>{{ formattedSelectedDate }}</h2>
        <div class="timeline-grid-wrapper">
          <div v-if="dailyOrders.length === 0" class="no-orders-message">
            <span>На эту дату нет запланированных записей.</span>
          </div>
          <div v-else class="timeline-grid">
            <div
              v-for="(slot, index) in timelineSlots" :key="index" class="time-slot" :style="{ gridRow: index + 1 }">
              {{ slot }}
            </div>
            <div
              v-for="order in dailyOrders" :key="order._id" class="order-card" :style="getOrderPosition(order)" @click="openDetailsModalFromTimeline(order)">
              <strong>{{ order.clientName }} - {{ order.carInfo }}</strong>
              <div class="order-price">{{ order.total_price }} ₽</div>
              <div class="employee-info">👤 {{ order.employeeName }}</div>
              <small class="order-time">{{ formatTime(order.start_time) }} - {{ formatTime(order.end_time) }}</small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно для СОЗДАНИЯ заказа -->
    <div v-if="isCreateModalVisible" class="modal-overlay" @click.self="isCreateModalVisible = false">
      <div class="modal-content">
        <h2>Новая запись</h2>
        <form @submit.prevent="createOrder">
          <div class="form-group">
            <label>Время начала</label>
            <input type="datetime-local" v-model="newOrder.start_time" required />
          </div>
          <div class="form-group">
            <label>Клиент</label>
            <select v-model="newOrder.client_id" required @change="newOrder.car_id = ''">
              <option disabled value="">Выберите клиента</option>
              <option v-for="client in clients" :key="client._id" :value="client._id">
                {{ client.full_name }}
              </option>
            </select>
          </div>
          <div class="form-group" v-if="newOrder.client_id">
            <label>Автомобиль</label>
            <select v-model="newOrder.car_id" required :disabled="availableCars.length === 0">
              <option disabled value="">Выберите автомобиль</option>
              <option v-for="car in availableCars" :key="car._id" :value="car._id">
                {{ car.make }} {{ car.model }} ({{ car.license_plate }})
              </option>
            </select>
            <small v-if="availableCars.length === 0">У этого клиента нет автомобилей.</small>
          </div>
          <div class="form-group">
            <label>Услуги (удерживайте Ctrl/Cmd для выбора нескольких)</label>
            <select v-model="newOrder.service_ids" multiple required size="5">
              <!-- <<< ИСПРАВЛЕНИЕ №3: ИСПОЛЬЗУЕМ 'service.id' ВМЕСТО 'service._id' >>> -->
              <option v-for="service in services" :key="service.id" :value="service.id">
                {{ service.name }} ({{ service.price }} руб.)
              </option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="submit" class="save-btn">Создать запись</button>
            <button type="button" class="cancel-btn" @click="isCreateModalVisible = false">Отмена</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно для ДЕТАЛЕЙ ЗАКАЗА -->
    <div v-if="isDetailsModalVisible && selectedOrder" class="modal-overlay" @click.self="isDetailsModalVisible = false">
      <div class="modal-content large-modal">
        <h2>Детали Записи</h2>
        <p><strong>Клиент:</strong> {{ selectedOrder.clientName }}</p>
        <p><strong>Автомобиль:</strong> {{ selectedOrder.carInfo }}</p>
        <strong>Услуги:</strong>
        <ul>
          <!-- <<< ИСПРАВЛЕНИЕ №4: ИСПОЛЬЗУЕМ 'service.id' ВМЕСТО 'service._id' >>> -->
          <li v-for="service in selectedOrder.serviceDetails" :key="service.id">
            {{ service.name }} - {{ service.price }} руб.
          </li>
        </ul>
        <p><strong>Итого:</strong> {{ selectedOrder.total_price }} руб.</p>
        <div class="form-group">
          <label for="employee"><strong>Исполнитель</strong></label>
          <select id="employee" v-model="selectedOrder.employee_id">
            <option :value="null">Не назначен</option>
            <option v-for="employee in employees" :key="employee._id" :value="employee._id">
              {{ employee.full_name }} ({{ employee.role }})
            </option>
          </select>
        </div>
        <div class="form-group">
          <label for="status"><strong>Статус заказа</strong></label>
          <select id="status" v-model="selectedOrder.status">
            <option v-for="status in availableStatuses" :key="status" :value="status">
              {{ status }}
            </option>
          </select>
        </div>
        <div class="modal-actions">
          <button @click="deleteOrder" class="delete-btn">Удалить заказ</button>
          <button @click="updateOrder" class="save-btn">Сохранить</button>
        </div>

        <hr class="modal-divider">
        
        <div class="materials-section">
          <h3>Расходные материалы</h3>
          <h4>Списать материал на заказ</h4>
          <form @submit.prevent="useMaterialOnOrder" class="material-usage-form">
            <select v-model="materialToUse.itemId" required>
              <option :value="null" disabled>Выберите материал</option>
              <option v-for="item in inventoryItems" :key="item._id" :value="item._id">
                {{ item.name }} (Остаток: {{ item.quantity }} {{ item.unit }})
              </option>
            </select>
            <input type="number" v-model.number="materialToUse.quantity" placeholder="Кол-во" required min="0.01" step="any">
            <button type="submit" class="btn-withdraw">Списать</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ------------------------------------ */
/* --- 1. Общая структура Layout --- */
/* ------------------------------------ */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #ddd;
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
}
.create-order-btn-header {
  background-color: #28a745;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
}
.create-order-btn-header:hover { background-color: #218838; }
.calendar-layout { display: flex; gap: 30px; align-items: flex-start; }
.calendar-month-container { width: 380px; flex-shrink: 0; position: sticky; top: 20px; }
.timeline-container { flex-grow: 1; background-color: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; }
.timeline-container h2 { margin-top: 0; margin-bottom: 20px; }
.no-orders-message { padding: 50px 20px; text-align: center; color: #718096; background-color: #f7fafc; border-radius: 8px; border: 1px dashed #e2e8f0; }

/* ------------------------------------ */
/* --- 2. V-Calendar Адаптация --- */
/* ------------------------------------ */
:root { --vc-accent-color: #3b82f6; }
:deep(.vc-light) {
    --vc-bg: #ffffff; --vc-border: #e2e8f0; --vc-header-arrow-color: #6b7280; --vc-weekday-color: #4a5568; --vc-day-color: #333333; --vc-day-content-hover-bg: #f1f5f9; --vc-nav-item-active-color: var(--vc-accent-color);
}
:deep(.vc-container) { --day-width: 48px; --day-height: 48px; border-radius: 8px; width: 100%; }
:deep(.vc-day) { min-height: var(--day-height); }
:deep(.vc-day-content:hover) { background-color: var(--vc-day-content-hover-bg) !important; }
:deep(.is-today .vc-day-content) { background-color: #fef3c7; }
:deep(.is-selected .vc-day-content) { background-color: var(--vc-accent-color) !important; color: white; }
:deep(.vc-dots) { justify-content: center; }

/* ------------------------------------ */
/* --- 3. Daily Timeline Стилизация --- */
/* ------------------------------------ */
.timeline-grid-wrapper { overflow-y: auto; max-height: 70vh; }
.timeline-grid { display: grid; grid-template-columns: 60px 1fr; grid-template-rows: repeat(23, 30px); position: relative; }
.time-slot { grid-column: 1; text-align: right; padding-right: 10px; font-size: 12px; color: #a0aec0; position: relative; transform: translateY(-50%); }
.time-slot:nth-child(2n+1) { color: #4a5568; border-top: 1px solid #e2e8f0; }
.time-slot:nth-child(2n) { border-top: 1px dotted #e2e8f0; }
.order-card {
  grid-column: 2; border-left: 4px solid; border-radius: 4px; padding: 8px 12px; margin: 1px 5px 1px 0px; font-size: 13px; overflow: hidden; color: #1a202c; cursor: pointer; z-index: 10; transition: all 0.2s ease; display: flex; flex-direction: column; justify-content: center;
}
.order-card:hover { transform: scale(1.01); box-shadow: 0 4px 8px rgba(0,0,0,0.1); z-index: 11; }
.order-card strong { font-weight: 600; }
.order-price { font-size: 0.8rem; color: #4a5568; font-weight: 500; }
.order-time { font-size: 0.75rem; color: #718096; }
.employee-info { font-size: 0.8rem; color: #4a5568; margin-top: 4px; font-weight: 500; }

/* ------------------------------------ */
/* --- 4. Стили для модальных окон --- */
/* ------------------------------------ */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.6); display: flex; justify-content: center; align-items: center; z-index: 1000;
}
.modal-content {
  background-color: white; padding: 2rem; border-radius: 8px; width: 90%; max-width: 500px; max-height: 90vh; overflow-y: auto;
}
.large-modal { max-width: 700px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1.5rem; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
.form-group input, .form-group select { width: 100%; padding: 0.5rem; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
.form-group select[multiple] { height: 120px; }
.form-group small { color: #666; font-size: 0.8rem; margin-top: 4px; }

/* --- 5. Стили для кнопок --- */
button { padding: 0.7rem 1.2rem; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
.save-btn { background-color: #28a745; color: white; }
.delete-btn { background-color: #dc3545; color: white; }
.cancel-btn { background-color: #6c757d; color: white; }

/* ------------------------------------ */
/* --- 6. Стили для склада --- */
/* ------------------------------------ */
.modal-divider { margin: 2rem 0; border: 0; border-top: 1px solid #eee; }
.materials-section h3, .materials-section h4 { margin-bottom: 1rem; }
.material-usage-form { display: flex; gap: 10px; align-items: center; }
.material-usage-form select { flex-grow: 1; }
.material-usage-form input { width: 120px; }
.btn-withdraw { background-color: #f97316; color: white; padding: 0.5rem 1rem; }
</style>