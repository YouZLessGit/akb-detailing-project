<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// --- ДЛЯ КЛИЕНТОВ ---
const clients = ref([])
const newClient = ref({ full_name: '', phone_number: '', email: '' })
const isLoadingClients = ref(true)

// --- ДЛЯ АВТОМОБИЛЕЙ ---
const carMakes = ref([])
const selectedClient = ref(null)
const clientCars = ref([])
const newCar = ref({ make: '', model: '', license_plate: '' })
const isLoadingCars = ref(true)

// --- ДЛЯ РЕДАКТИРОВАНИЯ ---
const isEditModalVisible = ref(false)
const editingCar = ref(null)

// --- Функции для КЛИЕНТОВ ---
const fetchClients = async () => {
  try {
    isLoadingClients.value = true
    const response = await axios.get('http://localhost:8000/api/clients/')
    clients.value = response.data
  } catch (error) {
    alert("Не удалось загрузить список клиентов.")
  } finally {
    isLoadingClients.value = false
  }
}

const addClient = async () => {
  if (!newClient.value.full_name || !newClient.value.phone_number) {
    alert('ФИО и номер телефона обязательны!')
    return
  }
  try {
    await axios.post('http://localhost:8000/api/clients/create/', newClient.value)
    newClient.value = { full_name: '', phone_number: '', email: '' }
    await fetchClients()
  } catch (error) {
    alert("Произошла ошибка при добавлении клиента.")
  }
}

// --- Функции для АВТОМОБИЛЕЙ ---
const fetchCarMakes = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/car-makes/')
    carMakes.value = response.data.map(make => make.name)
  } catch (error) {
    alert("Не удалось загрузить список марок авто.")
  }
}

const fetchClientCars = async (clientId) => {
  try {
    isLoadingCars.value = true
    const response = await axios.get(`http://localhost:8000/api/cars/client/${clientId}/`)
    clientCars.value = response.data
  } catch (error) {
    alert(`Не удалось загрузить автомобили для выбранного клиента.`)
  } finally {
    isLoadingCars.value = false
  }
}

const addCarToClient = async () => {
  if (!selectedClient.value?._id) return alert("Сначала выберите клиента.")
  if (!newCar.value.make || !newCar.value.model || !newCar.value.license_plate) return alert('Все поля автомобиля обязательны!')

  try {
    const carData = { ...newCar.value, client_id: selectedClient.value._id }
    await axios.post('http://localhost:8000/api/cars/create/', carData)
    newCar.value = { make: '', model: '', license_plate: '' }
    await fetchClientCars(selectedClient.value._id)
  } catch (error) {
    alert("Произошла ошибка при добавлении автомобиля.")
  }
}

// --- Функции для Редактирования/Удаления ---
const openEditModal = (car) => {
  editingCar.value = { ...car }
  isEditModalVisible.value = true
}

const saveCarChanges = async () => {
  if (!editingCar.value) return;
  try {
    await axios.put(`http://localhost:8000/api/cars/update/${editingCar.value._id}/`, editingCar.value)
    isEditModalVisible.value = false
    await fetchClientCars(selectedClient.value._id)
  } catch (error) {
    alert("Ошибка при сохранении изменений.")
  }
}

const deleteCar = async (carId) => {
  if (!confirm('Вы уверены, что хотите удалить этот автомобиль?')) return
  try {
    await axios.delete(`http://localhost:8000/api/cars/delete/${carId}/`)
    await fetchClientCars(selectedClient.value._id)
  } catch (error) {
    alert("Ошибка при удалении автомобиля.")
  }
}

// --- Управление ---
const selectClient = (client) => {
  selectedClient.value = client
  fetchClientCars(client._id)
}

onMounted(() => {
  fetchClients()
  fetchCarMakes()
})
</script>

<template>
  <div class="clients-view">
    <h1>Управление клиентами и автомобилями</h1>
    
    <div class="form-container">
      <h2>Добавить нового клиента</h2>
      <form @submit.prevent="addClient">
        <div class="form-group">
          <label for="fullName">ФИО клиента</label>
          <input type="text" id="fullName" v-model="newClient.full_name" required>
        </div>
        <div class="form-group">
          <label for="phone">Номер телефона</label>
          <input type="tel" id="phone" v-model="newClient.phone_number" required>
        </div>
        <div class="form-group">
          <label for="email">Email (необязательно)</label>
          <input type="email" id="email" v-model="newClient.email">
        </div>
        <button type="submit">Добавить клиента</button>
      </form>
    </div>

    <hr>

    <h2>Список клиентов</h2>
    <div v-if="isLoadingClients">Загрузка клиентов...</div>
    <ul v-else class="clients-list">
      <li v-for="client in clients" :key="client._id" :class="{ 'selected': client._id === selectedClient?._id }" @click="selectClient(client)">
        <div class="client-info">
          <strong>{{ client.full_name }}</strong> <br>
          <small>{{ client.phone_number }} <span v-if="client.email">- {{ client.email }}</span></small>
        </div>
      </li>
    </ul>

    <hr>

    <div v-if="selectedClient" class="car-management-section">
      <h2>Автомобили клиента: {{ selectedClient.full_name }}</h2>
      
      <div class="form-container">
        <h3>Добавить новый автомобиль</h3>
        <form @submit.prevent="addCarToClient">
          <div class="form-group">
            <label for="carMake">Марка</label>
            <select id="carMake" v-model="newCar.make" required>
              <option value="" disabled>Выберите марку</option>
              <option v-for="make in carMakes" :key="make" :value="make">{{ make }}</option>
            </select>
          </div>
          <div class="form-group">
            <label for="carModel">Модель</label>
            <input type="text" id="carModel" v-model="newCar.model" required>
          </div>
          <div class="form-group">
            <label for="licensePlate">Гос. номер</label>
            <input type="text" id="licensePlate" v-model="newCar.license_plate" required>
          </div>
          <button type="submit">Добавить автомобиль</button>
        </form>
      </div>

      <h3>Список автомобилей</h3>
      <div v-if="isLoadingCars">Загрузка автомобилей...</div>
      <ul v-else-if="clientCars.length > 0" class="cars-list">
        <li v-for="car in clientCars" :key="car._id">
          <span>{{ car.make }} {{ car.model }} ({{ car.license_plate }})</span>
          <div class="car-actions">
            <button class="edit-btn" @click="openEditModal(car)">Редактировать</button>
            <button class="delete-btn" @click="deleteCar(car._id)">Удалить</button>
          </div>
        </li>
      </ul>
      <p v-else>У этого клиента пока нет зарегистрированных автомобилей.</p>
    </div>
    <p v-else class="hint-text">Выберите клиента из списка выше, чтобы управлять его автомобилями.</p>

    <div v-if="isEditModalVisible" class="modal-overlay" @click.self="isEditModalVisible = false">
      <div class="modal-content">
        <h2>Редактировать автомобиль</h2>
        <form @submit.prevent="saveCarChanges">
          <div class="form-group">
            <label>Марка</label>
            <select v-model="editingCar.make" required>
              <option v-for="make in carMakes" :key="make" :value="make">{{ make }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Модель</label>
            <input type="text" v-model="editingCar.model" required>
          </div>
          <div class="form-group">
            <label>Гос. номер</label>
            <input type="text" v-model="editingCar.license_plate" required>
          </div>
          <div class="modal-actions">
            <button type="submit" class="save-btn">Сохранить</button>
            <button type="button" class="cancel-btn" @click="isEditModalVisible = false">Отмена</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.clients-view { max-width: 900px; margin: 0 auto; padding: 1.5rem; }
h1, h2 { color: #333; margin-bottom: 1.5rem; border-bottom: 1px solid #eee; padding-bottom: 0.5rem; }
h3 { margin-top: 1.5rem; margin-bottom: 1rem; color: #555; }
.form-container { background-color: #fff; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: bold; color: #555; }
.form-group input, .form-group select { width: 100%; padding: 0.75rem; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
button[type="submit"] { background-color: #007bff; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
button[type="submit"]:hover { background-color: #0056b3; }
hr { margin: 3rem 0; border: 0; border-top: 1px solid #eee; }
.loading, .hint-text { text-align: center; color: #777; font-style: italic; padding: 1rem 0; }
.clients-list, .cars-list { list-style: none; padding: 0; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.clients-list li, .cars-list li { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.5rem; border-bottom: 1px solid #eee; transition: background-color 0.2s ease; }
.clients-list li { cursor: pointer; }
.clients-list li:last-child, .cars-list li:last-child { border-bottom: none; }
.clients-list li:hover { background-color: #e9f0f7; }
.clients-list li.selected { background-color: #d1e2f3; font-weight: bold; }
.client-info { flex-grow: 1; }
.client-info small { color: #666; }
.car-management-section { margin-top: 2rem; background-color: #f0f8ff; padding: 2rem; border-radius: 8px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1); }
.car-actions button { color: white; padding: 0.4rem 0.8rem; font-size: 0.9rem; margin-left: 0.5rem; border: none; border-radius: 4px; cursor: pointer; }
.edit-btn { background-color: #ffc107; color: #333; }
.delete-btn { background-color: #dc3545; }
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background-color: white; padding: 2rem; border-radius: 8px; width: 90%; max-width: 500px; }
.modal-actions { display: flex; justify-content: flex-end; margin-top: 1.5rem; }
.save-btn { background-color: #28a745; }
.cancel-btn { background-color: #6c757d; margin-left: 0.5rem; }
</style>