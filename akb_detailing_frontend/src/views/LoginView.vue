  <script setup>
  import { ref } from 'vue';
  import axios from 'axios';
  import { useRouter } from 'vue-router';

  const credentials = ref({
    username: '',
    password: ''
  });
  const router = useRouter();
  const error = ref('');

  // --- ИЗМЕНЕНИЕ №1: Добавляем состояние загрузки ---
  const isLoading = ref(false);

  const login = async () => {
    // --- ИЗМЕНЕНИЕ №2: Включаем загрузку и сбрасываем старые ошибки ---
    isLoading.value = true;
    error.value = '';

    if (!credentials.value.username || !credentials.value.password) {
      error.value = 'Пожалуйста, введите логин и пароль.';
      isLoading.value = false; // Отключаем загрузку, если поля пустые
      return;
    }

    try {
      const response = await axios.post('http://localhost:8000/api/auth/login/', credentials.value);
      
      sessionStorage.setItem('user-token', response.data.token);
      sessionStorage.setItem('user-data', JSON.stringify(response.data.user)); 
      
      await router.push('/admin/dashboard');
    } catch (err) {
      error.value = 'Неверный логин или пароль.';
      console.error(err);
    } finally {
      // --- ИЗМЕНЕНИЕ №3: Выключаем загрузку в любом случае (успех или ошибка) ---
      isLoading.value = false;
    }
  };
  </script>

  <template>
    <div class="login-container">
      <div class="login-form">
        <h1>Вход в CRM</h1>
        <form @submit.prevent="login">
          <div class="form-group">
            <label for="username">Логин</label>
            <input type="text" id="username" v-model="credentials.username" required>
          </div>
          <div class="form-group">
            <label for="password">Пароль</label>
            <input type="password" id="password" v-model="credentials.password" required>
          </div>
          <!-- --- ИЗМЕНЕНИЕ №4: Привязываем состояние загрузки к кнопке --- -->
          <button type="submit" :disabled="isLoading">
            {{ isLoading ? 'Вход...' : 'Войти' }}
          </button>
          <p v-if="error" class="error-message">{{ error }}</p>
        </form>
      </div>
    </div>
  </template>

  <style scoped>
  /* Ваши стили остаются без изменений */
  .login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f4f6f9;
  }
  .login-form {
    padding: 2rem;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
  }
  h1 { text-align: center; margin-bottom: 1.5rem; }
  .form-group { margin-bottom: 1rem; }
  label { display: block; margin-bottom: 0.5rem; }
  input { width: 100%; padding: 0.75rem; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
  button { 
    width: 100%; 
    padding: 0.75rem; 
    background-color: #007bff; 
    color: white; 
    border: none; 
    border-radius: 4px; 
    cursor: pointer; 
    font-size: 1rem;
    transition: background-color 0.2s; /* Добавим плавности */
  }
  /* --- ИЗМЕНЕНИЕ №5: Стиль для неактивной кнопки --- */
  button:disabled {
    background-color: #6c757d;
    cursor: not-allowed;
  }
  .error-message { color: #dc3545; text-align: center; margin-top: 1rem; }
  </style>