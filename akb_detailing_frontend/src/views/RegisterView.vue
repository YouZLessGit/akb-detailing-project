<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter() // Для перенаправления после успеха

const form = ref({
  username: '',
  password: ''
})
const message = ref('') // Для сообщений пользователю

const handleRegister = async () => {
  if (!form.value.username || !form.value.password) {
    message.value = 'Пожалуйста, заполните все поля.'
    return
  }

  try {
    // Отправляем данные на наш новый эндпоинт регистрации
    const response = await axios.post('http://localhost:8000/api/auth/register/', form.value)
    
    console.log(response.data)
    message.value = 'Регистрация прошла успешно! Теперь вы можете войти.'
    
    // Опционально: перенаправляем на страницу входа через 2 секунды
    setTimeout(() => {
      router.push('/login')
    }, 2000)

  } catch (error) {
    console.error('Ошибка регистрации:', error)
    if (error.response && error.response.data.error) {
      message.value = `Ошибка: ${error.response.data.error}`
    } else {
      message.value = 'Произошла ошибка при регистрации.'
    }
  }
}
</script>

<template>
  <div class="auth-form-container">
    <h2>Регистрация нового сотрудника</h2>
    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <label for="username">Имя пользователя (логин)</label>
        <input type="text" id="username" v-model="form.username" required>
      </div>
      <div class="form-group">
        <label for="password">Пароль</label>
        <input type="password" id="password" v-model="form.password" required>
      </div>
      <button type="submit">Зарегистрироваться</button>
    </form>
    <p v-if="message" class="message">{{ message }}</p>
  </div>
</template>

<style scoped>
.auth-form-container {
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: #f9f9f9;
  border-radius: 8px;
  text-align: center;
}
.form-group {
  margin-bottom: 1rem;
  text-align: left;
}
label {
  display: block;
  margin-bottom: 0.5rem;
}
input {
  width: 100%;
  padding: 0.5rem;
}
button {
  width: 100%;
  padding: 0.75rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.message {
  margin-top: 1rem;
  color: green;
}
</style>