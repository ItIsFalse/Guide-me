import requests
import json
from datetime import datetime

BASE_URL = "https://guide-me-api.onrender.com"

# Админские данные
ADMIN_EMAIL = "admin@guideme.com"
ADMIN_PASSWORD = "superpuperadmin"

# Сохраняем токен
access_token = None

# Список для отчёта
report = []


def log(message, status="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    report.append(f"[{timestamp}] {status}: {message}")
    print(f"[{timestamp}] {status}: {message}")


def check_endpoint(method, url, description, expected_status=200, data=None, headers=None, requires_auth=False):
    """Проверяет один эндпоинт."""
    full_url = f"{BASE_URL}{url}"
    log(f"🔄 {method} {url} - {description}", "TEST")

    try:
        if method == "GET":
            response = requests.get(full_url, headers=headers or {})
        elif method == "POST":
            response = requests.post(full_url, json=data, headers=headers or {})
        elif method == "PUT":
            response = requests.put(full_url, json=data, headers=headers or {})
        elif method == "DELETE":
            response = requests.delete(full_url, headers=headers or {})
        elif method == "PATCH":
            response = requests.patch(full_url, json=data, headers=headers or {})
        else:
            log(f"❌ Неизвестный метод {method}", "ERROR")
            return

        status = response.status_code
        if status == expected_status:
            log(f"✅ {method} {url} → {status} (OK)", "PASS")
        else:
            log(f"❌ {method} {url} → {status} (ожидался {expected_status})", "FAIL")
            if status == 401:
                log(f"   🔐 Требуется авторизация (токен не передан или невалидный)", "INFO")
            if status == 404:
                log(f"   🔍 Эндпоинт не найден (возможно, не создан или не зарегистрирован)", "INFO")
            if status == 500:
                log(f"   💥 Внутренняя ошибка сервера", "ERROR")
        return response
    except requests.exceptions.ConnectionError:
        log(f"❌ {method} {url} → Ошибка подключения (сервер не отвечает)", "FAIL")
    except Exception as e:
        log(f"❌ {method} {url} → Ошибка: {str(e)}", "ERROR")


# ==================== ШАГ 1: ЛОГИН ====================
log("🚀 Начинаем тестирование API...", "START")

# Логин
login_response = check_endpoint(
    "POST",
    "/api/v1/auth/login",
    "Логин админа",
    expected_status=200,
    data={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
)

if login_response and login_response.status_code == 200:
    try:
        access_token = login_response.json().get("data", {}).get("access_token")
        if access_token:
            log(f"✅ Токен получен: {access_token[:30]}...", "PASS")
        else:
            log("❌ Токен не найден в ответе", "FAIL")
    except:
        log("❌ Не удалось разобрать ответ логина", "FAIL")

headers_admin = {"Authorization": f"Bearer {access_token}"} if access_token else {}


# ==================== ШАГ 2: ПУБЛИЧНЫЕ ЭНДПОИНТЫ ====================
log("📋 Проверка публичных эндпоинтов...", "TEST")

public_endpoints = [
    {"method": "GET", "url": "/", "desc": "Root"},
    {"method": "GET", "url": "/api/v1/regions/", "desc": "Список регионов"},
    {"method": "GET", "url": "/api/v1/regions/1", "desc": "Регион по ID"},
    {"method": "GET", "url": "/api/v1/properties/", "desc": "Список свойств"},
    {"method": "GET", "url": "/api/v1/properties/1", "desc": "Свойство по ID"},
    {"method": "GET", "url": "/api/v1/properties/1/nearby", "desc": "Ближайшие свойства"},
    {"method": "GET", "url": "/api/v1/properties/1/hotels", "desc": "Отели свойства"},
    {"method": "GET", "url": "/api/v1/tours/", "desc": "Список туров"},
    {"method": "GET", "url": "/api/v1/tours/1", "desc": "Тур по ID"},
    {"method": "GET", "url": "/api/v1/tours/1/navigation", "desc": "Навигация тура"},
    {"method": "GET", "url": "/api/v1/tours/averages/regions", "desc": "Средние траты по регионам"},
    {"method": "GET", "url": "/api/v1/reviews/property/1", "desc": "Отзывы свойства"},
    {"method": "GET", "url": "/api/v1/exchange/", "desc": "Курсы валют"},
    {"method": "GET", "url": "/api/v1/promo/validate?code=GUIDEME", "desc": "Проверка промокода"},
    {"method": "GET", "url": "/api/v1/photos/property/1", "desc": "Фото свойства"},
]

for ep in public_endpoints:
    check_endpoint(ep["method"], ep["url"], ep["desc"])


# ==================== ШАГ 3: ЗАЩИЩЁННЫЕ ЭНДПОИНТЫ (ТРЕБУЮТ ТОКЕН) ====================
log("🔐 Проверка защищённых эндпоинтов (с токеном)...", "TEST")

protected_endpoints = [
    {"method": "GET", "url": "/api/v1/auth/me", "desc": "Профиль пользователя"},
    {"method": "PUT", "url": "/api/v1/auth/me", "data": {"name": "Test"}, "desc": "Обновить профиль"},
    {"method": "POST", "url": "/api/v1/auth/change-password", "data": {"current_password": "superpuperadmin", "new_password": "NewPass123!"}, "desc": "Смена пароля"},
    {"method": "POST", "url": "/api/v1/auth/refresh", "data": {"refresh_token": "test"}, "desc": "Обновление токена (тест)"},
    {"method": "GET", "url": "/api/v1/booking/", "desc": "Мои брони"},
    {"method": "GET", "url": "/api/v1/booking/my", "desc": "Мои брони (алиас)"},
    {"method": "GET", "url": "/api/v1/saved/", "desc": "Сохранённое"},
    {"method": "POST", "url": "/api/v1/saved/?item_type=property&item_id=1", "desc": "Сохранить свойство (тест)", "expected_status": 400},
    {"method": "GET", "url": "/api/v1/reviews/my", "desc": "Мои отзывы"},
    {"method": "GET", "url": "/api/v1/users/me", "desc": "Профиль (users/me)"},
    {"method": "GET", "url": "/api/v1/users/me/stats", "desc": "Статистика пользователя"},
    {"method": "GET", "url": "/api/v1/notifications/", "desc": "Уведомления"},
    {"method": "POST", "url": "/api/v1/tours/expenses", "data": {"total_spent": 100}, "desc": "Добавить расходы"},
    {"method": "POST", "url": "/api/v1/tours/1/book", "data": {"transport_type": "car", "duration_days": 1}, "desc": "Забронировать тур"},
    {"method": "GET", "url": "/api/v1/tours/active", "desc": "Активный тур"},
]

for ep in protected_endpoints:
    check_endpoint(
        ep["method"],
        ep["url"],
        ep["desc"],
        expected_status=ep.get("expected_status", 200),
        data=ep.get("data"),
        headers=headers_admin
    )


# ==================== ШАГ 4: СПЕЦИАЛЬНЫЕ ЭНДПОИНТЫ (нестандартные) ====================
log("🧪 Проверка специальных эндпоинтов...", "TEST")

# POST /api/v1/ai/ (AI Chat)
check_endpoint(
    "POST",
    "/api/v1/ai/",
    "AI Chat (с тестовым сообщением)",
    expected_status=200,
    data={"message": "Привет, что посмотреть в Ташкенте?"},
    headers=headers_admin
)

# POST /api/v1/booking/ (создание брони)
check_endpoint(
    "POST",
    "/api/v1/booking/",
    "Создание брони",
    expected_status=200,
    data={"property_id": 1, "check_in_date": "2026-07-01", "check_out_date": "2026-07-05"},
    headers=headers_admin
)

# POST /api/v1/reviews/ (отзыв)
check_endpoint(
    "POST",
    "/api/v1/reviews/",
    "Создание отзыва",
    expected_status=200,
    data={"property_id": 1, "rating": 5, "text_en": "Great place!"},
    headers=headers_admin
)

# POST /api/v1/chat/ (сообщение)
check_endpoint(
    "POST",
    "/api/v1/chat/",
    "Отправить сообщение",
    expected_status=200,
    data={"property_id": 1, "message": "Hello!"},
    headers=headers_admin
)

# POST /api/v1/navigation/route
check_endpoint(
    "POST",
    "/api/v1/navigation/route",
    "Построить маршрут",
    expected_status=200,
    data={"property_id": 1, "user_lat": 41.3112, "user_lon": 69.2797},
    headers=headers_admin
)


# ==================== ИТОГ ====================
log("✅ Тестирование завершено!", "DONE")
log(f"📊 Всего проверок: {len(report) - 2}", "INFO")

# Сохраняем отчёт в файл
with open("test_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(report))

print("\n📄 Отчёт сохранён в файл test_report.txt")