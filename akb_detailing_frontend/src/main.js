import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// 1. Импортируем VCalendar и его CSS
import VCalendar from 'v-calendar'
import 'v-calendar/style.css'
import 'v-calendar/dist/style.css';

// Создаем экземпляр приложения
const app = createApp(App)

// "Регистрируем" плагины. Порядок важен!
app.use(router)
app.use(VCalendar, {}) // Это говорит Vue: "Теперь ты знаешь, что такое v-calendar и другие компоненты этой библиотеки"

// .mount('#app') ДОЛЖЕН БЫТЬ ПОСЛЕДНИМ
app.mount('#app')