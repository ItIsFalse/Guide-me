"""
Заполняет базу тестовыми данными: 12 областей Узбекистана + отели, музеи, рестораны + теги + тур-пакеты.
Запуск: python -m scripts.seed_data
"""
import sys

sys.path.insert(0, ".")

from app.core.database import SessionLocal, init_db
from app.models.region import Region
from app.models.property import Property
from app.models.property_unit import PropertyUnit
from app.models.property_tag import PropertyTag
from app.models.tour import Tour, TourStop
from app.models.promo_code import PromoCode
from app.models.tour_booking import TourBooking
from app.models.booking import BookingRequest
from app.models.notification import Notification
from app.models.chat import ChatMessage
from app.models.review import Review
from app.models.saved import SavedItem
from app.models.photo import Photo
from app.models.tour import UserTourExpense
from app.models.exchange_rate import ExchangeRate

REGIONS_DATA = [
    {"name_en": "Andijan", "name_uz": "Andijon", "name_ru": "Андижан", "lat": 40.78, "lon": 72.34,
     "best_season": "Spring, Autumn", "description": "Industrial and cultural center of Fergana Valley"},
    {"name_en": "Bukhara", "name_uz": "Buxoro", "name_ru": "Бухара", "lat": 39.77, "lon": 64.42,
     "best_season": "Spring, Autumn",
     "description": "Ancient city on the Silk Road with stunning Islamic architecture"},
    {"name_en": "Jizzakh", "name_uz": "Jizzax", "name_ru": "Джизак", "lat": 40.12, "lon": 67.84,
     "best_season": "Spring, Summer", "description": "Gateway to Samarkand, known for Aydarkul Lake"},
    {"name_en": "Kashkadarya", "name_uz": "Qashqadaryo", "name_ru": "Кашкадарья", "lat": 38.85, "lon": 65.79,
     "best_season": "Spring, Autumn", "description": "Home to Shakhrisabz, birthplace of Amir Timur"},
    {"name_en": "Navoiy", "name_uz": "Navoiy", "name_ru": "Навои", "lat": 40.08, "lon": 65.38,
     "best_season": "Spring, Autumn", "description": "Region of deserts and ancient caravanserais"},
    {"name_en": "Namangan", "name_uz": "Namangan", "name_ru": "Наманган", "lat": 40.99, "lon": 71.67,
     "best_season": "Spring, Summer", "description": "Famous for gardens, flowers and the beautiful Chartak Reservoir"},
    {"name_en": "Samarkand", "name_uz": "Samarqand", "name_ru": "Самарканд", "lat": 39.65, "lon": 66.97,
     "best_season": "Spring, Autumn",
     "description": "Crossroads of cultures, Registan Square and centuries of history"},
    {"name_en": "Surkhandarya", "name_uz": "Surxondaryo", "name_ru": "Сурхандарья", "lat": 37.22, "lon": 67.28,
     "best_season": "Spring, Autumn", "description": "Southernmost region with unique Buddhist heritage"},
    {"name_en": "Syrdarya", "name_uz": "Sirdaryo", "name_ru": "Сырдарья", "lat": 40.42, "lon": 68.67,
     "best_season": "Spring, Summer", "description": "Fertile lands along the Syr Darya river"},
    {"name_en": "Tashkent", "name_uz": "Toshkent", "name_ru": "Ташкент", "lat": 41.30, "lon": 69.24,
     "best_season": "Spring, Autumn", "description": "Modern capital blending Soviet legacy with Islamic heritage"},
    {"name_en": "Fergana", "name_uz": "Farg'ona", "name_ru": "Фергана", "lat": 40.39, "lon": 71.78,
     "best_season": "Spring, Summer", "description": "Heart of Fergana Valley, silk and ceramics center"},
    {"name_en": "Khorezm", "name_uz": "Xorazm", "name_ru": "Хорезм", "lat": 41.38, "lon": 60.36,
     "best_season": "Spring, Autumn", "description": "Ancient Khiva, desert fortresses and unique culture"},
]

PROPERTIES_BY_REGION = {
    "Tashkent": [
        {"type": "hotel", "name_en": "Hyatt Regency Tashkent", "name_uz": "Hyatt Regency Toshkent",
         "name_ru": "Hyatt Regency Ташкент", "star": 5, "price": 1200000, "lat": 41.3164, "lon": 69.2780,
         "desc": "Luxury 5-star hotel in the business center of Tashkent with pool and spa",
         "tags": ["hotel", "luxury", "pool", "spa", "business", "5star"]},
        {"type": "hotel", "name_en": "International Hotel Tashkent", "name_uz": "International Hotel Toshkent",
         "name_ru": "International Hotel Ташкент", "star": 4, "price": 800000, "lat": 41.3375, "lon": 69.2836,
         "desc": "Iconic hotel with panoramic city views, located in the city center",
         "tags": ["hotel", "business", "view", "center", "modern"]},
        {"type": "hotel", "name_en": "Miran International Hotel", "name_uz": "Miran International mehmonxonasi",
         "name_ru": "Miran International Отель", "star": 5, "price": 950000, "lat": 41.3038, "lon": 69.2839,
         "desc": "Modern luxury hotel with traditional Uzbek hospitality, near Amir Timur Square",
         "tags": ["hotel", "luxury", "modern", "uzbek", "center"]},
        {"type": "hotel", "name_en": "Shodlik Palace Hotel", "name_uz": "Shodlik Palace mehmonxonasi",
         "name_ru": "Shodlik Palace Отель", "star": 3, "price": 350000, "lat": 41.3112, "lon": 69.2798,
         "desc": "Affordable comfort in the heart of old Tashkent", "tags": ["hotel", "budget", "center", "cozy"]},
        {"type": "hotel", "name_en": "Grand Mir Hotel", "name_uz": "Grand Mir mehmonxonasi",
         "name_ru": "Grand Mir Отель", "star": 4, "price": 650000, "lat": 41.3005, "lon": 69.2401,
         "desc": "Spacious rooms with traditional decor, near Broadway street",
         "tags": ["hotel", "traditional", "spacious", "modern"]},
        {"type": "museum", "name_en": "Amir Timur Museum", "name_uz": "Amir Temur muzeyi",
         "name_ru": "Музей Амира Тимура", "price": 30000, "lat": 41.3135, "lon": 69.2789,
         "desc": "Blue-domed museum showcasing Timurid dynasty history and artifacts",
         "tags": ["museum", "history", "timur", "monument", "culture", "iconic"]},
        {"type": "museum", "name_en": "State Museum of History of Uzbekistan",
         "name_uz": "O'zbekiston tarixi davlat muzeyi", "name_ru": "Государственный музей истории Узбекистана",
         "price": 25000, "lat": 41.3115, "lon": 69.2801, "desc": "Oldest museum in Central Asia with 250,000+ exhibits",
         "tags": ["museum", "history", "ancient", "culture", "central asia"]},
        {"type": "museum", "name_en": "Museum of Applied Arts", "name_uz": "Amaliy san'at muzeyi",
         "name_ru": "Музей прикладного искусства", "price": 20000, "lat": 41.2983, "lon": 69.2689,
         "desc": "Beautifully decorated museum showcasing traditional Uzbek handicrafts",
         "tags": ["museum", "art", "craft", "traditional", "ceramics", "textiles"]},
        {"type": "museum", "name_en": "Khast Imam Complex", "name_uz": "Hazrati Imom majmuasi",
         "name_ru": "Комплекс Хазрати Имам", "price": 0, "lat": 41.3392, "lon": 69.2397,
         "desc": "Religious center of Tashkent housing the world's oldest Quran (7th century)",
         "tags": ["museum", "religious", "islamic", "history", "quran", "free"]},
        {"type": "museum", "name_en": "Tashkent Tower", "name_uz": "Toshkent teleminorasi",
         "name_ru": "Ташкентская телебашня", "price": 40000, "lat": 41.3469, "lon": 69.2843,
         "desc": "Tallest structure in Central Asia (375m) with observation deck",
         "tags": ["museum", "modern", "view", "tallest", "observation"]},
        {"type": "park", "name_en": "Alisher Navoi National Park", "name_uz": "Alisher Navoiy milliy bog'i",
         "name_ru": "Национальный парк Алишера Навои", "price": 0, "lat": 41.3040, "lon": 69.2410,
         "desc": "Large green park with lakes and monuments",
         "tags": ["park", "lake", "nature", "monument", "free", "family"]},
        {"type": "park", "name_en": "Tashkent Botanical Garden", "name_uz": "Toshkent botanika bog'i",
         "name_ru": "Ташкентский ботанический сад", "price": 15000, "lat": 41.3309, "lon": 69.2909,
         "desc": "65-hectare botanical garden with 4,500+ plant species",
         "tags": ["park", "nature", "garden", "plants", "family", "education"]},
        {"type": "park", "name_en": "Magic City Park", "name_uz": "Magic City parki", "name_ru": "Парк Magic City",
         "price": 50000, "lat": 41.2884, "lon": 69.2108, "desc": "Modern amusement park with rides and aquarium",
         "tags": ["park", "amusement", "family", "children", "rides", "modern"]},
        {"type": "restaurant", "name_en": "Afsona Restaurant", "name_uz": "Afsona restorani",
         "name_ru": "Ресторан Афсона", "cuisine": "Uzbek, International", "lat": 41.3150, "lon": 69.2770,
         "desc": "Fine dining with live traditional music",
         "tags": ["restaurant", "uzbek", "fine dining", "music", "luxury"]},
        {"type": "restaurant", "name_en": "Caravan Restaurant", "name_uz": "Caravan restorani",
         "name_ru": "Ресторан Караван", "cuisine": "Uzbek, European", "lat": 41.3105, "lon": 69.2725,
         "desc": "Popular restaurant with traditional decor, famous for pilaf",
         "tags": ["restaurant", "uzbek", "pilaf", "traditional", "popular"]},
        {"type": "shop", "name_en": "Chorsu Bazaar", "name_uz": "Chorsu bozori", "name_ru": "Рынок Чорсу",
         "lat": 41.3275, "lon": 69.2358, "desc": "The largest and oldest bazaar in Tashkent",
         "tags": ["shop", "bazaar", "market", "traditional", "food", "spices", "souvenir"]},
        {"type": "shop", "name_en": "Samarkand Darvoza", "name_uz": "Samarqand Darvoza savdo markazi",
         "name_ru": "Самарканд Дарвоза", "lat": 41.3050, "lon": 69.2520,
         "desc": "Modern shopping mall with food court and cinema",
         "tags": ["shop", "mall", "modern", "food court", "shopping"]},
        {"type": "shop", "name_en": "Next Mall", "name_uz": "Next Mall savdo markazi", "name_ru": "Next Mall",
         "lat": 41.3175, "lon": 69.2705, "desc": "Popular shopping center in the heart of Tashkent",
         "tags": ["shop", "mall", "modern", "center", "shopping", "boutique"]},
        {"type": "shop", "name_en": "Alay Bazaar", "name_uz": "Alay bozori", "name_ru": "Алайский базар",
         "lat": 41.3055, "lon": 69.2805, "desc": "Traditional market with national goods and souvenirs",
         "tags": ["shop", "bazaar", "market", "traditional", "souvenir", "food"]},
        {"type": "entertainment", "name_en": "Tashkent City Park", "name_uz": "Tashkent City parki",
         "name_ru": "Tashkent City Парк", "price": 0, "lat": 41.2905, "lon": 69.2855,
         "desc": "Modern amusement park with fountains and light shows",
         "tags": ["entertainment", "amusement", "park", "fountains", "modern", "family", "free"]},
        {"type": "entertainment", "name_en": "Aqua Park Tashkent", "name_uz": "Toshkent akvaparki",
         "name_ru": "Аквапарк Ташкент", "price": 80000, "lat": 41.2975, "lon": 69.2155,
         "desc": "Water park with pools and slides. Open seasonally May-September",
         "tags": ["entertainment", "waterpark", "pool", "slides", "family", "summer"]},
        {"type": "entertainment", "name_en": "Cinema Palace Alisher Navoi", "name_uz": "Alisher Navoiy kinosi",
         "name_ru": "Кинотеатр Алишер Навои", "price": 35000, "lat": 41.3185, "lon": 69.2655,
         "desc": "Largest cinema in Tashkent with multiple screens",
         "tags": ["entertainment", "cinema", "movies", "modern", "indoor"]},
        {"type": "entertainment", "name_en": "Ashgabat Park", "name_uz": "Ashgabat bog'i", "name_ru": "Парк Ашхабад",
         "price": 0, "lat": 41.3025, "lon": 69.2905, "desc": "Family amusement park with rides and carousels",
         "tags": ["entertainment", "amusement", "park", "rides", "family", "children", "free"]},
        {"type": "museum", "name_en": "Monument of Courage", "name_uz": "Jasorat monumenti",
         "name_ru": "Монумент Мужество", "price": 0, "lat": 41.3015, "lon": 69.2455,
         "desc": "Memorial to the 1966 Tashkent earthquake",
         "tags": ["museum", "monument", "history", "earthquake", "memorial", "free"]},
        {"type": "museum", "name_en": "Independence Monument", "name_uz": "Mustaqillik monumenti",
         "name_ru": "Монумент Независимости", "price": 0, "lat": 41.3115, "lon": 69.2809,
         "desc": "Tall monument with a golden globe on Independence Square",
         "tags": ["museum", "monument", "independence", "history", "golden", "free", "iconic"]},
        {"type": "museum", "name_en": "Museum of Victims of Repressions", "name_uz": "Qatag'on qurbonlari muzeyi",
         "name_ru": "Музей жертв репрессий", "price": 15000, "lat": 41.3195, "lon": 69.2325,
         "desc": "Museum dedicated to the memory of those who suffered",
         "tags": ["museum", "history", "repressions", "memory", "education"]},
        {"type": "museum", "name_en": "Railway Museum", "name_uz": "Temir yo'l muzeyi",
         "name_ru": "Музей железнодорожной техники", "price": 20000, "lat": 41.2855, "lon": 69.2005,
         "desc": "Open-air museum featuring historic locomotives",
         "tags": ["museum", "railway", "trains", "open-air", "technology", "history", "unique"]},
        {"type": "restaurant", "name_en": "Jumanji", "name_uz": "Jumanji restorani", "name_ru": "Ресторан Джуманджи",
         "cuisine": "Uzbek, Asian", "lat": 41.3095, "lon": 69.2815,
         "desc": "Popular chain restaurant with Asian fusion cuisine",
         "tags": ["restaurant", "uzbek", "asian", "sushi", "popular", "modern"]},
        {"type": "restaurant", "name_en": "The Irish Pub & Restaurant", "name_uz": "Irish Pub restorani",
         "name_ru": "Ирландский Паб", "cuisine": "European", "lat": 41.3165, "lon": 69.2745,
         "desc": "Authentic Irish pub with European cuisine and wide selection of beers",
         "tags": ["restaurant", "european", "pub", "beer", "international", "center"]},
        {"type": "restaurant", "name_en": "Beshqozon", "name_uz": "Beshqozon restorani", "name_ru": "Бешкозон",
         "cuisine": "Uzbek", "lat": 41.2945, "lon": 69.2605,
         "desc": "Famous pilaf center of Tashkent. Massive cauldrons of pilaf cooked daily",
         "tags": ["restaurant", "uzbek", "pilaf", "famous", "traditional", "authentic"]},
        {"type": "restaurant", "name_en": "Saffron Restaurant", "name_uz": "Saffron restorani",
         "name_ru": "Ресторан Саффрон", "cuisine": "Uzbek, International", "lat": 41.3125, "lon": 69.2765,
         "desc": "Premium restaurant offering refined Uzbek cuisine with international twists",
         "tags": ["restaurant", "uzbek", "international", "premium", "luxury", "elegant"]}
    ],
    "Andijan": [
        {"type": "hotel", "name_en": "Hotel Andijon", "name_uz": "Andijon mehmonxonasi", "name_ru": "Отель Андижан",
         "star": 3, "price": 280000, "lat": 40.7820, "lon": 72.3440,
         "desc": "Central hotel in Andijan with comfortable rooms", "tags": ["hotel", "center", "comfort", "budget"]},
        {"type": "hotel", "name_en": "Vella Hotel", "name_uz": "Vella mehmonxonasi", "name_ru": "Отель Велла",
         "star": 3, "price": 350000, "lat": 40.7850, "lon": 72.3410,
         "desc": "Modern hotel with free Wi-Fi and breakfast", "tags": ["hotel", "modern", "wifi", "breakfast"]},
        {"type": "hotel", "name_en": "Tashkent Hotel Andijan", "name_uz": "Toshkent mehmonxonasi Andijon",
         "name_ru": "Ташкент Отель Андижан", "star": 2, "price": 180000, "lat": 40.7810, "lon": 72.3480,
         "desc": "Budget-friendly hotel in the city center", "tags": ["hotel", "budget", "simple", "cheap"]},
        {"type": "museum", "name_en": "Babur Literary Museum", "name_uz": "Bobur adabiyot muzeyi",
         "name_ru": "Литературный музей Бабура", "price": 25000, "lat": 40.7800, "lon": 72.3500,
         "desc": "Dedicated to Zahiriddin Muhammad Babur",
         "tags": ["museum", "history", "literature", "babur", "culture"]},
        {"type": "museum", "name_en": "Andijan Regional Museum", "name_uz": "Andijon viloyat muzeyi",
         "name_ru": "Андижанский областной музей", "price": 15000, "lat": 40.7830, "lon": 72.3400,
         "desc": "Regional museum of Andijan region", "tags": ["museum", "history", "regional", "culture", "nature"]},
        {"type": "park", "name_en": "Babur Park", "name_uz": "Bobur bog'i", "name_ru": "Парк Бабура", "price": 0,
         "lat": 40.7780, "lon": 72.3520, "desc": "Large green park named after Babur",
         "tags": ["park", "green", "monument", "fountains", "walking", "free", "family"]},
        {"type": "park", "name_en": "Bogishamol Park", "name_uz": "Bog'ishamol bog'i", "name_ru": "Парк Богишамол",
         "price": 0, "lat": 40.7860, "lon": 72.3380, "desc": "Popular recreation park with rides and cafes",
         "tags": ["park", "recreation", "rides", "cafe", "garden", "free", "family"]},
        {"type": "restaurant", "name_en": "Andijon Osh Markazi", "name_uz": "Andijon osh markazi",
         "name_ru": "Андижанский Центр Плова", "cuisine": "Uzbek", "lat": 40.7870, "lon": 72.3420,
         "desc": "Authentic Andijan-style pilaf center",
         "tags": ["restaurant", "uzbek", "pilaf", "authentic", "local"]},
        {"type": "restaurant", "name_en": "Bogishamol Restaurant", "name_uz": "Bog'ishamol restorani",
         "name_ru": "Ресторан Богишамол", "cuisine": "Uzbek, European", "lat": 40.7840, "lon": 72.3350,
         "desc": "Garden restaurant with traditional and European dishes",
         "tags": ["restaurant", "uzbek", "european", "garden", "family"]},
        {"type": "shop", "name_en": "Andijan City Mall", "name_uz": "Andijon City Mall", "name_ru": "Андижан Сити Молл",
         "lat": 40.7815, "lon": 72.3390, "desc": "Modern shopping center with boutiques and food court",
         "tags": ["shop", "mall", "modern", "shopping", "food court"]},
        {"type": "entertainment", "name_en": "Andijan Amusement Park", "name_uz": "Andijon attraksionlar bog'i",
         "name_ru": "Андижанский парк аттракционов", "price": 20000, "lat": 40.7880, "lon": 72.3460,
         "desc": "Family amusement park with rides and ferris wheel",
         "tags": ["entertainment", "amusement", "park", "rides", "family", "children"]}
    ],
    "Bukhara": [
        {"type": "hotel", "name_en": "Lyabi House Hotel", "name_uz": "Lyabi House mehmonxonasi",
         "name_ru": "Отель Ляби Хаус", "star": 3, "price": 380000, "lat": 39.7730, "lon": 64.4210,
         "desc": "Historic boutique hotel near Lyabi-Hauz ensemble",
         "tags": ["hotel", "boutique", "historic", "old city", "center"]},
        {"type": "hotel", "name_en": "Komil Bukhara Boutique Hotel", "name_uz": "Komil Buxoro butik mehmonxonasi",
         "name_ru": "Бутик-отель Комил Бухара", "star": 3, "price": 420000, "lat": 39.7710, "lon": 64.4190,
         "desc": "Charming boutique hotel with traditional decor",
         "tags": ["hotel", "boutique", "traditional", "courtyard", "cozy"]},
        {"type": "hotel", "name_en": "Amulet Hotel", "name_uz": "Amulet mehmonxonasi", "name_ru": "Отель Амулет",
         "star": 2, "price": 250000, "lat": 39.7750, "lon": 64.4230, "desc": "Budget-friendly hotel in the old city",
         "tags": ["hotel", "budget", "authentic", "old city", "cheap"]},
        {"type": "museum", "name_en": "Ark Fortress", "name_uz": "Ark qal'asi", "name_ru": "Крепость Арк",
         "price": 40000, "lat": 39.7780, "lon": 64.4100, "desc": "Ancient citadel housing museums",
         "tags": ["museum", "fortress", "history", "ancient", "unesco", "iconic"]},
        {"type": "museum", "name_en": "Samanid Mausoleum", "name_uz": "Somoniylar maqbarasi",
         "name_ru": "Мавзолей Саманидов", "price": 0, "lat": 39.7770, "lon": 64.4000,
         "desc": "9th-century masterpiece of Islamic architecture",
         "tags": ["museum", "mausoleum", "architecture", "islamic", "ancient", "unesco", "free"]},
        {"type": "park", "name_en": "Samanid Park", "name_uz": "Somoniylar bog'i", "name_ru": "Парк Саманидов",
         "price": 0, "lat": 39.7760, "lon": 64.4010, "desc": "Green park around Samanid Mausoleum",
         "tags": ["park", "green", "fountains", "historic", "walking", "free"]},
        {"type": "restaurant", "name_en": "Minzifa Restaurant", "name_uz": "Minzifa restorani",
         "name_ru": "Ресторан Минзифа", "cuisine": "Uzbek, European", "lat": 39.7725, "lon": 64.4205,
         "desc": "Rooftop restaurant with panoramic Old City views",
         "tags": ["restaurant", "uzbek", "european", "rooftop", "view", "romantic"]},
        {"type": "restaurant", "name_en": "Old Bukhara Restaurant", "name_uz": "Old Bukhara restorani",
         "name_ru": "Ресторан Старая Бухара", "cuisine": "Uzbek", "lat": 39.7740, "lon": 64.4180,
         "desc": "Traditional restaurant with national cuisine",
         "tags": ["restaurant", "uzbek", "traditional", "music", "old city"]},
        {"type": "shop", "name_en": "Toki Sarrafon Bazaar", "name_uz": "Toki Sarrafon bozori",
         "name_ru": "Базар Токи Саррафон", "lat": 39.7745, "lon": 64.4195,
         "desc": "Ancient trading dome, market for carpets and souvenirs",
         "tags": ["shop", "bazaar", "historic", "carpets", "jewelry", "souvenir"]},
        {"type": "shop", "name_en": "Bukhara Craft Shop", "name_uz": "Buxoro hunarmandchilik do'koni",
         "name_ru": "Бухарская ремесленная лавка", "lat": 39.7705, "lon": 64.4175,
         "desc": "Handicraft shop with handmade ceramics",
         "tags": ["shop", "craft", "handmade", "ceramics", "textiles", "souvenir"]},
        {"type": "museum", "name_en": "Bolo Hauz Mosque", "name_uz": "Bolo Hovuz masjidi",
         "name_ru": "Мечеть Боло Хауз", "price": 0, "lat": 39.7785, "lon": 64.4075,
         "desc": "Beautiful 18th-century mosque with wooden pillars",
         "tags": ["museum", "mosque", "islamic", "architecture", "historic", "free"]}
    ],
    "Samarkand": [
        {"type": "hotel", "name_en": "Registon Saroy Hotel", "name_uz": "Registon Saroy mehmonxonasi",
         "name_ru": "Отель Регистон Сарой", "star": 4, "price": 550000, "lat": 39.6560, "lon": 66.9750,
         "desc": "Elegant hotel with Registan Square view",
         "tags": ["hotel", "luxury", "view", "registan", "center", "rooftop"]},
        {"type": "hotel", "name_en": "Dilimah Hotel", "name_uz": "Dilimah mehmonxonasi", "name_ru": "Отель Дилимах",
         "star": 3, "price": 320000, "lat": 39.6540, "lon": 66.9700,
         "desc": "Comfortable mid-range hotel near the city center",
         "tags": ["hotel", "comfort", "modern", "center", "mid-range"]},
        {"type": "hotel", "name_en": "Jahongir Hotel", "name_uz": "Jahongir mehmonxonasi", "name_ru": "Отель Джахонгир",
         "star": 2, "price": 200000, "lat": 39.6580, "lon": 66.9780,
         "desc": "Simple budget hotel within walking distance to Registan",
         "tags": ["hotel", "budget", "simple", "registan", "cheap"]},
        {"type": "museum", "name_en": "Registan Square", "name_uz": "Registon maydoni", "name_ru": "Площадь Регистан",
         "price": 65000, "lat": 39.6550, "lon": 66.9750, "desc": "Three magnificent madrasahs, UNESCO World Heritage",
         "tags": ["museum", "unesco", "architecture", "history", "madrasah", "iconic"]},
        {"type": "museum", "name_en": "Gur-e-Amir Mausoleum", "name_uz": "Go'ri Amir maqbarasi",
         "name_ru": "Мавзолей Гур-Эмир", "price": 30000, "lat": 39.6490, "lon": 66.9690,
         "desc": "Tomb of Amir Timur. Blue dome masterpiece",
         "tags": ["museum", "mausoleum", "timur", "history", "blue dome", "unesco"]},
        {"type": "park", "name_en": "Central Park Samarkand", "name_uz": "Samarqand markaziy bog'i",
         "name_ru": "Центральный парк Самарканда", "price": 0, "lat": 39.6520, "lon": 66.9600,
         "desc": "Large central park with monuments and fountains",
         "tags": ["park", "green", "monument", "fountains", "family", "free"]},
        {"type": "restaurant", "name_en": "Samarkand Pilaf Center", "name_uz": "Samarqand osh markazi",
         "name_ru": "Самаркандский Центр Плова", "cuisine": "Uzbek", "lat": 39.6575, "lon": 66.9735,
         "desc": "The best Samarkand pilaf", "tags": ["restaurant", "uzbek", "pilaf", "famous", "authentic"]},
        {"type": "restaurant", "name_en": "Karimbek Restaurant", "name_uz": "Karimbek restorani",
         "name_ru": "Ресторан Каримбек", "cuisine": "Uzbek", "lat": 39.6535, "lon": 66.9675,
         "desc": "Popular restaurant with traditional decor",
         "tags": ["restaurant", "uzbek", "traditional", "shashlik", "lagman"]},
        {"type": "shop", "name_en": "Siab Bazaar", "name_uz": "Siyob bozori", "name_ru": "Сиабский базар",
         "lat": 39.6600, "lon": 66.9850, "desc": "Largest market in Samarkand",
         "tags": ["shop", "bazaar", "market", "food", "souvenir", "traditional"]},
        {"type": "shop", "name_en": "Samarkand Silk Carpet Factory", "name_uz": "Samarqand ipak gilam fabrikasi",
         "name_ru": "Самаркандская фабрика шёлковых ковров", "lat": 39.6515, "lon": 66.9655,
         "desc": "Workshop with handwoven silk carpets",
         "tags": ["shop", "silk", "carpets", "handmade", "souvenir", "workshop"]},
        {"type": "museum", "name_en": "Shah-i-Zinda Necropolis", "name_uz": "Shohi Zinda nekropoli",
         "name_ru": "Некрополь Шахи-Зинда", "price": 25000, "lat": 39.6620, "lon": 66.9880,
         "desc": "Street of blue tombs, one of the most beautiful sights",
         "tags": ["museum", "necropolis", "tombs", "blue tiles", "history", "unesco", "photography"]}
    ],
    "Khorezm": [
        {"type": "hotel", "name_en": "Orient Star Khiva", "name_uz": "Orient Star Xiva",
         "name_ru": "Отель Ориент Стар Хива", "star": 4, "price": 480000, "lat": 41.3790, "lon": 60.3620,
         "desc": "Unique hotel inside Ichan-Kala walls",
         "tags": ["hotel", "historic", "unique", "madrasah", "inside walls", "authentic"]},
        {"type": "hotel", "name_en": "Malika Kheivak Hotel", "name_uz": "Malika Xeyvak mehmonxonasi",
         "name_ru": "Отель Малика Хейвак", "star": 3, "price": 300000, "lat": 41.3810, "lon": 60.3580,
         "desc": "Comfortable hotel near Ichan-Kala",
         "tags": ["hotel", "comfort", "national style", "modern", "near old city"]},
        {"type": "hotel", "name_en": "Arkanchi Hotel", "name_uz": "Arkanchi mehmonxonasi", "name_ru": "Отель Арканчи",
         "star": 2, "price": 200000, "lat": 41.3830, "lon": 60.3650,
         "desc": "Budget hotel, walking distance to old city",
         "tags": ["hotel", "budget", "simple", "old city", "cheap"]},
        {"type": "museum", "name_en": "Ichan-Kala Fortress", "name_uz": "Ichan-Qal'a qal'asi",
         "name_ru": "Крепость Ичан-Кала", "price": 100000, "lat": 41.3780, "lon": 60.3600,
         "desc": "UNESCO walled inner city of Khiva",
         "tags": ["museum", "unesco", "fortress", "history", "open-air", "walled city", "iconic"]},
        {"type": "museum", "name_en": "Kalta Minor Minaret", "name_uz": "Kalta Minor minorasi",
         "name_ru": "Минарет Кальта Минор", "price": 0, "lat": 41.3785, "lon": 60.3595,
         "desc": "Unfinished minaret with stunning blue tiles",
         "tags": ["museum", "minaret", "blue tiles", "iconic", "unfinished", "photography", "free"]},
        {"type": "park", "name_en": "Al-Khorezmi Park", "name_uz": "Al-Xorazmiy bog'i", "name_ru": "Парк Аль-Хорезми",
         "price": 0, "lat": 41.3820, "lon": 60.3550, "desc": "City park named after Al-Khorezmi",
         "tags": ["park", "monument", "green", "walking", "free"]},
        {"type": "restaurant", "name_en": "Khorezm Art Restaurant", "name_uz": "Xorazm san'at restorani",
         "name_ru": "Ресторан Хорезм Арт", "cuisine": "Uzbek, Khorezm", "lat": 41.3775, "lon": 60.3615,
         "desc": "Authentic Khorezm cuisine",
         "tags": ["restaurant", "uzbek", "khorezm", "local", "shivit osh", "authentic"]},
        {"type": "restaurant", "name_en": "Terrassa Restaurant", "name_uz": "Terrassa restorani",
         "name_ru": "Ресторан Террасса", "cuisine": "Uzbek, European", "lat": 41.3795, "lon": 60.3635,
         "desc": "Rooftop restaurant with panoramic view of Ichan-Kala",
         "tags": ["restaurant", "uzbek", "european", "rooftop", "view", "sunset"]},
        {"type": "shop", "name_en": "Ichan-Kala Bazaar", "name_uz": "Ichan-Qal'a bozori", "name_ru": "Базар Ичан-Кала",
         "lat": 41.3765, "lon": 60.3645, "desc": "Market inside the old city",
         "tags": ["shop", "bazaar", "craft", "handmade", "silk", "souvenir"]},
        {"type": "shop", "name_en": "Khiva Silk Workshop", "name_uz": "Xiva ipak ustaxonasi",
         "name_ru": "Хивинская шёлковая мастерская", "lat": 41.3805, "lon": 60.3615,
         "desc": "Workshop producing handmade silk carpets",
         "tags": ["shop", "silk", "carpets", "handmade", "workshop", "souvenir"]},
        {"type": "museum", "name_en": "Pakhlavan Mahmud Mausoleum", "name_uz": "Pahlavon Mahmud maqbarasi",
         "name_ru": "Мавзолей Пахлавана Махмуда", "price": 0, "lat": 41.3772, "lon": 60.3622,
         "desc": "Beautiful mausoleum of the patron saint of Khiva",
         "tags": ["museum", "mausoleum", "blue dome", "tiles", "religious", "free"]}
    ],
    "Fergana": [
        {"type": "hotel", "name_en": "Hotel Club 777", "name_uz": "Club 777 mehmonxonasi", "name_ru": "Отель Клуб 777",
         "star": 3, "price": 300000, "lat": 40.3850, "lon": 71.7860, "desc": "Modern hotel in Fergana city center",
         "tags": ["hotel", "modern", "center", "business"]},
        {"type": "hotel", "name_en": "Fergana Palace Hotel", "name_uz": "Farg'ona Palace mehmonxonasi",
         "name_ru": "Отель Фергана Палас", "star": 3, "price": 350000, "lat": 40.3880, "lon": 71.7820,
         "desc": "Comfortable hotel with pool and garden", "tags": ["hotel", "comfort", "pool", "garden", "center"]},
        {"type": "museum", "name_en": "Fergana Regional Museum", "name_uz": "Farg'ona viloyat muzeyi",
         "name_ru": "Ферганский областной музей", "price": 15000, "lat": 40.3860, "lon": 71.7880,
         "desc": "Regional museum of Fergana Valley", "tags": ["museum", "history", "regional", "culture", "nature"]},
        {"type": "museum", "name_en": "Ahmad Al-Fergani Monument", "name_uz": "Ahmad al-Farg'oniy monumenti",
         "name_ru": "Монумент Ахмада Аль-Фергани", "price": 0, "lat": 40.3840, "lon": 71.7850,
         "desc": "Monument to the great astronomer",
         "tags": ["museum", "monument", "astronomy", "history", "park", "free"]},
        {"type": "park", "name_en": "Fergana Central Park", "name_uz": "Farg'ona markaziy bog'i",
         "name_ru": "Центральный парк Ферганы", "price": 0, "lat": 40.3870, "lon": 71.7900,
         "desc": "Large central park with fountains",
         "tags": ["park", "green", "fountains", "walking", "family", "free"]},
        {"type": "restaurant", "name_en": "Fergana Pilaf Center", "name_uz": "Farg'ona osh markazi",
         "name_ru": "Ферганский Центр Плова", "cuisine": "Uzbek", "lat": 40.3890, "lon": 71.7840,
         "desc": "Authentic Fergana-style pilaf", "tags": ["restaurant", "uzbek", "pilaf", "authentic", "local"]},
        {"type": "restaurant", "name_en": "Ziyorat Restaurant", "name_uz": "Ziyorat restorani",
         "name_ru": "Ресторан Зиёрат", "cuisine": "Uzbek, European", "lat": 40.3820, "lon": 71.7890,
         "desc": "Popular restaurant with garden seating",
         "tags": ["restaurant", "uzbek", "european", "garden", "family"]},
        {"type": "shop", "name_en": "Fergana Bazaar", "name_uz": "Farg'ona bozori", "name_ru": "Ферганский базар",
         "lat": 40.3900, "lon": 71.7920, "desc": "Traditional market with fresh produce",
         "tags": ["shop", "bazaar", "market", "textiles", "local"]},
        {"type": "shop", "name_en": "Margilan Silk Factory Shop", "name_uz": "Marg'ilon ipak fabrikasi do'koni",
         "name_ru": "Маргиланский магазин шёлка", "lat": 40.3910, "lon": 71.7940,
         "desc": "Shop at the famous Margilan silk factory",
         "tags": ["shop", "silk", "factory", "handmade", "textiles", "souvenir"]}
    ],
    "Namangan": [
        {"type": "hotel", "name_en": "Hotel Namangan", "name_uz": "Namangan mehmonxonasi", "name_ru": "Отель Наманган",
         "star": 3, "price": 250000, "lat": 40.9950, "lon": 71.6720, "desc": "Central hotel with comfortable rooms",
         "tags": ["hotel", "center", "comfort", "breakfast", "budget"]},
        {"type": "hotel", "name_en": "Sardoba Hotel", "name_uz": "Sardoba mehmonxonasi", "name_ru": "Отель Сардоба",
         "star": 2, "price": 180000, "lat": 40.9920, "lon": 71.6680,
         "desc": "Budget-friendly hotel near the city center",
         "tags": ["hotel", "budget", "simple", "center", "cheap"]},
        {"type": "museum", "name_en": "Namangan Regional Museum", "name_uz": "Namangan viloyat muzeyi",
         "name_ru": "Наманганский областной музей", "price": 15000, "lat": 40.9970, "lon": 71.6750,
         "desc": "Regional museum with archaeological finds",
         "tags": ["museum", "history", "regional", "archaeology", "crafts"]},
        {"type": "museum", "name_en": "Mullah Kyrgyz Madrasah", "name_uz": "Mulla Qirg'iz madrasasi",
         "name_ru": "Медресе Муллы Кыргыза", "price": 0, "lat": 40.9980, "lon": 71.6700,
         "desc": "19th-century madrasah named after a local poet",
         "tags": ["museum", "madrasah", "islamic", "architecture", "historic", "free"]},
        {"type": "park", "name_en": "Babur Park Namangan", "name_uz": "Bobur bog'i Namangan",
         "name_ru": "Парк Бабура Наманган", "price": 0, "lat": 40.9960, "lon": 71.6780,
         "desc": "Large recreation park with monuments",
         "tags": ["park", "recreation", "monument", "garden", "walking", "free", "family"]},
        {"type": "park", "name_en": "Afsonalar Bogi Namangan", "name_uz": "Afsonalar bog'i Namangan",
         "name_ru": "Парк Афсоналар Наманган", "price": 20000, "lat": 40.9930, "lon": 71.6650,
         "desc": "Legends Park — family amusement park",
         "tags": ["park", "amusement", "family", "children", "rides", "entertainment"]},
        {"type": "restaurant", "name_en": "Oltin Vodiy Restaurant", "name_uz": "Oltin Vodiy restorani",
         "name_ru": "Ресторан Олтин Водий", "cuisine": "Uzbek", "lat": 40.9990, "lon": 71.6730,
         "desc": "Traditional Uzbek cuisine", "tags": ["restaurant", "uzbek", "traditional", "garden", "national"]},
        {"type": "shop", "name_en": "Namangan Bazaar", "name_uz": "Namangan bozori", "name_ru": "Наманганский базар",
         "lat": 41.0000, "lon": 71.6770, "desc": "Traditional market famous for Namangan apples",
         "tags": ["shop", "bazaar", "market", "apples", "textiles", "local"]}
    ],
    "Jizzakh": [
        {"type": "hotel", "name_en": "Jizzakh Plaza Hotel", "name_uz": "Jizzax Plaza mehmonxonasi",
         "name_ru": "Отель Джизак Плаза", "star": 3, "price": 220000, "lat": 40.1230, "lon": 67.8420,
         "desc": "Modern hotel in Jizzakh city center", "tags": ["hotel", "modern", "center", "business"]},
        {"type": "hotel", "name_en": "Jizzakh Central Hotel", "name_uz": "Jizzax markaziy mehmonxonasi",
         "name_ru": "Отель Джизак Централ", "star": 2, "price": 180000, "lat": 40.1200, "lon": 67.8400,
         "desc": "Simple hotel in the city center", "tags": ["hotel", "budget", "center", "simple"]},
        {"type": "museum", "name_en": "Jizzakh Regional Museum", "name_uz": "Jizzax viloyat muzeyi",
         "name_ru": "Джизакский областной музей", "price": 10000, "lat": 40.1250, "lon": 67.8400,
         "desc": "Museum of history and culture", "tags": ["museum", "history", "regional", "archaeology"]},
        {"type": "park", "name_en": "Aydarkul Lake", "name_uz": "Aydarko'l ko'li", "name_ru": "Озеро Айдаркуль",
         "price": 0, "lat": 40.3500, "lon": 67.2000, "desc": "Vast lake in the desert with yurt camping",
         "tags": ["park", "lake", "desert", "camping", "fishing", "yurt", "free", "nature"]},
        {"type": "restaurant", "name_en": "Jizzakh Samsa Center", "name_uz": "Jizzax somsa markazi",
         "name_ru": "Джизакский Центр Самсы", "cuisine": "Uzbek", "lat": 40.1220, "lon": 67.8450,
         "desc": "Famous for huge Jizzakh-style samsa",
         "tags": ["restaurant", "uzbek", "samsa", "local", "famous", "tandoor"]},
        {"type": "shop", "name_en": "Jizzakh Bazaar", "name_uz": "Jizzax bozori", "name_ru": "Джизакский базар",
         "lat": 40.1240, "lon": 67.8440, "desc": "Local market with fresh produce",
         "tags": ["shop", "bazaar", "market", "local", "food"]},
        {"type": "entertainment", "name_en": "Zomin Mountain Resort", "name_uz": "Zomin tog' kurorti",
         "name_ru": "Горный курорт Заамин", "price": 30000, "lat": 39.6300, "lon": 68.5100,
         "desc": "Mountain resort with hiking trails",
         "tags": ["entertainment", "resort", "mountains", "hiking", "nature", "forest"]}
    ],
    "Navoiy": [
        {"type": "hotel", "name_en": "Navoiy Hotel", "name_uz": "Navoiy mehmonxonasi", "name_ru": "Отель Навои",
         "star": 3, "price": 200000, "lat": 40.0840, "lon": 65.3790, "desc": "Comfortable hotel in Navoiy city center",
         "tags": ["hotel", "center", "comfort", "wifi"]},
        {"type": "hotel", "name_en": "Navoiy Ota Hotel", "name_uz": "Navoiy Ota mehmonxonasi",
         "name_ru": "Отель Навои Ота", "star": 2, "price": 160000, "lat": 40.0860, "lon": 65.3800,
         "desc": "Budget hotel near the city center", "tags": ["hotel", "budget", "simple", "center"]},
        {"type": "museum", "name_en": "Sarmishsay Petroglyphs", "name_uz": "Sarmishsoy petrogliflari",
         "name_ru": "Петроглифы Сармишсай", "price": 35000, "lat": 40.2000, "lon": 65.3500,
         "desc": "Ancient rock carvings with over 4000 petroglyphs",
         "tags": ["museum", "petroglyphs", "ancient", "history", "gorge", "unique", "unesco tentative"]},
        {"type": "park", "name_en": "Navoiy Central Park", "name_uz": "Navoiy markaziy bog'i",
         "name_ru": "Центральный парк Навои", "price": 0, "lat": 40.0820, "lon": 65.3750,
         "desc": "City park with fountains and monuments",
         "tags": ["park", "green", "fountains", "monument", "family", "free"]},
        {"type": "restaurant", "name_en": "Alisher Navoi Restaurant", "name_uz": "Alisher Navoiy restorani",
         "name_ru": "Ресторан Алишер Навои", "cuisine": "Uzbek", "lat": 40.0850, "lon": 65.3780,
         "desc": "Traditional Uzbek restaurant", "tags": ["restaurant", "uzbek", "traditional", "cultural"]},
        {"type": "shop", "name_en": "Navoiy Bazaar", "name_uz": "Navoiy bozori", "name_ru": "Базар Навои",
         "lat": 40.0880, "lon": 65.3820, "desc": "Local market with fresh produce",
         "tags": ["shop", "bazaar", "market", "local"]},
        {"type": "entertainment", "name_en": "Navoiy Palace of Culture", "name_uz": "Navoiy madaniyat saroyi",
         "name_ru": "Дворец культуры Навои", "price": 20000, "lat": 40.0860, "lon": 65.3810,
         "desc": "Cultural center with concerts and theater",
         "tags": ["entertainment", "culture", "theater", "concerts", "events"]}
    ],
    "Surkhandarya": [
        {"type": "hotel", "name_en": "Termez Palace Hotel", "name_uz": "Termiz Palace mehmonxonasi",
         "name_ru": "Отель Термез Палас", "star": 3, "price": 280000, "lat": 37.2240, "lon": 67.2780,
         "desc": "Best hotel in Termez with pool", "tags": ["hotel", "comfort", "pool", "restaurant", "best"]},
        {"type": "hotel", "name_en": "Termez Hotel", "name_uz": "Termiz mehmonxonasi", "name_ru": "Отель Термез",
         "star": 2, "price": 180000, "lat": 37.2200, "lon": 67.2800, "desc": "Simple hotel in the city center",
         "tags": ["hotel", "budget", "simple", "center"]},
        {"type": "museum", "name_en": "Fayaz-Tepa Buddhist Temple", "name_uz": "Fayoztepa budda ibodatxonasi",
         "name_ru": "Буддийский храм Фаяз-Тепа", "price": 25000, "lat": 37.2300, "lon": 67.2950,
         "desc": "Ancient Buddhist monastery with stunning frescoes",
         "tags": ["museum", "buddhist", "ancient", "temple", "frescoes", "unique", "archaeology"]},
        {"type": "museum", "name_en": "Sultan Saodat Mausoleum", "name_uz": "Sulton Saodat maqbarasi",
         "name_ru": "Мавзолей Султан Саодат", "price": 0, "lat": 37.2620, "lon": 67.3090,
         "desc": "Complex of mausoleums, sacred pilgrimage site",
         "tags": ["museum", "mausoleum", "islamic", "pilgrimage", "medieval", "free"]},
        {"type": "restaurant", "name_en": "Amudarya Restaurant", "name_uz": "Amudaryo restorani",
         "name_ru": "Ресторан Амударья", "cuisine": "Uzbek, Fish", "lat": 37.2260, "lon": 67.2790,
         "desc": "Specializing in fresh Amu Darya river fish",
         "tags": ["restaurant", "uzbek", "fish", "river", "local"]},
        {"type": "shop", "name_en": "Termez Central Market", "name_uz": "Termiz markaziy bozori",
         "name_ru": "Центральный рынок Термеза", "lat": 37.2250, "lon": 67.2820,
         "desc": "Main market with Afghan border trade goods", "tags": ["shop", "market", "bazaar", "spices", "local"]},
        {"type": "entertainment", "name_en": "Termez Archaeological Museum", "name_uz": "Termiz arxeologiya muzeyi",
         "name_ru": "Термезский археологический музей", "price": 20000, "lat": 37.2280, "lon": 67.2820,
         "desc": "Museum with Buddhist artifacts and Greek-Bactrian gold",
         "tags": ["entertainment", "museum", "archaeology", "buddhist", "gold", "history"]}
    ],
    "Kashkadarya": [
        {"type": "hotel", "name_en": "Shakhrisabz Orient Hotel", "name_uz": "Shahrisabz Orient mehmonxonasi",
         "name_ru": "Отель Шахрисабз Ориент", "star": 3, "price": 310000, "lat": 39.0580, "lon": 66.8310,
         "desc": "Cozy hotel steps from Ak-Saray Palace",
         "tags": ["hotel", "cozy", "traditional", "near palace", "center"]},
        {"type": "hotel", "name_en": "Karshi Hotel", "name_uz": "Qarshi mehmonxonasi", "name_ru": "Отель Карши",
         "star": 2, "price": 180000, "lat": 38.8610, "lon": 65.7890, "desc": "Simple budget hotel in Karshi",
         "tags": ["hotel", "budget", "simple", "center"]},
        {"type": "museum", "name_en": "Ak-Saray Palace", "name_uz": "Oq-Saroy saroyi", "name_ru": "Дворец Ак-Сарай",
         "price": 30000, "lat": 39.0600, "lon": 66.8290,
         "desc": "Ruins of Amir Timur's magnificent summer palace. UNESCO",
         "tags": ["museum", "palace", "timur", "ruins", "unesco", "history", "iconic"]},
        {"type": "museum", "name_en": "Dorut Tilovat Complex", "name_uz": "Dorut Tilovat majmuasi",
         "name_ru": "Комплекс Дорут Тиловат", "price": 0, "lat": 39.0570, "lon": 66.8280,
         "desc": "Religious complex with Kok Gumbaz mosque",
         "tags": ["museum", "mosque", "tomb", "timur", "blue dome", "unesco", "free"]},
        {"type": "park", "name_en": "Shakhrisabz Central Park", "name_uz": "Shahrisabz markaziy bog'i",
         "name_ru": "Центральный парк Шахрисабза", "price": 0, "lat": 39.0590, "lon": 66.8330,
         "desc": "City park near Ak-Saray Palace", "tags": ["park", "monument", "timur", "garden", "free", "family"]},
        {"type": "restaurant", "name_en": "Oqsaroy Restaurant", "name_uz": "Oqsaroy restorani",
         "name_ru": "Ресторан Оксарой", "cuisine": "Uzbek", "lat": 39.0610, "lon": 66.8300,
         "desc": "Traditional Kashkadarya cuisine",
         "tags": ["restaurant", "uzbek", "traditional", "pilaf", "near palace"]},
        {"type": "shop", "name_en": "Shakhrisabz Craft Bazaar", "name_uz": "Shahrisabz hunarmandlar bozori",
         "name_ru": "Ремесленный базар Шахрисабза", "lat": 39.0620, "lon": 66.8320,
         "desc": "Market with handmade embroidery and carpets",
         "tags": ["shop", "bazaar", "craft", "embroidery", "carpets", "souvenir"]}
    ],
    "Syrdarya": [
        {"type": "hotel", "name_en": "Guliston Hotel", "name_uz": "Guliston mehmonxonasi", "name_ru": "Отель Гулистан",
         "star": 2, "price": 150000, "lat": 40.4180, "lon": 68.6720, "desc": "Simple hotel in Gulistan city center",
         "tags": ["hotel", "budget", "simple", "center", "cheap"]},
        {"type": "hotel", "name_en": "Syrdarya Hotel", "name_uz": "Sirdaryo mehmonxonasi", "name_ru": "Отель Сырдарья",
         "star": 2, "price": 140000, "lat": 40.4150, "lon": 68.6700, "desc": "Basic hotel near the river",
         "tags": ["hotel", "budget", "simple", "river"]},
        {"type": "museum", "name_en": "Syrdarya Regional Museum", "name_uz": "Sirdaryo viloyat muzeyi",
         "name_ru": "Сырдарьинский областной музей", "price": 10000, "lat": 40.4200, "lon": 68.6700,
         "desc": "Regional museum with exhibits on history", "tags": ["museum", "history", "regional", "nature"]},
        {"type": "park", "name_en": "Syr Darya Riverside Park", "name_uz": "Sirdaryo bo'yi parki",
         "name_ru": "Парк набережной Сырдарьи", "price": 0, "lat": 40.4160, "lon": 68.6650,
         "desc": "Peaceful riverside park", "tags": ["park", "river", "picnic", "nature", "boats", "free", "family"]},
        {"type": "restaurant", "name_en": "Bakhor Cafe Gulistan", "name_uz": "Bahor kafesi Guliston",
         "name_ru": "Кафе Бахор Гулистан", "cuisine": "Uzbek, European", "lat": 40.4170, "lon": 68.6740,
         "desc": "Cozy family cafe with garden seating",
         "tags": ["restaurant", "uzbek", "european", "cafe", "garden", "cozy"]},
        {"type": "shop", "name_en": "Gulistan Bazaar", "name_uz": "Guliston bozori", "name_ru": "Гулистанский базар",
         "lat": 40.4190, "lon": 68.6760, "desc": "Local market with fresh produce",
         "tags": ["shop", "bazaar", "market", "local", "food"]}
    ]
}

TOURS_DATA = [
    # === ТАШКЕНТ (2) ===
    {
        "name_en": "Tashkent in 1 Day", "name_uz": "Toshkent 1 kunda", "name_ru": "Ташкент за 1 день",
        "days": 1, "transport": "car", "region": "Tashkent",
        "cover_url": "/static/photos/tours/tour_tashkent_1day.jpg",
        "stops": ["Amir Timur Museum", "Tashkent Tower", "Magic City Park", "Afsona Restaurant"],
    },
    {
        "name_en": "Cultural Tashkent", "name_uz": "Madaniy Toshkent", "name_ru": "Культурный Ташкент",
        "days": 1, "transport": "public", "region": "Tashkent",
        "cover_url": "/static/photos/tours/tour_cultural_tashkent.jpg",
        "stops": ["State Museum of History of Uzbekistan", "Museum of Applied Arts", "Khast Imam Complex", "Beshqozon"],
    },
    {
        "name_en": "Family Weekend Tashkent", "name_uz": "Oilaviy dam olish Toshkent",
        "name_ru": "Семейные выходные Ташкент",
        "days": 2, "transport": "car", "region": "Tashkent",
        "cover_url": "/static/photos/tours/tour_family_weekend.jpg",
        "stops": ["Tashkent Botanical Garden", "Alisher Navoi National Park", "Magic City Park", "Caravan Restaurant"],
    },

    # === САМАРКАНД (2) ===
    {
        "name_en": "Samarkand Gold", "name_uz": "Samarqand oltini", "name_ru": "Золото Самарканда",
        "days": 1, "transport": "car", "region": "Samarkand",
        "cover_url": "/static/photos/tours/tour_samarkand_gold.jpg",
        "stops": ["Registan Square", "Gur-e-Amir Mausoleum", "Shah-i-Zinda Necropolis", "Samarkand Pilaf Center"],
    },
    {
        "name_en": "Samarkand Weekend", "name_uz": "Samarqand dam olish", "name_ru": "Самаркандский уикенд",
        "days": 2, "transport": "public", "region": "Samarkand",
        "cover_url": "/static/photos/tours/tour_samarkand_weekend.jpg",
        "stops": ["Siab Bazaar", "Registan Square", "Central Park Samarkand", "Old City Restaurant"],
    },

    # === БУХАРА (2) ===
    {
        "name_en": "Bukhara Old City", "name_uz": "Buxoro eski shahar", "name_ru": "Старая Бухара",
        "days": 1, "transport": "walking", "region": "Bukhara",
        "cover_url": "/static/photos/tours/tour_bukhara_old.jpg",
        "stops": ["Ark Fortress", "Bolo Hauz Mosque", "Samanid Mausoleum", "Lyabi House Hotel"],
    },
    {
        "name_en": "Bukhara Silk Road", "name_uz": "Buxoro Ipak yo'li", "name_ru": "Бухарский шёлковый путь",
        "days": 2, "transport": "car", "region": "Bukhara",
        "cover_url": "/static/photos/tours/tour_bukhara_silk.jpg",
        "stops": ["Samanid Mausoleum", "Toki Sarrafon Bazaar", "Ark Fortress", "Old Bukhara Restaurant"],
    },

    # === ХИВА / ХОРЕЗМ (2) ===
    {
        "name_en": "Khiva Inside Walls", "name_uz": "Xiva ichki qal'a", "name_ru": "Хива внутри стен",
        "days": 1, "transport": "walking", "region": "Khorezm",
        "cover_url": "/static/photos/tours/tour_khiva_walls.jpg",
        "stops": ["Ichan-Kala Fortress", "Kalta Minor Minaret", "Pakhlavan Mahmud Mausoleum", "Khorezm Art Restaurant"],
    },
    {
        "name_en": "Khiva Sunset", "name_uz": "Xiva quyosh botishi", "name_ru": "Хивинский закат",
        "days": 1, "transport": "walking", "region": "Khorezm",
        "cover_url": "/static/photos/tours/tour_khiva_sunset.jpg",
        "stops": ["Ichan-Kala Bazaar", "Ichan-Kala Fortress", "Terrassa Restaurant", "Al-Khorezmi Park"],
    },

    # === ОСТАЛЬНЫЕ 8 ОБЛАСТЕЙ (по 1) ===
    {
        "name_en": "Fergana Valley Day", "name_uz": "Farg'ona vodiysi kuni", "name_ru": "День в Ферганской долине",
        "days": 1, "transport": "car", "region": "Fergana",
        "cover_url": "/static/photos/tours/tour_fergana_valley.jpg",
        "stops": ["Fergana Regional Museum", "Fergana Central Park", "Fergana Pilaf Center"],
    },
    {
        "name_en": "Andijan Heritage", "name_uz": "Andijon merosi", "name_ru": "Наследие Андижана",
        "days": 1, "transport": "car", "region": "Andijan",
        "cover_url": "/static/photos/tours/tour_andijan_heritage.jpg",
        "stops": ["Babur Literary Museum", "Babur Park", "Andijon Osh Markazi"],
    },
    {
        "name_en": "Namangan Gardens", "name_uz": "Namangan bog'lari", "name_ru": "Сады Намангана",
        "days": 1, "transport": "car", "region": "Namangan",
        "cover_url": "/static/photos/tours/tour_namangan_gardens.jpg",
        "stops": ["Babur Park Namangan", "Afsonalar Bogi Namangan", "Oltin Vodiy Restaurant"],
    },
    {
        "name_en": "Jizzakh Nature", "name_uz": "Jizzax tabiati", "name_ru": "Природа Джизака",
        "days": 1, "transport": "car", "region": "Jizzakh",
        "cover_url": "/static/photos/tours/tour_jizzakh_nature.jpg",
        "stops": ["Aydarkul Lake", "Jizzakh Samsa Center"],
    },
    {
        "name_en": "Navoiy Petroglyphs", "name_uz": "Navoiy petrogliflari", "name_ru": "Петроглифы Навои",
        "days": 1, "transport": "car", "region": "Navoiy",
        "cover_url": "/static/photos/tours/tour_navoiy_petroglyphs.jpg",
        "stops": ["Sarmishsay Petroglyphs", "Alisher Navoi Restaurant"],
    },
    {
        "name_en": "Shakhrisabz History", "name_uz": "Shahrisabz tarixi", "name_ru": "История Шахрисабза",
        "days": 1, "transport": "car", "region": "Kashkadarya",
        "cover_url": "/static/photos/tours/tour_shakhrisabz_history.jpg",
        "stops": ["Ak-Saray Palace", "Dorut Tilovat Complex", "Oqsaroy Restaurant"],
    },
    {
        "name_en": "Termez Ancient", "name_uz": "Termiz qadimiy", "name_ru": "Древний Термез",
        "days": 1, "transport": "car", "region": "Surkhandarya",
        "cover_url": "/static/photos/tours/tour_termez_ancient.jpg",
        "stops": ["Fayaz-Tepa Buddhist Temple", "Sultan Saodat Mausoleum", "Termez Archaeological Museum"],
    },
    {
        "name_en": "Syrdarya Riverside", "name_uz": "Sirdaryo bo'ylab", "name_ru": "Вдоль Сырдарьи",
        "days": 1, "transport": "car", "region": "Syrdarya",
        "cover_url": "/static/photos/tours/tour_syrdarya_riverside.jpg",
        "stops": ["Syr Darya Riverside Park", "Bakhor Cafe Gulistan"],
    },
]


def seed():
    init_db()
    db = SessionLocal()

    try:
        # Очистка — порядок важен из-за foreign keys (сначала зависимые)
        db.query(TourBooking).delete()
        db.query(TourStop).delete()
        db.query(Tour).delete()
        db.query(Notification).delete()
        db.query(ChatMessage).delete()
        db.query(Review).delete()
        db.query(BookingRequest).delete()
        db.query(SavedItem).delete()
        db.query(PropertyTag).delete()
        db.query(PropertyUnit).delete()
        db.query(Photo).delete()
        db.query(Property).delete()
        db.query(UserTourExpense).delete()
        db.query(PromoCode).delete()
        db.query(ExchangeRate).delete()
        db.query(Region).delete()
        db.commit()

        # Регионы
        region_map = {}
        for r_data in REGIONS_DATA:
            region = Region(
                name_en=r_data["name_en"], name_uz=r_data["name_uz"], name_ru=r_data["name_ru"],
                lat=r_data["lat"], lon=r_data["lon"],
                best_season=r_data["best_season"], description=r_data["description"],
                is_active=True,
                icon_url=f"/static/photos/regions/{r_data['name_en'].lower()}_icon.jpg",
                cover_url=f"/static/photos/regions/{r_data['name_en'].lower()}_cover.jpg",
            )
            db.add(region)
            db.flush()
            region_map[r_data["name_en"]] = region

        # Свойства
        for region_name, properties in PROPERTIES_BY_REGION.items():
            region = region_map[region_name]
            for p_data in properties:
                if p_data.get("lat"):
                    lat = p_data["lat"]
                elif region.lat is not None:
                    lat = region.lat + (hash(p_data["name_en"]) % 100 - 50) / 500
                else:
                    lat = 41.0

                if p_data.get("lon"):
                    lon = p_data["lon"]
                elif region.lon is not None:
                    lon = region.lon + (hash(p_data["name_en"] + "x") % 100 - 50) / 500
                else:
                    lon = 69.0
                prop = Property(
                    region_id=region.id, property_type=p_data["type"],
                    name_en=p_data["name_en"], name_uz=p_data.get("name_uz", p_data["name_en"]),
                    name_ru=p_data.get("name_ru", p_data["name_en"]),
                    description_en=p_data.get("desc", ""), description_uz=p_data.get("desc", ""),
                    description_ru=p_data.get("desc", ""),
                    lat=lat, lon=lon,
                    stars=p_data.get("star"), cuisine_type=p_data.get("cuisine"),
                    rating_uz=round(3.5 + (hash(p_data["name_en"]) % 15) / 10, 1),
                    rating_guest=round(3.5 + (hash(p_data["name_en"] + "g") % 15) / 10, 1),
                    total_reviews=(hash(p_data["name_en"]) % 200) + 10,
                    is_active=True, moderation_status="approved",
                    cover_url=f"/static/photos/properties/placeholder_{p_data['type']}.jpg",
                    icon_url=f"/static/photos/properties/placeholder_{p_data['type']}.jpg",
                )
                db.add(prop)
                db.flush()

                for tag in p_data.get("tags", []):
                    db.add(PropertyTag(property_id=prop.id, tag=tag))

                if p_data["type"] == "hotel":
                    unit_types = [
                        {"name": "Standard Room", "price_factor": 1.0, "guests": 2},
                        {"name": "Deluxe Room", "price_factor": 1.5, "guests": 2},
                        {"name": "Family Suite", "price_factor": 2.2, "guests": 4},
                    ]
                    for i, ut in enumerate(unit_types[:2 + (hash(p_data["name_en"]) % 2)]):
                        base_price = p_data["price"] * ut["price_factor"]
                        unit = PropertyUnit(
                            property_id=prop.id, unit_type="room",
                            name_en=f"{p_data['name_en']} - {ut['name']}",
                            name_uz=f"{p_data['name_uz']} - {ut['name']}",
                            base_price=base_price,
                            discount_price=base_price * 0.85 if i == 0 else None,
                            max_guests=ut["guests"], bedrooms=1 if ut["guests"] <= 2 else 2, is_active=True,
                        )
                        db.add(unit)
                elif p_data.get("price", 0) > 0:
                    unit = PropertyUnit(
                        property_id=prop.id, unit_type="entrance",
                        name_en="Standard Ticket", name_uz="Standart chipta", name_ru="Стандартный билет",
                        base_price=p_data["price"], is_active=True,
                    )
                    db.add(unit)

        # Тур-пакеты
        for t_data in TOURS_DATA:
            tour = Tour(
                region_id=region_map["Tashkent"].id,
                name_en=t_data["name_en"], name_uz=t_data["name_uz"], name_ru=t_data["name_ru"],
                duration_days=t_data["days"], transport_type=t_data["transport"],
                cover_url=t_data.get("cover_url"),
                is_template=True, is_active=True,
            )
            db.add(tour)
            db.flush()

            for i, stop_name in enumerate(t_data["stops"]):
                prop = db.query(Property).filter(Property.name_en == stop_name).first()
                if prop:
                    stop = TourStop(
                        tour_id=tour.id, property_id=prop.id,
                        stop_order=i + 1, duration_minutes=90,
                    )
                    db.add(stop)
        # Промокоды
        promos = [
            {"code": "GUIDEME", "discount_percent": 10, "description": "10% off your tour"},
            {"code": "WELCOME", "discount_percent": 15, "description": "15% off for new users"},
            {"code": "SUMMER", "discount_percent": 20, "description": "20% summer special", "max_uses": 50},
        ]
        for p in promos:
            promo = PromoCode(
                code=p["code"],
                discount_percent=p["discount_percent"],
                description=p["description"],
                max_uses=p.get("max_uses", 100),
            )
            db.add(promo)
        db.commit()
        print(
            f"✅ Seeded: {len(region_map)} regions, {sum(len(v) for v in PROPERTIES_BY_REGION.values())} properties, {len(TOURS_DATA)} tours")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
