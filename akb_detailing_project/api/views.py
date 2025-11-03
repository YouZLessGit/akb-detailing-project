# api/views.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
import os
from dotenv import load_dotenv
import re
import traceback
from functools import wraps
import jwt
from datetime import datetime, timedelta, timezone
import bcrypt
#from django.utils.text import slugify
from slugify import slugify
import uuid
from django.conf import settings
from django.core.files.storage import default_storage

load_dotenv()

# --- Константы и подключение к базе данных ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "akb_detailing_db")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-secret-key") 

try:
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    services_collection = db['services']
    employees_collection = db['employees']
    clients_collection = db['clients']
    cars_collection = db['cars']
    car_makes_collection = db['car_makes']
    orders_collection = db['orders']
    inventory_collection = db['inventory'] # <-- НОВАЯ КОЛЛЕКЦИЯ
    service_categories_collection = db['service_categories']
    inventory_movements_collection = db['inventory_movements']
    inventory_categories_collection = db['inventory_categories'] # <-- НОВАЯ КОЛЛЕКЦИЯ
    portfolio_collection = db['portfolio']
    blog_posts_collection = db['blog_posts']
    pages_collection = db['pages'] # <-- ДОБАВЬТЕ ЭТУ СТРОКУ
    print("✅ Подключение к MongoDB успешно!")
except Exception as e:
    print(f"❌ Ошибка подключения к MongoDB: {e}")


def role_required(allowed_roles=['Admin']):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'error': 'Токен авторизации отсутствует или некорректен'}, status=401)
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
                username = payload['username']
                employee = employees_collection.find_one({'username': username})
                if not employee:
                    return JsonResponse({'error': 'Пользователь не найден'}, status=401)
                user_role = employee.get('role')
                if user_role not in allowed_roles:
                    return JsonResponse({'error': 'Доступ запрещен. Недостаточно прав.'}, status=403)
                return view_func(request, *args, **kwargs)
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Срок действия токена истек'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Недействительный токен'}, status=401)
            except Exception as e:
                return JsonResponse({'error': f'Внутренняя ошибка сервера: {str(e)}'}, status=500)
        return _wrapped_view
    return decorator    

# --- 1. ФУНКЦИИ ДЛЯ УСЛУГ И ИХ КАТЕГОРИЙ (ЕДИНАЯ ИСПРАВЛЕННАЯ ЛОГИКА) ---

# --- Управление Категориями ---

def get_service_categories(request):
    if request.method == 'GET':
        try:
            categories = list(service_categories_collection.find({}))
            for cat in categories:
                cat['_id'] = str(cat['_id'])
                if cat.get('parent_id'):
                    cat['parent_id'] = str(cat['parent_id'])
            return JsonResponse(categories, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def create_service_category(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category_name = data.get('name')

            if not category_name or not category_name.strip():
                return JsonResponse({"error": "Название категории не может быть пустым"}, status=400)
            
            base_slug = slugify(category_name) # <-- Теперь эта функция работает правильно!
            
            if not base_slug:
                return JsonResponse({
                    "error": "Название категории не может состоять только из спецсимволов"
                }, status=400)

            slug = base_slug
            while service_categories_collection.find_one({'slug': slug}):
                slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
            
            new_category = {
                'name': category_name, 
                'slug': slug,
                'parent_id': ObjectId(data['parent_id']) if data.get('parent_id') else None,
                'main_image_url': data.get('main_image_url', ''),
                'description': data.get('description', '')
            }
            result = service_categories_collection.insert_one(new_category)
            return JsonResponse({"message": "Категория создана", "_id": str(result.inserted_id)}, status=201)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def update_service_category(request, category_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            category_name = data.get('name')

            if category_name is not None and not category_name.strip():
                 return JsonResponse({"error": "Название категории не может быть пустым"}, status=400)

            try:
                cat_obj_id = ObjectId(category_id)
                category_doc = service_categories_collection.find_one({'_id': cat_obj_id})
                if not category_doc:
                    return JsonResponse({'error': 'Категория с таким ID не найдена'}, status=404)
            except InvalidId:
                 return JsonResponse({'error': 'Некорректный формат ID категории'}, status=400)

            update_data = {}
            for key in ['name', 'main_image_url', 'description']:
                if key in data:
                    update_data[key] = data[key]
            
            if 'parent_id' in data:
                 update_data['parent_id'] = ObjectId(data['parent_id']) if data.get('parent_id') else None

            name_has_changed = 'name' in update_data and update_data['name'] != category_doc.get('name')
            slug_is_missing = not category_doc.get('slug')

            if name_has_changed or slug_is_missing:
                new_name = update_data.get('name', category_doc.get('name'))
                base_slug = slugify(new_name) # <-- Теперь эта функция работает правильно!

                if not base_slug:
                    return JsonResponse({"error": "Название не может состоять только из спецсимволов"}, status=400)

                slug = base_slug
                while service_categories_collection.find_one({'slug': slug, '_id': {'$ne': cat_obj_id}}):
                    slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
                update_data['slug'] = slug

            if not update_data:
                return JsonResponse({'message': 'Данные не изменились'})

            result = service_categories_collection.update_one({'_id': cat_obj_id}, {'$set': update_data})
            
            if result.modified_count > 0:
                 return JsonResponse({'message': 'Категория успешно обновлена'})
            else:
                 return JsonResponse({'message': 'Данные не изменились'})

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": f"Внутренняя ошибка сервера: {str(e)}"}, status=500)

@csrf_exempt
def delete_service_category(request, category_id):
    if request.method == 'DELETE':
        try:
            cat_obj_id = ObjectId(category_id)
            if services_collection.find_one({'category_id': category_id}):
                return JsonResponse({"error": "Нельзя удалить категорию, в которой есть услуги"}, status=409)
            if service_categories_collection.find_one({'parent_id': cat_obj_id}):
                return JsonResponse({"error": "Нельзя удалить категорию, у которой есть дочерние категории"}, status=409)
            result = service_categories_collection.delete_one({'_id': cat_obj_id})
            if result.deleted_count > 0:
                return JsonResponse({'message': 'Категория удалена'})
            return JsonResponse({'error': 'Категория не найдена'}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

# --- Управление Услугами ---

def get_admin_services(request):
    """
    ЭТОТ ЭНДПОИНТ ИСПОЛЬЗУЕТСЯ ТОЛЬКО В АДМИНКЕ
    Возвращает сгруппированный список для удобного отображения в панели управления.
    """
    if request.method == 'GET':
        try:
            pipeline = [
                {'$addFields': {'category_obj_id': {'$toObjectId': '$category_id'}}},
                {'$lookup': {'from': 'service_categories', 'localField': 'category_obj_id', 'foreignField': '_id', 'as': 'category_details'}},
                {'$unwind': '$category_details'},
                {'$sort': {'name': 1}},
                {'$group': {
                    '_id': '$category_details._id', 'category_name': {'$first': '$category_details.name'},
                    'services': {'$push': '$$ROOT'}
                }},
                {'$project': {
                    '_id': 0, 'category_id': {'$toString': '$_id'}, 'category_name': 1,
                    'services': {
                        '$map': {
                            'input': '$services', 'as': 'service',
                            'in': {
                                '_id': {'$toString': '$$service._id'}, 'name': '$$service.name', 'slug': '$$service.slug',
                                'category_id': '$$service.category_id', 'main_image_url': '$$service.main_image_url',
                                'short_description': '$$service.short_description', 'price_from': '$$service.price_from',
                                'duration': '$$service.duration', 'rich_content': '$$service.rich_content'
                            }
                        }
                    }
                }},
                {'$sort': {'category_name': 1}}
            ]
            grouped_services = list(services_collection.aggregate(pipeline))
            return JsonResponse(grouped_services, safe=False)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def create_service(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if not all(k in data and data[k] is not None for k in ['name', 'price_from', 'duration', 'category_id']):
                return JsonResponse({"error": "Требуются: Название, Цена 'от', Длительность и ID Категории"}, status=400)
            base_slug = slugify(data['name'])
            slug = base_slug
            while services_collection.find_one({'slug': slug}):
                slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
            new_service_data = {
                'name': data['name'], 'slug': slug, 'category_id': data['category_id'],
                'main_image_url': data.get('main_image_url', ''), 'short_description': data.get('short_description', ''),
                'price_from': float(data['price_from']), 'duration': int(data['duration']),
                'rich_content': data.get('rich_content', ''),
                'price': float(data['price_from']), 'description': data.get('short_description', '')
            }
            services_collection.insert_one(new_service_data)
            return JsonResponse({"message": "Услуга успешно создана"}, status=201)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)

@csrf_exempt
def update_service(request, service_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            update_data = {}
            allowed_fields = ['name', 'category_id', 'main_image_url', 'short_description', 'price_from', 'duration', 'rich_content']
            for field in allowed_fields:
                if field in data:
                    update_data[field] = data[field]
            if 'name' in update_data:
                base_slug = slugify(update_data['name'])
                slug = base_slug
                while services_collection.find_one({'slug': slug, '_id': {'$ne': ObjectId(service_id)}}):
                    slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
                update_data['slug'] = slug
            if 'price_from' in update_data: update_data['price'] = float(update_data['price_from'])
            if 'short_description' in update_data: update_data['description'] = update_data['short_description']
            
            result = services_collection.update_one({'_id': ObjectId(service_id)}, {'$set': update_data})
            if result.modified_count > 0:
                return JsonResponse({'message': 'Услуга успешно обновлена'})
            return JsonResponse({'error': 'Услуга не найдена или данные не изменились'}, status=404)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only PUT method is allowed"}, status=405)

@csrf_exempt
def delete_service(request, service_id):
    if request.method == 'DELETE':
        try:
            result = services_collection.delete_one({'_id': ObjectId(service_id)})
            if result.deleted_count > 0:
                return JsonResponse({'message': 'Услуга удалена'})
            return JsonResponse({'error': 'Услуга не найдена'}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only DELETE method is allowed"}, status=405)

# --- Публичные Эндпоинты для сайта ---

def public_get_top_level_categories(request):
    """
    Отдает только родительские категории для главной страницы /services.
    ГАРАНТИРОВАННО ВКЛЮЧАЕТ SLUG.
    """
    if request.method == 'GET':
        try:
            # Используем проекцию, чтобы гарантированно получить нужные поля
            projection = {'_id': 1, 'name': 1, 'slug': 1, 'main_image_url': 1}
            top_level_categories = list(service_categories_collection.find(
                {'parent_id': None},
                projection 
            ))
            
            # Конвертируем _id в строку
            for cat in top_level_categories:
                cat['_id'] = str(cat['_id'])
                
            return JsonResponse(top_level_categories, safe=False)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

def public_get_category_page(request, slug):
    """
    Отдает данные для страницы категории /services/category/:slug.
    """
    if request.method == 'GET':
        try:
            parent_category = service_categories_collection.find_one({'slug': slug})
            if not parent_category:
                return JsonResponse({'error': 'Категория не найдена'}, status=404)
            parent_category['_id'] = str(parent_category['_id'])
            parent_category_obj_id = ObjectId(parent_category['_id'])
            child_categories = list(service_categories_collection.find({'parent_id': parent_category_obj_id}))
            all_category_ids_to_search = [parent_category['_id']] + [str(cat['_id']) for cat in child_categories]
            services_in_group = list(services_collection.find({'category_id': {'$in': all_category_ids_to_search}}))
            for srv in services_in_group:
                srv['_id'] = str(srv['_id'])
            return JsonResponse({"category": parent_category, "services": services_in_group})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": "Категория не найдена"}, status=404)
    return JsonResponse({"error": "Invalid request method"}, status=405)

def public_get_service_details(request, slug):
    """
    Отдает детальную информацию для страницы услуги /service/:slug.
    """
    if request.method == 'GET':
        try:
            service = services_collection.find_one({'slug': slug})
            if not service:
                return JsonResponse({'error': 'Услуга не найдена'}, status=404)
            service['_id'] = str(service['_id'])
            return JsonResponse(service)
        except Exception as e:
            return JsonResponse({"error": "Услуга не найдена"}, status=404)
    return JsonResponse({"error": "Invalid request method"}, status=405)

# --- 2. ФУНКЦИИ ДЛЯ КЛИЕНТОВ ---
def get_clients(request):
    if request.method == 'GET':
        try:
            clients = list(clients_collection.find({}))
            for client in clients:
                client['_id'] = str(client['_id'])
            return JsonResponse(clients, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def create_client(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if 'full_name' not in data or 'phone_number' not in data:
                return JsonResponse({"error": "ФИО и номер телефона обязательны"}, status=400)
            result = clients_collection.insert_one(data)
            return JsonResponse({
                "message": "Client created successfully",
                "_id": str(result.inserted_id)
            }, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)

# --- 3. ФУНКЦИИ ДЛЯ АВТОМОБИЛЕЙ ---
def get_cars(request, client_id=None):
    if request.method == 'GET':
        try:
            query = {}
            if client_id:
                query['client_id'] = client_id
            
            cars = list(cars_collection.find(query))
            for car in cars:
                car['_id'] = str(car['_id'])
            return JsonResponse(cars, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def create_car(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if 'client_id' not in data or 'make' not in data or 'model' not in data or 'license_plate' not in data:
                return JsonResponse({"error": "Не все обязательные поля для автомобиля указаны"}, status=400)
            
            result = cars_collection.insert_one(data)
            return JsonResponse({
                "message": "Car created successfully",
                "_id": str(result.inserted_id)
            }, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)

@csrf_exempt
def update_car(request, car_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            # Удаляем client_id из данных для обновления, чтобы его нельзя было случайно поменять
            if 'client_id' in data:
                del data['client_id']

            result = cars_collection.update_one(
                {'_id': ObjectId(car_id)}, # Находим документ по его ID
                {'$set': data}            # Устанавливаем новые значения
            )

            if result.modified_count > 0:
                return JsonResponse({'message': 'Автомобиль успешно обновлен'})
            else:
                return JsonResponse({'error': 'Автомобиль не найден или данные не изменились'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only PUT method is allowed'}, status=405)



@csrf_exempt
def delete_car(request, car_id):
    if request.method == 'DELETE':
        try:
            result = cars_collection.delete_one({'_id': ObjectId(car_id)}) # Находим и удаляем по ID

            if result.deleted_count > 0:
                return JsonResponse({'message': 'Автомобиль успешно удален'})
            else:
                return JsonResponse({'error': 'Автомобиль не найден'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only DELETE method is allowed'}, status=405)


# --- 4. ФУНКЦИИ ДЛЯ МАРОК АВТОМОБИЛЕЙ ---
def get_car_makes(request):
    if request.method == 'GET':
        try:
            car_makes = list(car_makes_collection.find({}))
            for make in car_makes:
                make['_id'] = str(make['_id'])
            return JsonResponse(car_makes, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def add_car_make(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if 'name' not in data:
                return JsonResponse({"error": "Name of car make is required"}, status=400)
            if car_makes_collection.find_one({'name': data['name']}):
                return JsonResponse({"error": "Car make already exists"}, status=409)
            
            result = car_makes_collection.insert_one({'name': data['name']})
            return JsonResponse({"message": "Car make added", "_id": str(result.inserted_id)}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only POST method allowed"}, status=405)


# --- 5. ФУНКЦИИ ДЛЯ АУТЕНТИФИКАЦИИ ---
def get_employees(request):
    """
    НОВАЯ ФУНКЦИЯ
    Возвращает список всех сотрудников (без хэшей паролей) для использования в интерфейсе.
    """
    if request.method == 'GET':
        try:
            # Projection={'password': 0} исключает поле 'password' из ответа. Это важно для безопасности.
            employees = list(employees_collection.find({}, {'password': 0}))
            for employee in employees:
                employee['_id'] = str(employee['_id'])
            return JsonResponse(employees, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def register_employee(request):
    """
    МОДИФИЦИРОВАННАЯ ФУНКЦИЯ
    Теперь она не просто регистрирует логин/пароль, а создает полноценного сотрудника.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            full_name = data.get('full_name') # <-- НОВОЕ ПОЛЕ
            role = data.get('role')             # <-- НОВОЕ ПОЛЕ

            # <-- ОБНОВЛЕННАЯ ВАЛИДАЦИЯ
            if not all([username, password, full_name, role]):
                return JsonResponse({'error': 'Требуются: username, password, full_name, role'}, status=400)

            if employees_collection.find_one({'username': username}):
                return JsonResponse({'error': 'Сотрудник с таким логином уже существует'}, status=409)

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # <-- ОБНОВЛЕННЫЙ ДОКУМЕНТ ДЛЯ СОХРАНЕНИЯ
            employees_collection.insert_one({
                'username': username,
                'password': hashed_password.decode('utf-8'),
                'full_name': full_name,
                'role': role
            })
            
            return JsonResponse({'message': 'Сотрудник успешно создан'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


@csrf_exempt
def login_employee(request): # <-- ОБНОВЛЕНО
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            if not username or not password:
                return JsonResponse({'error': 'Username and password are required'}, status=400)
            
            employee = employees_collection.find_one({'username': username})
            if not employee:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
            
            if bcrypt.checkpw(password.encode('utf-8'), employee['password'].encode('utf-8')):
                payload = {
                    'username': username,
                    'exp': datetime.now(timezone.utc) + timedelta(hours=24)
                }
                token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
                
                # ВОЗВРАЩАЕМ ДАННЫЕ ПОЛЬЗОВАТЕЛЯ, ВКЛЮЧАЯ ID
                return JsonResponse({
                    'token': token,
                    'user': {
                        '_id': str(employee['_id']), # <-- ДОБАВЛЕНО
                        'username': employee['username'],
                        'full_name': employee.get('full_name', ''),
                        'role': employee.get('role', 'User')
                    }
                })
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

def get_orders(request):
    if request.method == 'GET':
        try:
            # В будущем здесь можно будет добавить фильтрацию по дате, 
            # например: orders = list(orders_collection.find({'start_time': {'$gte': '2025-10-01', '$lt': '2025-11-01'}}))
            orders = list(orders_collection.find({}))
            for order in orders:
                order['_id'] = str(order['_id'])
            return JsonResponse(orders, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # --- 1. Валидация ---
            required_fields = ['client_id', 'car_id', 'service_ids', 'start_time']
            if not all(field in data for field in required_fields):
                return JsonResponse({'error': 'Не все обязательные поля указаны'}, status=400)
            
            # --- 2. Расчет общей стоимости и длительности ---
            total_price = 0
            total_duration = 0
            
            service_ids_obj = [ObjectId(sid) for sid in data['service_ids']]
            selected_services = list(services_collection.find({'_id': {'$in': service_ids_obj}}))
            
            if len(selected_services) != len(data['service_ids']):
                return JsonResponse({'error': 'Одна или несколько услуг не найдены.'}, status=400)

            for service in selected_services:
                if 'price' not in service or 'duration' not in service:
                    return JsonResponse({'error': f"Услуга '{service.get('name')}' не имеет цены или длительности."}, status=400)
                
                total_price += int(service['price'])
                total_duration += int(service['duration'])
            
            if total_duration <= 0:
                return JsonResponse({'error': 'Длительность заказа должна быть больше нуля.'}, status=400)
                
            # --- 3. РАБОТА С ДАТОЙ (САМАЯ НАДЕЖНАЯ ВЕРСИЯ) ---
            start_time_str = data['start_time']
            
            # Убираем 'Z' если она есть, т.к. мы и так будем работать в UTC
            if start_time_str.endswith('Z'):
                start_time_str = start_time_str[:-1]

            # fromisoformat - более гибкий метод, чем strptime
            start_time = datetime.fromisoformat(start_time_str)
            start_time = start_time.replace(tzinfo=timezone.utc)
            
            end_time = start_time + timedelta(minutes=total_duration)

            start_time_iso = start_time.isoformat()
            end_time_iso = end_time.isoformat()

            # --- 4. Проверка на конфликты ---
            conflict_query = {
                'start_time': {'$lt': end_time_iso},
                'end_time': {'$gt': start_time_iso}
            }
            conflicting_order = orders_collection.find_one(conflict_query)

            if conflicting_order:
                # Более детальное сообщение об ошибке
                conflicting_client = clients_collection.find_one({'_id': ObjectId(conflicting_order.get('client_id'))})
                client_name = conflicting_client.get('full_name') if conflicting_client else "Другой клиент"
                return JsonResponse({'error': f'Это время пересекается с записью клиента: {client_name}'}, status=409)

            # --- 5. Создание документа заказа ---
            new_order = {
                'client_id': data['client_id'],
                'car_id': data['car_id'],
                'service_ids': data['service_ids'],
                'start_time': start_time_iso,
                'end_time': end_time_iso,
                'total_price': total_price,
                'status': 'Запланирован',
            }
            
            result = orders_collection.insert_one(new_order)
            
            return JsonResponse({ "message": "Заказ успешно создан", "_id": str(result.inserted_id) }, status=201)

        except Exception as e:
            # Наш надежный логгер ошибок
            print(f"!!! КРИТИЧЕСКАЯ ОШИБКА в create_order: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': 'Критическая ошибка на сервере.'}, status=500)
    
    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

@csrf_exempt
def update_order(request, order_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            # Мы будем обновлять только те поля, которые пришли в запросе
            # Например, можно будет прислать только {'status': 'В работе'}
            result = orders_collection.update_one(
                {'_id': ObjectId(order_id)},
                {'$set': data}
            )
            if result.modified_count > 0:
                return JsonResponse({'message': 'Заказ успешно обновлен'})
            else:
                return JsonResponse({'error': 'Заказ не найден или данные не изменились'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only PUT method is allowed'}, status=405)

# === НОВАЯ ФУНКЦИЯ ДЛЯ УДАЛЕНИЯ ЗАКАЗА ===
@csrf_exempt
def delete_order(request, order_id):
    if request.method == 'DELETE':
        try:
            result = orders_collection.delete_one({'_id': ObjectId(order_id)})
            if result.deleted_count > 0:
                return JsonResponse({'message': 'Заказ успешно удален'})
            else:
                return JsonResponse({'error': 'Заказ не найден'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only DELETE method is allowed'}, status=405)

# === КАТЕГОРИИ ТОВАРОВ ===

# === КАТЕГОРИИ ТОВАРОВ ===
def get_inventory_categories(request):
    if request.method == 'GET':
        try:
            categories = list(inventory_categories_collection.find({}))
            for category in categories:
                category['_id'] = str(category['_id'])
                if 'parent_id' in category and category['parent_id']:
                    category['parent_id'] = str(category['parent_id'])
            return JsonResponse(categories, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def create_inventory_category(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if 'name' not in data or not data['name']:
                return JsonResponse({"error": "Название категории обязательно"}, status=400)
            
            new_category = {'name': data['name']}
            parent_id = data.get('parent_id')

            if parent_id:
                new_category['parent_id'] = ObjectId(parent_id)
            else:
                new_category['parent_id'] = None

            result = inventory_categories_collection.insert_one(new_category)
            return JsonResponse({"message": "Категория создана", "_id": str(result.inserted_id)}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def update_inventory_category(request, category_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            if 'name' not in data or not data['name']:
                return JsonResponse({"error": "Название категории обязательно"}, status=400)
            
            update_data = {'name': data['name']}
            parent_id = data.get('parent_id')

            if parent_id and parent_id == category_id:
                 return JsonResponse({"error": "Категория не может быть дочерней самой себе"}, status=400)

            update_data['parent_id'] = ObjectId(parent_id) if parent_id else None

            result = inventory_categories_collection.update_one(
                {'_id': ObjectId(category_id)},
                {'$set': update_data}
            )
            if result.modified_count > 0:
                return JsonResponse({'message': 'Категория обновлена'})
            return JsonResponse({'error': 'Категория не найдена или данные не изменились'}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def delete_inventory_category(request, category_id):
    if request.method == 'DELETE':
        try:
            if inventory_categories_collection.find_one({'parent_id': ObjectId(category_id)}):
                return JsonResponse({"error": "Нельзя удалить категорию, у которой есть подкатегории"}, status=409)
            
            result = inventory_categories_collection.delete_one({'_id': ObjectId(category_id)})
            if result.deleted_count > 0:
                return JsonResponse({'message': 'Категория удалена'})
            return JsonResponse({'error': 'Категория не найдена'}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        

# --- 6. ФУНКЦИИ ДЛЯ СКЛАДА (INVENTORY) ---

def get_inventory_items(request):
    if request.method == 'GET':
        try:
            items = list(inventory_collection.find({}))
            for item in items:
                item['_id'] = str(item['_id'])
            return JsonResponse(items, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
# @role_required(['Admin', 'Manager']) # <-- Раскомментируйте, когда будете готовы внедрять права
@csrf_exempt
def create_inventory_item(request): # <-- ОБНОВЛЕНО
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            required_fields = ['name', 'quantity', 'unit', 'cost', 'category_id']
            if not all(k in data for k in required_fields):
                return JsonResponse({"error": "Требуются все поля: name, quantity, unit, cost, category_id"}, status=400)
            
            data['quantity'] = float(data['quantity'])
            data['cost'] = float(data['cost']) # <-- ДОБАВЛЕНО
            
            result = inventory_collection.insert_one(data)
            return JsonResponse({"message": "Позиция успешно добавлена", "_id": str(result.inserted_id)}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
@csrf_exempt
def update_inventory_item(request, item_id): # <-- НОВАЯ ФУНКЦИЯ
    """Обновляет информацию о товаре (кроме количества)."""
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            update_fields = {}
            
            # Собираем только те поля, которые можно редактировать
            editable_fields = ['name', 'unit', 'cost', 'category_id', 'low_stock_threshold']
            for field in editable_fields:
                if field in data:
                    update_fields[field] = data[field]
            
            if 'cost' in update_fields:
                update_fields['cost'] = float(update_fields['cost'])

            if not update_fields:
                return JsonResponse({"error": "Нет данных для обновления"}, status=400)

            result = inventory_collection.update_one(
                {'_id': ObjectId(item_id)},
                {'$set': update_fields}
            )
            if result.modified_count > 0:
                return JsonResponse({'message': 'Товар обновлен'})
            return JsonResponse({'error': 'Товар не найден или данные не изменились'}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
# @role_required(['Admin', 'Manager', 'Detailer'])
def manage_inventory_movement(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            change_quantity = data.get('change_quantity')
            movement_type = data.get('type')
            employee_id = data.get('employee_id')
            order_id = data.get('order_id', None)

            if not all([item_id, change_quantity, movement_type, employee_id]):
                 return JsonResponse({"error": "Не все поля для движения товара указаны"}, status=400)

            change_quantity = float(change_quantity)

            # --- ИСПРАВЛЕНИЕ И УЛУЧШЕНИЕ ЗДЕСЬ ---
            try:
                item_obj_id = ObjectId(item_id)
                employee_obj_id = ObjectId(employee_id)
                order_obj_id = ObjectId(order_id) if order_id else None
            except InvalidId:
                return JsonResponse({"error": "Передан некорректный ID"}, status=400)
            # --- КОНЕЦ УЛУЧШЕНИЯ ---
            
            item = inventory_collection.find_one({'_id': item_obj_id})
            if not item:
                 return JsonResponse({"error": "Товар не найден на складе"}, status=404)

            if movement_type == 'withdrawal' and item.get('quantity', 0) < change_quantity:
                return JsonResponse({"error": f"Недостаточно товара на складе. Остаток: {item.get('quantity', 0)}"}, status=409)

            quantity_modifier = -change_quantity if movement_type == 'withdrawal' else change_quantity
            
            inventory_collection.update_one(
                {'_id': item_obj_id},
                {'$inc': {'quantity': quantity_modifier}}
            )

            movement_log = {
                "item_id": item_obj_id,
                "employee_id": employee_obj_id,
                "order_id": order_obj_id,
                "change_quantity": quantity_modifier,
                "type": movement_type,
                "timestamp": datetime.now(timezone.utc)
            }
            inventory_movements_collection.insert_one(movement_log)

            return JsonResponse({"message": "Операция со складом успешно выполнена"}, status=200)
            
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": f"Ошибка сервера: {str(e)}"}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

# --- 7. ФУНКЦИИ ДЛЯ ОТЧЕТНОСТИ ---

@csrf_exempt
def get_profit_summary_report(request):
    if request.method == 'GET':
        try:
            start_date_str = request.GET.get('start_date')
            end_date_str = request.GET.get('end_date')

            if not start_date_str or not end_date_str:
                return JsonResponse({"error": "Требуются параметры start_date и end_date"}, status=400)

            start_date = datetime.fromisoformat(start_date_str).replace(tzinfo=timezone.utc)
            end_date = datetime.fromisoformat(end_date_str).replace(tzinfo=timezone.utc)

            pipeline = [
                {'$match': {'status': 'Выполнен', 'start_time': {'$gte': start_date.isoformat(), '$lte': end_date.isoformat()}}},
                {'$lookup': {
                    'from': 'inventory_movements', 'let': {'order_id': '$_id'},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$order_id', '$$order_id']}}},
                        {'$lookup': {'from': 'inventory', 'localField': 'item_id', 'foreignField': '_id', 'as': 'item_details'}},
                        {'$unwind': '$item_details'},
                        {'$group': {'_id': '$order_id', 'total_cost': {'$sum': {'$multiply': ['$item_details.cost', '$change_quantity', -1]}}}}
                    ], 'as': 'material_cost_calc'
                }},
                {'$addFields': {
                    'total_material_cost': {'$ifNull': [{'$arrayElemAt': ['$material_cost_calc.total_cost', 0]}, 0]},
                    'profit': {'$subtract': ['$total_price', {'$ifNull': [{'$arrayElemAt': ['$material_cost_calc.total_cost', 0]}, 0]}]}
                }},
                {'$addFields': {
                    'employee_obj_id': {'$cond': {'if': '$employee_id', 'then': {'$toObjectId': '$employee_id'}, 'else': None}},
                    'client_obj_id': {'$cond': {'if': '$client_id', 'then': {'$toObjectId': '$client_id'}, 'else': None}}
                }},
                {'$lookup': {'from': 'clients', 'localField': 'client_obj_id', 'foreignField': '_id', 'as': 'client_details'}},
                {'$group': {
                    '_id': '$employee_obj_id',
                    'completed_orders_count': {'$sum': 1},
                    'total_revenue': {'$sum': '$total_price'},
                    'total_material_cost': {'$sum': '$total_material_cost'},
                    'total_profit': {'$sum': '$profit'},
                    'orders_details': {'$push': {
                        'order_id': '$_id',
                        'start_time': '$start_time',
                        'revenue': '$total_price',
                        'material_cost': '$total_material_cost',
                        'profit': '$profit',
                        'client_name': {'$ifNull': [{'$arrayElemAt': ['$client_details.full_name', 0]}, 'Клиент удален']}
                    }}
                }},
                {'$lookup': {'from': 'employees', 'localField': '_id', 'foreignField': '_id', 'as': 'employee_details'}},
                
                # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
                {'$project': {
                    '_id': 0, 
                    'employee_id': { '$toString': '$_id' }, # <-- Конвертируем ObjectId в строку
                    'employee_name': {'$ifNull': [{'$arrayElemAt': ['$employee_details.full_name', 0]}, 'Не назначен']},
                    'completed_orders_count': 1, 
                    'total_revenue': 1, 
                    'total_material_cost': 1, 
                    'total_profit': 1,
                    # Проходимся по массиву и конвертируем каждый order_id
                    'orders_details': {
                        '$map': {
                            'input': '$orders_details',
                            'as': 'order',
                            'in': {
                                'order_id': { '$toString': '$$order.order_id' }, # <-- Конвертируем ObjectId в строку
                                'start_time': '$$order.start_time',
                                'revenue': '$$order.revenue',
                                'material_cost': '$$order.material_cost',
                                'profit': '$$order.profit',
                                'client_name': '$$order.client_name'
                            }
                        }
                    }
                }}
            ]
            
            report_data = list(orders_collection.aggregate(pipeline))
            return JsonResponse(report_data, safe=False)

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)



# --- 8. ПУБЛИЧНЫЕ API ЭНДПОИНТЫ (БЕЗ АВТОРИЗАЦИИ) ---

@csrf_exempt
def public_get_services(request):
    """
    Возвращает упрощенный список услуг для публичного сайта.
    """
    if request.method == 'GET':
        try:
            # Projection используется, чтобы отдать только нужные поля
            projection = {'_id': 1, 'name': 1, 'description': 1, 'price': 1, 'duration': 1}
            services = list(services_collection.find({}, projection))
            
            # Преобразуем ObjectId в строку для JSON-совместимости
            for service in services:
                service['id'] = str(service.pop('_id'))
                
            return JsonResponse(services, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only GET method is allowed"}, status=405)


@csrf_exempt
def get_available_slots(request):
    """
    Возвращает доступные временные слоты для записи на конкретную дату.
    Принимает query-параметры: `date` (YYYY-MM-DD) и `duration` (в минутах).
    """
    if request.method == 'GET':
        try:
            # 1. Получение и валидация параметров
            target_date_str = request.GET.get('date')
            duration_str = request.GET.get('duration')
            
            if not target_date_str or not duration_str:
                return JsonResponse({'error': 'Требуются параметры "date" и "duration"'}, status=400)
            
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                duration_minutes = int(duration_str)
            except (ValueError, TypeError):
                return JsonResponse({'error': 'Некорректный формат даты или длительности'}, status=400)

            # 2. Определение рабочего времени и существующих записей
            work_start_hour = 9
            work_end_hour = 20
            slot_interval_minutes = 30 # Шаг, с которым проверяем доступность (e.g., 9:00, 9:30, 10:00)

            # Находим начало и конец дня в UTC для запроса в MongoDB
            day_start = datetime(target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc)
            day_end = day_start + timedelta(days=1)

            existing_orders = list(orders_collection.find({
                'start_time': {'$gte': day_start.isoformat(), '$lt': day_end.isoformat()}
            }, {'start_time': 1, 'end_time': 1}))
            
            # Конвертируем строки ISO в объекты datetime для удобного сравнения
            busy_slots = []
            for order in existing_orders:
                busy_slots.append({
                    'start': datetime.fromisoformat(order['start_time'].replace('Z', '+00:00')),
                    'end': datetime.fromisoformat(order['end_time'].replace('Z', '+00:00'))
                })

            # 3. Генерация и проверка слотов
            available_slots = []
            potential_slot_time = day_start.replace(hour=work_start_hour)
            
            while potential_slot_time.hour < work_end_hour:
                potential_end_time = potential_slot_time + timedelta(minutes=duration_minutes)

                # Пропускаем слот, если он заканчивается позже рабочего дня
                if potential_end_time.hour > work_end_hour or (potential_end_time.hour == work_end_hour and potential_end_time.minute > 0):
                    break
                
                is_free = True
                for busy in busy_slots:
                    # Проверка на пересечение интервалов: (StartA < EndB) and (EndA > StartB)
                    if potential_slot_time < busy['end'] and potential_end_time > busy['start']:
                        is_free = False
                        break
                
                if is_free:
                    available_slots.append(potential_slot_time.strftime('%H:%M'))

                potential_slot_time += timedelta(minutes=slot_interval_minutes)
                
            return JsonResponse(available_slots, safe=False)

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': f'Внутренняя ошибка сервера: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Only GET method is allowed'}, status=405)


@csrf_exempt
def create_public_booking(request):
    """
    Создает новую запись (заказ) от имени клиента.
    Автоматически создает клиента, если его нет в базе.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # 1. Валидация входных данных
            client_data = data.get('client', {})
            car_data = data.get('car', {})
            service_id = data.get('service_id')
            start_time_str = data.get('start_time')

            if not all([client_data.get('name'), client_data.get('phone'), car_data.get('make'), car_data.get('model'), service_id, start_time_str]):
                return JsonResponse({'error': 'Не все поля для создания записи заполнены'}, status=400)

            # 2. Поиск или создание клиента и автомобиля
            phone_number = client_data['phone']
            client = clients_collection.find_one({'phone_number': phone_number})
            
            if not client:
                new_client = {
                    'full_name': client_data['name'],
                    'phone_number': phone_number
                }
                client_id = clients_collection.insert_one(new_client).inserted_id
            else:
                client_id = client['_id']

            # Для простоты всегда создаем новую машину, в будущем можно добавить проверку по гос. номеру
            new_car = {
                'client_id': str(client_id),
                'make': car_data['make'],
                'model': car_data['model'],
                'license_plate': car_data.get('plate_number', 'Не указан')
            }
            car_id = cars_collection.insert_one(new_car).inserted_id
            
            # 3. Получение информации об услуге и расчет времени
            service = services_collection.find_one({'_id': ObjectId(service_id)})
            if not service:
                return JsonResponse({'error': 'Выбранная услуга не найдена'}, status=404)

            duration_minutes = service.get('duration', 0)
            start_time = datetime.fromisoformat(start_time_str).replace(tzinfo=timezone.utc)
            end_time = start_time + timedelta(minutes=duration_minutes)

            # 4. Финальная проверка на конфликты перед записью
            conflict_query = {'start_time': {'$lt': end_time.isoformat()}, 'end_time': {'$gt': start_time.isoformat()}}
            if orders_collection.find_one(conflict_query):
                return JsonResponse({'error': 'Извините, это время только что было занято. Пожалуйста, выберите другое.'}, status=409)

            # 5. Создание заказа
            new_order = {
                'client_id': str(client_id),
                'car_id': str(car_id),
                'service_ids': [service_id], # Публичная запись пока на одну услугу
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'total_price': service.get('price', 0),
                'status': 'Ожидает подтверждения', # Новый статус для записей с сайта
                'employee_id': None, # Сотрудник будет назначен менеджером
            }
            result = orders_collection.insert_one(new_order)
            
            return JsonResponse({
                "success": True,
                "message": "Спасибо! Ваша запись успешно создана. Мы скоро свяжемся с вами для подтверждения.",
                "order_id": str(result.inserted_id)
            }, status=201)

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': f'Внутренняя ошибка сервера: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

# === НОВАЯ УНИВЕРСАЛЬНАЯ ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ ПЛОСКОГО СПИСКА УСЛУГ ===
@csrf_exempt
def public_get_services_list(request):
    """
    Возвращает плоский список всех услуг с ключевыми полями.
    Используется и в админке (для календаря), и на сайте (для онлайн-записи).
    """
    if request.method == 'GET':
        try:
            # Projection используется, чтобы отдать только нужные поля и переименовать их
            # для совместимости с фронтендом.
            pipeline = [
                {
                    '$project': {
                        'id': {'$toString': '$_id'}, # Преобразуем ObjectId в строку и называем 'id'
                        'name': '$name',
                        'description': '$short_description', # Используем short_description как description
                        'price': '$price_from',          # Используем price_from как price
                        'duration': '$duration',
                        '_id': 0 # Исключаем оригинальное поле _id
                    }
                }
            ]
            services = list(services_collection.aggregate(pipeline))
            return JsonResponse(services, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only GET method is allowed"}, status=405)



# --- 9. ФУНКЦИИ ДЛЯ ПОРТФОЛИО ---

@csrf_exempt
def create_portfolio_project(request):
    if request.method == 'POST':
        try:
            data = request.POST
            images = request.FILES.getlist('gallery_images')

            # ИЗМЕНЕНИЕ: Добавляем проверку на наличие даты
            if not all(k in data for k in ['title', 'category', 'date_completed']) or not images:
                return JsonResponse({"error": "Требуются Заголовок, Категория, Дата и хотя бы одно изображение"}, status=400)

            gallery_urls = []
            project_folder = os.path.join('portfolio', str(uuid.uuid4()))
            
            for image in images:
                file_name = f"{uuid.uuid4().hex}_{image.name}"
                file_path = os.path.join(project_folder, file_name)
                saved_path = default_storage.save(file_path, image)
                gallery_urls.append(default_storage.url(saved_path))

            base_slug = slugify(data['title'])
            slug = base_slug
            while portfolio_collection.find_one({'slug': slug}):
                slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"

            new_project = {
                'title': data['title'],
                'slug': slug,
                'category': data['category'],
                'main_image_url': gallery_urls[0], 
                'description': data.get('description', ''),
                'gallery_images': gallery_urls,
                # ИЗМЕНЕНИЕ: Берем дату из формы, а не генерируем автоматически
                'date_completed': data['date_completed']
            }
            result = portfolio_collection.insert_one(new_project)
            return JsonResponse({"message": "Проект успешно создан", "_id": str(result.inserted_id)}, status=201)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def update_portfolio_project(request, project_id):
    if request.method == 'POST':
        try:
            data = request.POST
            new_images = request.FILES.getlist('gallery_images')
            existing_urls = data.getlist('existing_images')

            update_data = {}
            # ИЗМЕНЕНИЕ: Добавляем 'date_completed' в список обновляемых полей
            for key in ['title', 'category', 'description', 'date_completed']:
                if key in data:
                    update_data[key] = data[key]

            final_gallery_urls = existing_urls
            if new_images:
                project_folder = os.path.join('portfolio', str(uuid.uuid4()))
                for image in new_images:
                    file_name = f"{uuid.uuid4().hex}_{image.name}"
                    file_path = os.path.join(project_folder, file_name)
                    saved_path = default_storage.save(file_path, image)
                    final_gallery_urls.append(default_storage.url(saved_path))
            
            if not final_gallery_urls:
                return JsonResponse({"error": "Проект должен содержать хотя бы одно изображение"}, status=400)
            
            update_data['gallery_images'] = final_gallery_urls
            update_data['main_image_url'] = final_gallery_urls[0]

            if 'title' in update_data:
                base_slug = slugify(update_data['title'])
                slug = base_slug
                while portfolio_collection.find_one({'slug': slug, '_id': {'$ne': ObjectId(project_id)}}):
                    slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
                update_data['slug'] = slug
            
            result = portfolio_collection.update_one({'_id': ObjectId(project_id)}, {'$set': update_data})
            
            return JsonResponse({'message': 'Проект успешно обновлен'})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": f"Внутренняя ошибка сервера: {str(e)}"}, status=500)
            
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)



def get_portfolio_projects(request):
    if request.method == 'GET':
        try:
            projects = list(portfolio_collection.find({}).sort('date_completed', -1))
            for p in projects:
                p['_id'] = str(p['_id'])
            return JsonResponse(projects, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def delete_portfolio_project(request, project_id):
    if request.method == 'DELETE':
        try:
            result = portfolio_collection.delete_one({'_id': ObjectId(project_id)})
            if result.deleted_count > 0:
                return JsonResponse({'message': 'Проект удален'})
            return JsonResponse({'error': 'Проект не найден'}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def public_get_portfolio_detail(request, slug):
    if request.method == 'GET':
        try:
            project = portfolio_collection.find_one({'slug': slug})
            if not project:
                return JsonResponse({'error': 'Проект не найден'}, status=404)
            project['_id'] = str(project['_id'])
            return JsonResponse(project)
        except Exception as e:
            return JsonResponse({"error": "Проект не найден"}, status=404)
        

# === НОВЫЕ ФУНКЦИИ ДЛЯ СТРАНИЦЫ "О НАС" ===

# === ФУНКЦИИ ДЛЯ СТРАНИЦЫ "О НАС" (ВЕРСИЯ 2.1 - с иконками) ===

def get_about_us_page(request):
    """
    Публичный эндпоинт для получения СТРУКТУРИРОВАННОГО контента страницы "О нас".
    """
    if request.method == 'GET':
        try:
            page_data = pages_collection.find_one({'key': 'about_us'})
            
            # --- ИЗМЕНЕНИЕ: Добавили поле 'icon' в структуру по умолчанию ---
            default_content = {
                "founder_photo_url": "",
                "founder_quote": "",
                "founder_name": "",
                "values": [
                    {"icon": "🔬", "title": "", "text": ""},
                    {"icon": "🏆", "title": "", "text": ""},
                    {"icon": "🤝", "title": "", "text": ""}
                ],
                "studio_photo_url": ""
            }

            if not page_data:
                return JsonResponse(default_content)
            
            # Умное слияние: если в базе данных нет иконок, добавляем их из default_content
            content = page_data.get('content', {})
            for i in range(3):
                if 'icon' not in content.get('values', [])[i]:
                    content['values'][i]['icon'] = default_content['values'][i]['icon']

            return JsonResponse(content)
            
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def update_about_us_page(request):
    """
    Эндпоинт для админки, чтобы сохранять СТРУКТУРИРОВАННЫЙ контент и ИЗОБРАЖЕНИЯ.
    Теперь работает с multipart/form-data.
    """
    if request.method == 'POST':
        try:
            data = request.POST
            files = request.FILES
            
            existing_page = pages_collection.find_one({'key': 'about_us'})
            existing_content = existing_page.get('content', {}) if existing_page else {}

            values = []
            for i in range(3):
                # --- ИЗМЕНЕНИЕ: Добавили считывание иконки ---
                values.append({
                    "icon": data.get(f'values[{i}][icon]', '✨'), # '✨' - как запасной вариант
                    "title": data.get(f'values[{i}][title]', ''),
                    "text": data.get(f'values[{i}][text]', '')
                })

            data_to_save = {
                "founder_quote": data.get('founder_quote', ''),
                "founder_name": data.get('founder_name', ''),
                "values": values,
            }

            # --- ОБРАБОТКА ИЗОБРАЖЕНИЙ (без изменений) ---
            if 'founder_photo' in files:
                image = files['founder_photo']
                file_name = f"founder_{uuid.uuid4().hex}.{image.name.split('.')[-1]}"
                file_path = os.path.join('pages', file_name)
                saved_path = default_storage.save(file_path, image)
                data_to_save['founder_photo_url'] = default_storage.url(saved_path)
            else:
                data_to_save['founder_photo_url'] = existing_content.get('founder_photo_url', '')

            if 'studio_photo' in files:
                image = files['studio_photo']
                file_name = f"studio_{uuid.uuid4().hex}.{image.name.split('.')[-1]}"
                file_path = os.path.join('pages', file_name)
                saved_path = default_storage.save(file_path, image)
                data_to_save['studio_photo_url'] = default_storage.url(saved_path)
            else:
                data_to_save['studio_photo_url'] = existing_content.get('studio_photo_url', '')

            pages_collection.update_one(
                {'key': 'about_us'},
                {'$set': {'content': data_to_save}},
                upsert=True
            )
            
            return JsonResponse({'message': 'Страница "О нас" успешно обновлена'})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)
        
        # --- 10. ФУНКЦИИ ДЛЯ БЛОГА ---

@csrf_exempt
def create_blog_post(request):
    """
    Создает новую статью в блоге. Работает с multipart/form-data.
    """
    if request.method == 'POST':
        try:
            data = request.POST
            main_image = request.FILES.get('main_image')

            # --- Валидация ---
            if not all(k in data for k in ['title', 'content', 'status', 'author_name']) or not main_image:
                return JsonResponse({"error": "Требуются: Заголовок, Контент, Статус, Имя автора и Главное изображение"}, status=400)

            # --- Сохранение изображения ---
            image_folder = os.path.join('blog', str(uuid.uuid4()))
            file_name = f"{uuid.uuid4().hex}_{main_image.name}"
            file_path = os.path.join(image_folder, file_name)
            saved_path = default_storage.save(file_path, main_image)
            image_url = default_storage.url(saved_path)

            # --- Генерация слага ---
            base_slug = slugify(data['title'])
            slug = base_slug
            while blog_posts_collection.find_one({'slug': slug}):
                slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"

            # --- Создание документа ---
            new_post = {
                'title': data['title'],
                'slug': slug,
                'main_image_url': image_url,
                'content': data['content'],
                'author_name': data['author_name'],
                'status': data['status'], # "published" или "draft"
                'tags': [tag.strip() for tag in data.get('tags', '').split(',') if tag.strip()], # ['тег1', 'тег2']
                'created_at': datetime.now(timezone.utc)
            }
            result = blog_posts_collection.insert_one(new_post)
            return JsonResponse({"message": "Статья успешно создана", "_id": str(result.inserted_id)}, status=201)
        
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def update_blog_post(request, post_id):
    """
    Обновляет существующую статью. Также работает с multipart/form-data.
    """
    if request.method == 'POST':
        try:
            data = request.POST
            new_image = request.FILES.get('main_image')
            
            update_data = {}
            for key in ['title', 'content', 'status', 'author_name']:
                if key in data:
                    update_data[key] = data[key]
            
            if 'tags' in data:
                update_data['tags'] = [tag.strip() for tag in data.get('tags', '').split(',') if tag.strip()]

            # --- Обновление изображения, если оно было загружено ---
            if new_image:
                image_folder = os.path.join('blog', str(uuid.uuid4()))
                file_name = f"{uuid.uuid4().hex}_{new_image.name}"
                file_path = os.path.join(image_folder, file_name)
                saved_path = default_storage.save(file_path, new_image)
                update_data['main_image_url'] = default_storage.url(saved_path)

            # --- Обновление слага, если заголовок изменился ---
            if 'title' in update_data:
                base_slug = slugify(update_data['title'])
                slug = base_slug
                while blog_posts_collection.find_one({'slug': slug, '_id': {'$ne': ObjectId(post_id)}}):
                    slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
                update_data['slug'] = slug
            
            result = blog_posts_collection.update_one({'_id': ObjectId(post_id)}, {'$set': update_data})
            
            if result.modified_count > 0:
                return JsonResponse({'message': 'Статья успешно обновлена'})
            return JsonResponse({'message': 'Данные не изменились'})

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": f"Внутренняя ошибка сервера: {str(e)}"}, status=500)

@csrf_exempt
def delete_blog_post(request, post_id):
    """
    Удаляет статью.
    """
    if request.method == 'DELETE':
        try:
            result = blog_posts_collection.delete_one({'_id': ObjectId(post_id)})
            if result.deleted_count > 0:
                return JsonResponse({'message': 'Статья удалена'})
            return JsonResponse({'error': 'Статья не найдена'}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def get_blog_posts(request):
    """
    Возвращает ВСЕ статьи для админ-панели.
    """
    if request.method == 'GET':
        try:
            posts = list(blog_posts_collection.find({}).sort('created_at', -1))
            for p in posts:
                p['_id'] = str(p['_id'])
                # Преобразуем дату для удобного отображения
                if 'created_at' in p and isinstance(p['created_at'], datetime):
                    p['created_at'] = p['created_at'].isoformat()
            return JsonResponse(posts, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def public_get_blog_posts(request):
    """
    Возвращает ОПУБЛИКОВАННЫЕ статьи для публичного сайта.
    """
    if request.method == 'GET':
        try:
            # Важный фильтр: {'status': 'published'}
            posts = list(blog_posts_collection.find({'status': 'published'}).sort('created_at', -1))
            for p in posts:
                p['_id'] = str(p['_id'])
                if 'created_at' in p and isinstance(p['created_at'], datetime):
                    p['created_at'] = p['created_at'].isoformat()
            return JsonResponse(posts, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def public_get_blog_post_detail(request, slug):
    """
    Возвращает одну ОПУБЛИКОВАННУЮ статью по ее slug.
    """
    if request.method == 'GET':
        try:
            # Ищем только среди опубликованных
            post = blog_posts_collection.find_one({'slug': slug, 'status': 'published'})
            if not post:
                return JsonResponse({'error': 'Статья не найдена'}, status=404)
            post['_id'] = str(post['_id'])
            if 'created_at' in post and isinstance(post['created_at'], datetime):
                post['created_at'] = post['created_at'].isoformat()
            return JsonResponse(post)
        except Exception as e:
            return JsonResponse({"error": "Статья не найдена или произошла ошибка"}, status=404)