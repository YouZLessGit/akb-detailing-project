<template>
  <div class="booking-container">
    <!-- ======================= ЭТАП 1: ВЫБОР УСЛУГИ ======================= -->
    <div v-if="!bookingSuccessMessage" class="step-container">
      <h1 class="step-title">Шаг 1: Выберите услугу</h1>
      <div v-if="isLoading" class="loader">Загрузка услуг...</div>
      <div v-if="error" class="error-message">{{ error }}</div>
      <div class="services-grid" v-if="!isLoading && services.length > 0">
        <div 
          v-for="service in services" 
          :key="service.id"
          class="service-card"
          @click="selectService(service)"
          :class="{ 'selected': selectedService && selectedService.id === service.id }"
        >
          <h3>{{ service.name }}</h3>
          <p>{{ service.description }}</p>
          <div class="service-footer">
            <span class="price">{{ service.price }} BYN</span>
            <span class="duration">{{ service.duration }} мин.</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ======================= ЭТАП 2: ВЫБОР ДАТЫ И ВРЕМЕНИ ======================= -->
    <div v-if="selectedService && !bookingSuccessMessage" class="step-container">
      <h1 class="step-title">Шаг 2: Выберите дату и время</h1>
      <div class="date-time-picker">
        <div class="calendar-wrapper">
          <VDatePicker 
            v-model="selectedDate"
            :min-date="new Date()"
            color="blue"
            is-dark
            title-position="left"
          />
        </div>
        <div class="slots-wrapper">
          <h3 v-if="selectedDate">Доступное время на {{ formattedDate }}</h3>
          <h3 v-else>Выберите дату в календаре</h3>
          
          <div v-if="isLoadingSlots" class="loader">Поиск слотов...</div>
          <div v-if="slotsError" class="error-message">{{ slotsError }}</div>
          
          <div v-if="!isLoadingSlots && availableSlots.length > 0" class="slots-grid">
            <button 
              v-for="slot in availableSlots" 
              :key="slot" 
              class="slot-button"
              :class="{ 'selected': selectedSlot === slot }"
              @click="selectSlot(slot)"
            >
              {{ slot }}
            </button>
          </div>

          <div v-if="selectedDate && !isLoadingSlots && availableSlots.length === 0 && !slotsError" class="no-slots">
            На выбранную дату свободных мест нет. Пожалуйста, выберите другой день.
          </div>
        </div>
      </div>
    </div>

    <!-- ======================= ЭТАП 3: ВВОД ДАННЫХ ИЛИ СООБЩЕНИЕ ОБ УСПЕХЕ ======================= -->
    <div v-if="selectedSlot" class="step-container">
      <!-- Блок с формой (показывается, пока нет сообщения об успехе) -->
      <div v-if="!bookingSuccessMessage">
        <h1 class="step-title">Шаг 3: Ваши данные</h1>
        <form @submit.prevent="submitBooking" class="booking-form">
          <div class="form-group">
            <label for="name">Ваше имя</label>
            <input type="text" id="name" v-model="clientDetails.name" required placeholder="Иван Иванов">
          </div>
          <div class="form-group">
            <label for="phone">Номер телефона</label>
            <input type="tel" id="phone" v-model="clientDetails.phone" required placeholder="+375 (29) 123-45-67">
          </div>
          <div class="form-group">
            <label for="car-make">Марка автомобиля</label>
            <input type="text" id="car-make" v-model="clientDetails.car.make" required placeholder="BMW">
          </div>
          <div class="form-group">
            <label for="car-model">Модель автомобиля</label>
            <input type="text" id="car-model" v-model="clientDetails.car.model" required placeholder="X5">
          </div>
          <button type="submit" class="submit-button" :disabled="isSubmitting">
            {{ isSubmitting ? 'Отправка...' : 'Записаться' }}
          </button>
        </form>
        <div v-if="bookingError" class="error-message" style="margin-top: 20px;">{{ bookingError }}</div>
      </div>

      <!-- Блок УСПЕХА (показывается, когда есть сообщение об успехе) -->
      <div v-else class="success-state">
        <svg class="success-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
          <circle class="success-icon__circle" cx="26" cy="26" r="25" fill="none"/>
          <path class="success-icon__check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
        </svg>
        <h2 class="success-title">Отлично!</h2>
        <p class="success-text">{{ bookingSuccessMessage }}</p>
        <button @click="resetFlow" class="submit-button">Записаться еще раз</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import axios from 'axios';
import { DatePicker as VDatePicker } from 'v-calendar';
import 'v-calendar/style.css';


// --- Состояния для Шага 1 ---
const services = ref([]);
const isLoading = ref(true);
const error = ref(null);
const selectedService = ref(null);

// --- Состояния для Шага 2 ---
const selectedDate = ref(null);
const availableSlots = ref([]);
const isLoadingSlots = ref(false);
const slotsError = ref(null);
const selectedSlot = ref(null);

// --- Состояния для Шага 3 ---
const clientDetails = ref({
  name: '',
  phone: '',
  car: {
    make: '',
    model: ''
  }
});
const isSubmitting = ref(false);
const bookingError = ref(null);
const bookingSuccessMessage = ref(null);

const API_BASE_URL = 'http://127.0.0.1:8000/api';

// --- Логика для Шага 1 ---
const fetchServices = async () => {
  try {
    // <<< ИСПРАВЛЕНИЕ: ИСПОЛЬЗУЕМ НОВЫЙ URL >>>
    const response = await axios.get(`${API_BASE_URL}/public/services-list/`);
    services.value = response.data;
  } catch (err) {
    error.value = "Не удалось загрузить список услуг.";
  } finally {
    isLoading.value = false;
  }
};

const selectService = (service) => {
  selectedService.value = service;
  // Сбрасываем последующие шаги при смене услуги
  selectedDate.value = null;
  selectedSlot.value = null;
  availableSlots.value = [];
};

// --- Логика для Шага 2 ---
const fetchAvailableSlots = async (date) => {
  if (!date || !selectedService.value) return;

  isLoadingSlots.value = true;
  slotsError.value = null;
  availableSlots.value = [];
  selectedSlot.value = null;

  const dateString = date.toISOString().split('T')[0]; // Формат YYYY-MM-DD
  const duration = selectedService.value.duration;

  try {
    const response = await axios.get(`${API_BASE_URL}/public/available-slots/`, {
      params: { date: dateString, duration }
    });
    availableSlots.value = response.data;
  } catch (err) {
    slotsError.value = "Не удалось загрузить доступное время. Попробуйте выбрать другую дату.";
  } finally {
    isLoadingSlots.value = false;
  }
};

// "Наблюдатель": автоматически вызывает fetchAvailableSlots, когда меняется selectedDate
watch(selectedDate, (newDate) => {
  fetchAvailableSlots(newDate);
});

const formattedDate = computed(() => {
  return selectedDate.value ? new Date(selectedDate.value).toLocaleDateString('ru-RU') : '';
});

const selectSlot = (slot) => {
  selectedSlot.value = slot;
};

// --- Логика для Шага 3 ---
const submitBooking = async () => {
  isSubmitting.value = true;
  bookingError.value = null;

  // <<< НАЧАЛО ИСПРАВЛЕНИЯ >>>

  // Было (НЕПРАВИЛЬНО):
  // const datePart = selectedDate.value.toISOString().split('T')[0];
  
  // Стало (ПРАВИЛЬНО):
  // Мы вручную собираем строку YYYY-MM-DD из локальной даты, чтобы избежать конвертации в UTC.
  const date = selectedDate.value;
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0'); // getMonth() 0-индексный, добавляем 1
  const day = String(date.getDate()).padStart(2, '0');
  const datePart = `${year}-${month}-${day}`;

  // Эта строка теперь использует правильную дату.
  // Она создает новый объект Date, который JS по-прежнему считает локальным,
  // и .toISOString() теперь корректно переведет его в UTC для сервера.
  const startTimeISO = new Date(`${datePart}T${selectedSlot.value}`).toISOString();

  const bookingData = {
    client: {
      name: clientDetails.value.name,
      phone: clientDetails.value.phone
    },
    car: {
      make: clientDetails.value.car.make,
      model: clientDetails.value.car.model
    },
    service_id: selectedService.value.id,
    start_time: startTimeISO
  };

  try {
    const response = await axios.post(`${API_BASE_URL}/public/booking/`, bookingData);
    // Просто устанавливаем сообщение об успехе. Сброс состояния произойдет по кнопке.
    bookingSuccessMessage.value = response.data.message;
  } catch (err) {
    bookingError.value = err.response?.data?.error || "Произошла неизвестная ошибка при записи.";
  } finally {
    isSubmitting.value = false;
  }
};

// --- Функция для сброса всего процесса ---
const resetFlow = () => {
  selectedService.value = null;
  selectedDate.value = null;
  selectedSlot.value = null;
  availableSlots.value = [];
  clientDetails.value = { name: '', phone: '', car: { make: '', model: '' } };
  bookingSuccessMessage.value = null; // <-- Скрываем блок успеха и возвращаем к Шагу 1
  bookingError.value = null;
};

onMounted(fetchServices);
</script>

<style scoped>
/* Общие стили */
.booking-container {
  max-width: 1000px;
  margin: 40px auto;
  padding: 0 20px;
  color: #f0f0f0;
}
.step-container {
  background-color: #242424;
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 40px;
  border: 1px solid #333;
}
.step-title {
  text-align: center;
  font-size: 2.2rem;
  margin-top: 0;
  margin-bottom: 30px;
}
.loader, .error-message {
  text-align: center;
  padding: 20px;
  font-size: 1.1rem;
  border-radius: 8px;
}
.error-message {
  color: #ff4d4d;
  background-color: rgba(255, 77, 77, 0.1);
}

/* Стили для Шага 1 */
.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}
.service-card {
  background-color: #2a2a2a;
  border: 1px solid #444;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  display: flex;
  flex-direction: column;
}
.service-card:hover {
  transform: translateY(-5px);
  border-color: #007BFF;
}
.service-card.selected {
  border-color: #007BFF;
  box-shadow: 0 0 15px rgba(0, 123, 255, 0.5);
}
.service-card h3 {
  margin-top: 0;
  color: #fff;
}
.service-card p {
  color: #ccc;
  font-size: 0.9rem;
  flex-grow: 1;
}
.service-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  font-weight: bold;
}
.price {
  color: #007BFF;
  font-size: 1.2rem;
}
.duration {
  color: #aaa;
}

/* Стили для Шага 2 */
.date-time-picker {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}
.calendar-wrapper {
  display: flex;
  justify-content: center;
}
.slots-wrapper h3 {
  text-align: center;
  margin-top: 0;
  color: #ccc;
}
.no-slots {
  text-align: center;
  color: #aaa;
  padding: 20px;
  background-color: #2a2a2a;
  border-radius: 8px;
}
.slots-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}
.slot-button {
  background-color: #333;
  color: #fff;
  border: 1px solid #555;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1rem;
  text-align: center;
}
.slot-button:hover {
  background-color: #007BFF;
  border-color: #007BFF;
}
.slot-button.selected {
  background-color: #007BFF;
  border-color: #007BFF;
  color: #fff;
  transform: scale(1.05);
}
:deep(.vc-container) {
  background-color: #2a2a2a;
  border: 1px solid #444;
}

/* Стили для Шага 3 (Форма) */
.booking-form {
  max-width: 500px;
  margin: 0 auto;
}
.form-group {
  margin-bottom: 20px;
}
.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #ccc;
}
.form-group input {
  width: 100%;
  padding: 12px;
  background-color: #333;
  border: 1px solid #555;
  border-radius: 6px;
  color: #fff;
  font-size: 1rem;
  box-sizing: border-box;
}
.form-group input:focus {
  border-color: #007BFF;
  outline: none;
}
.submit-button {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  display: block;
  background-color: #007BFF;
  color: #fff;
  padding: 15px;
  border-radius: 5px;
  text-decoration: none;
  font-size: 1.2rem;
  font-weight: bold;
  transition: background-color 0.3s;
  border: none;
  cursor: pointer;
}
.submit-button:hover:not(:disabled) {
  background-color: #0056b3;
}
.submit-button:disabled {
  background-color: #555;
  cursor: not-allowed;
}

/* Стили для блока успеха */
.success-state {
  text-align: center;
  padding: 20px;
}
.success-title {
  font-size: 2rem;
  color: #fff;
  margin: 20px 0 10px;
}
.success-text {
  color: #ccc;
  font-size: 1.1rem;
  margin-bottom: 30px;
  max-width: 450px;
  margin-left: auto;
  margin-right: auto;
}
.success-icon {
  width: 80px;
  height: 80px;
  display: block;
  margin: 0 auto;
}
.success-icon__circle {
  stroke-dasharray: 166;
  stroke-dashoffset: 166;
  stroke-width: 2;
  stroke-miterlimit: 10;
  stroke: #4bb71b;
  fill: none;
  animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
}
.success-icon__check {
  transform-origin: 50% 50%;
  stroke-dasharray: 48;
  stroke-dashoffset: 48;
  stroke-width: 2;
  stroke: #4bb71b;
  fill: none;
  animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
}
@keyframes stroke {
  100% {
    stroke-dashoffset: 0;
  }
}

/* Адаптивность */
@media (max-width: 768px) {
  .date-time-picker {
    grid-template-columns: 1fr;
  }
  .slots-wrapper {
    margin-top: 20px;
  }
}
</style>