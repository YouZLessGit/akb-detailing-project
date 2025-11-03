# akb_detailing_project/api/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # --- Услуги и Категории (АДМИНКА) ---
    path('services/admin-list/', views.get_admin_services, name='get_admin_services'),
    # Вот маршрут, который нужен календарю. Убедитесь, что он здесь есть.
    path('services/list/', views.public_get_services_list, name='get_services_list_admin'),
    path('services/create/', views.create_service, name='create_service'),
    path('services/update/<str:service_id>/', views.update_service, name='update_service'),
    path('services/delete/<str:service_id>/', views.delete_service, name='delete_service'),
    path('services/categories/', views.get_service_categories, name='get_service_categories'),
    path('services/categories/create/', views.create_service_category, name='create_service_category'),
    path('services/categories/update/<str:category_id>/', views.update_service_category, name='update_service_category'),
    path('services/categories/delete/<str:category_id>/', views.delete_service_category, name='delete_service_category'),

    # --- Услуги и Категории (ПУБЛИЧНЫЙ САЙТ) ---
    path('public/services/', views.public_get_top_level_categories, name='public_get_top_level_categories'),
    path('public/service-category/<slug:slug>/', views.public_get_category_page, name='public_get_category_page'),
    path('public/service-detail/<slug:slug>/', views.public_get_service_details, name='public_get_service_details'),
    # А вот маршрут, который нужен для онлайн-записи.
    path('public/services-list/', views.public_get_services_list, name='public_get_services_list'),

    # --- Клиенты ---
    path('clients/', views.get_clients, name='get_clients'),
    path('clients/create/', views.create_client, name='create_client'),

    # --- Автомобили ---
    path('cars/', views.get_cars, name='get_all_cars'),
    path('cars/client/<str:client_id>/', views.get_cars, name='get_client_cars'),
    path('cars/create/', views.create_car, name='create_car'),
    path('cars/update/<str:car_id>/', views.update_car, name='update_car'),
    path('cars/delete/<str:car_id>/', views.delete_car, name='delete_car'),

    # --- Марки Авто ---
    path('car-makes/', views.get_car_makes, name='get_car_makes'),
    path('car-makes/create/', views.add_car_make, name='add_car_make'),

    # --- Заказы ---
    path('orders/', views.get_orders, name='get_orders'),
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/update/<str:order_id>/', views.update_order, name='update_order'),
    path('orders/delete/<str:order_id>/', views.delete_order, name='delete_order'),

    # --- Сотрудники и Аутентификация ---
    path('employees/', views.get_employees, name='get_employees'),
    path('employees/create/', views.register_employee, name='create_employee'),
    path('auth/login/', views.login_employee, name='login_employee'),

    # --- Склад ---
    path('inventory/categories/', views.get_inventory_categories, name='get_inventory_categories'),
    path('inventory/categories/create/', views.create_inventory_category, name='create_inventory_category'),
    path('inventory/categories/update/<str:category_id>/', views.update_inventory_category, name='update_inventory_category'),
    path('inventory/categories/delete/<str:category_id>/', views.delete_inventory_category, name='delete_inventory_category'),
    path('inventory/', views.get_inventory_items, name='get_inventory_items'),
    path('inventory/create/', views.create_inventory_item, name='create_inventory_item'),
    path('inventory/update/<str:item_id>/', views.update_inventory_item, name='update_inventory_item'),
    path('inventory/movement/', views.manage_inventory_movement, name='manage_inventory_movement'),

    # --- Отчетность ---
    path('reports/profit_summary/', views.get_profit_summary_report, name='get_profit_summary_report'),

    # --- ПУБЛИЧНЫЕ МАРШРУТЫ ДЛЯ ОНЛАЙН-ЗАПИСИ (кроме услуг) ---
    path('public/available-slots/', views.get_available_slots, name='get_available_slots'),
    path('public/booking/', views.create_public_booking, name='create_public_booking'),

    # --- ПОРТФОЛИО ---
    # Админка
    path('portfolio/', views.get_portfolio_projects, name='get_portfolio_projects'),
    path('portfolio/create/', views.create_portfolio_project, name='create_portfolio_project'),
    path('portfolio/update/<str:project_id>/', views.update_portfolio_project, name='update_portfolio_project'),
    path('portfolio/delete/<str:project_id>/', views.delete_portfolio_project, name='delete_portfolio_project'),
    # Публичный сайт
    path('public/portfolio/', views.get_portfolio_projects, name='public_get_portfolio_list'),
    path('public/portfolio/<slug:slug>/', views.public_get_portfolio_detail, name='public_get_portfolio_detail'),


    # --- ПУБЛИЧНЫЕ МАРШРУТЫ ДЛЯ ОНЛАЙН-ЗАПИСИ (кроме услуг) ---
    path('public/available-slots/', views.get_available_slots, name='get_available_slots'),
    path('public/booking/', views.create_public_booking, name='create_public_booking'),



    # --- Страница о нас ---
    path('public/page/about-us/', views.get_about_us_page, name='get_about_us_page'),
    path('page/about-us/update/', views.update_about_us_page, name='update_about_us_page'),

    # --- БЛОГ (НОВЫЕ МАРШРУТЫ) ---
    path('blog/posts/', views.get_blog_posts, name='get_blog_posts'),
    path('blog/posts/create/', views.create_blog_post, name='create_blog_post'),
    path('blog/posts/update/<str:post_id>/', views.update_blog_post, name='update_blog_post'),
    path('blog/posts/delete/<str:post_id>/', views.delete_blog_post, name='delete_blog_post'),
    path('public/blog/posts/', views.public_get_blog_posts, name='public_get_blog_posts'),
    path('public/blog/post/<slug:slug>/', views.public_get_blog_post_detail, name='public_get_blog_post_detail'),
]