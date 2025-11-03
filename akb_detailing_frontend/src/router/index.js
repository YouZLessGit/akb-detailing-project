// router/index.js

import { createRouter, createWebHistory } from 'vue-router'

// Импортируем макеты
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'

// Импортируем публичные страницы
import HomeView from '../views/HomeView.vue'
import ServicesView from '../views/ServicesView.vue'
import CategoryDetailView from '../views/CategoryDetailView.vue'
import ServiceDetailView from '../views/ServiceDetailView.vue'
import BookingView from '../views/BookingView.vue'
import LoginView from '../views/LoginView.vue'
import PortfolioView from '../views/PortfolioView.vue'
import PortfolioDetailView from '../views/PortfolioDetailView.vue'
import AboutView from '../views/AboutView.vue'

// Импортируем страницы админки
import DashboardView from '../views/admin/DashboardView.vue'
import ServicesManagementView from '../views/admin/ServicesManagementView.vue'
import ClientsView from '../views/admin/ClientsView.vue'
import CalendarView from '../views/admin/CalendarView.vue'
import EmployeesView from '../views/admin/EmployeesView.vue'
import InventoryView from '../views/admin/InventoryView.vue'
import ReportsView from '../views/admin/ReportsView.vue'
import PortfolioManagementView from '../views/admin/PortfolioManagementView.vue'
import AboutManagementView from '../views/admin/AboutManagementView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: DefaultLayout,
      children: [
        { path: '', name: 'home', component: HomeView },
        { path: 'services', name: 'services', component: ServicesView },
        { path: 'services/category/:slug', name: 'category-detail', component: CategoryDetailView },
        { path: 'service/:slug', name: 'service-detail', component: ServiceDetailView },
        { path: 'portfolio', name: 'portfolio', component: PortfolioView },
        { path: 'portfolio/:slug', name: 'portfolio-detail', component: PortfolioDetailView },
        { path: 'booking', name: 'booking', component: BookingView },
        { path: 'about', name: 'about', component: AboutView },
        // --- НОВЫЕ МАРШРУТЫ ДЛЯ БЛОГА ---
        { path: 'blog', name: 'blog', component: () => import('../views/BlogListView.vue') },
        { path: 'blog/:slug', name: 'blog-detail', component: () => import('../views/BlogPostDetailView.vue') },
      ]
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/admin/dashboard' },
        { path: 'dashboard', name: 'admin-dashboard', component: DashboardView },
        { path: 'services', name: 'admin-services', component: ServicesManagementView },
        { path: 'clients', name: 'admin-clients', component: ClientsView },
        { path: 'calendar', name: 'admin-calendar', component: CalendarView },
        { path: 'employees', name: 'admin-employees', component: EmployeesView },
        { path: 'inventory', name: 'admin-inventory', component: InventoryView },
        { path: 'portfolio', name: 'admin-portfolio', component: PortfolioManagementView },
        // --- НОВЫЙ МАРШРУТ ДЛЯ АДМИНКИ БЛОГА ---
        { path: 'blog', name: 'admin-blog', component: () => import('../views/admin/BlogManagementView.vue') },
        { path: 'about', name: 'admin-about', component: AboutManagementView },
        { path: 'reports', name: 'admin-reports', component: ReportsView },
      ]
    },
  ]
})

// Навигационный охранник (без изменений)
router.beforeEach((to, from, next) => {
  const isLoggedIn = !!sessionStorage.getItem('user-token');
  
  if (to.matched.some(record => record.meta.requiresAuth) && !isLoggedIn) {
    next({ name: 'login' });
  } 
  else if (to.name === 'login' && isLoggedIn) {
    next({ name: 'admin-dashboard' });
  } 
  else {
    next();
  }
})

export default router