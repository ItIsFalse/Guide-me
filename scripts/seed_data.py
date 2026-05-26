"""
Заполняет базу тестовыми данными: 12 областей Узбекистана + отели, музеи, рестораны + теги.
Запуск: python -m scripts.seed_data
"""
import sys
sys.path.insert(0, ".")

from app.core.database import SessionLocal, init_db
from app.models.region import Region
from app.models.property import Property
from app.models.property_unit import PropertyUnit
from app.models.property_tag import PropertyTag


REGIONS_DATA = [
    {"name_en": "Andijan", "name_uz": "Andijon", "name_ru": "Андижан", "lat": 40.78, "lon": 72.34, "best_season": "Spring, Autumn", "description": "Industrial and cultural center of Fergana Valley"},
    {"name_en": "Bukhara", "name_uz": "Buxoro", "name_ru": "Бухара", "lat": 39.77, "lon": 64.42, "best_season": "Spring, Autumn", "description": "Ancient city on the Silk Road with stunning Islamic architecture"},
    {"name_en": "Jizzakh", "name_uz": "Jizzax", "name_ru": "Джизак", "lat": 40.12, "lon": 67.84, "best_season": "Spring, Summer", "description": "Gateway to Samarkand, known for Aydarkul Lake"},
    {"name_en": "Kashkadarya", "name_uz": "Qashqadaryo", "name_ru": "Кашкадарья", "lat": 38.85, "lon": 65.79, "best_season": "Spring, Autumn", "description": "Home to Shakhrisabz, birthplace of Amir Timur"},
    {"name_en": "Navoiy", "name_uz": "Navoiy", "name_ru": "Навои", "lat": 40.08, "lon": 65.38, "best_season": "Spring, Autumn", "description": "Region of deserts and ancient caravanserais"},
    {"name_en": "Namangan", "name_uz": "Namangan", "name_ru": "Наманган", "lat": 40.99, "lon": 71.67, "best_season": "Spring, Summer", "description": "Famous for gardens, flowers and the beautiful Chartak Reservoir"},
    {"name_en": "Samarkand", "name_uz": "Samarqand", "name_ru": "Самарканд", "lat": 39.65, "lon": 66.97, "best_season": "Spring, Autumn", "description": "Crossroads of cultures, Registan Square and centuries of history"},
    {"name_en": "Surkhandarya", "name_uz": "Surxondaryo", "name_ru": "Сурхандарья", "lat": 37.22, "lon": 67.28, "best_season": "Spring, Autumn", "description": "Southernmost region with unique Buddhist heritage"},
    {"name_en": "Syrdarya", "name_uz": "Sirdaryo", "name_ru": "Сырдарья", "lat": 40.42, "lon": 68.67, "best_season": "Spring, Summer", "description": "Fertile lands along the Syr Darya river"},
    {"name_en": "Tashkent", "name_uz": "Toshkent", "name_ru": "Ташкент", "lat": 41.30, "lon": 69.24, "best_season": "Spring, Autumn", "description": "Modern capital blending Soviet legacy with Islamic heritage"},
    {"name_en": "Fergana", "name_uz": "Farg'ona", "name_ru": "Фергана", "lat": 40.39, "lon": 71.78, "best_season": "Spring, Summer", "description": "Heart of Fergana Valley, silk and ceramics center"},
    {"name_en": "Khorezm", "name_uz": "Xorazm", "name_ru": "Хорезм", "lat": 41.38, "lon": 60.36, "best_season": "Spring, Autumn", "description": "Ancient Khiva, desert fortresses and unique culture"},
]

# Каждый регион получит 3 объекта: отель, музей/парк, ресторан
PROPERTIES_BY_REGION = {
    "Andijan": [
        {"type": "hotel", "name_en": "Andijan Palace Hotel", "name_uz": "Andijon Palace mehmonxonasi", "star": 4, "price": 420000, "desc": "Comfortable hotel in the city center with pool and spa", "tags": ["hotel", "comfort", "pool", "spa", "business"]},
        {"type": "museum", "name_en": "Babur Literary Museum", "name_uz": "Bobur adabiyot muzeyi", "price": 25000, "desc": "Dedicated to Zahiriddin Muhammad Babur, founder of Mughal Empire", "tags": ["museum", "history", "literature", "culture", "babur"]},
        {"type": "restaurant", "name_en": "Chinor Restaurant", "name_uz": "Chinor restorani", "cuisine": "Uzbek", "desc": "Traditional pilaf and shashlik under century-old plane trees", "tags": ["restaurant", "uzbek", "pilaf", "traditional", "garden"]},
    ],
    "Bukhara": [
        {"type": "hotel", "name_en": "Lyabi House Hotel", "name_uz": "Lyabi House mehmonxonasi", "star": 3, "price": 380000, "desc": "Historic boutique hotel near Lyabi-Hauz ensemble", "tags": ["hotel", "boutique", "historic", "budget", "center"]},
        {"type": "museum", "name_en": "Ark Fortress", "name_uz": "Ark qal'asi", "price": 40000, "desc": "Ancient citadel housing museums of Bukhara's rich history", "tags": ["museum", "fortress", "history", "unesco", "ancient"]},
        {"type": "restaurant", "name_en": "Minzifa Terrace", "name_uz": "Minzifa terasi", "cuisine": "Uzbek, European", "desc": "Rooftop dining with panoramic Old City views", "tags": ["restaurant", "rooftop", "view", "uzbek", "european", "romantic"]},
    ],
    "Jizzakh": [
        {"type": "hotel", "name_en": "Jizzakh Plaza", "name_uz": "Jizzax Plaza mehmonxonasi", "star": 3, "price": 280000, "desc": "Modern hotel with conference facilities", "tags": ["hotel", "modern", "business", "conference", "budget"]},
        {"type": "park", "name_en": "Aydarkul Lake Camp", "name_uz": "Aydarko'l lageri", "price": 50000, "desc": "Yurt camping by the vast Aydarkul Lake", "tags": ["park", "lake", "camping", "nature", "yurt", "family"]},
        {"type": "restaurant", "name_en": "Zomin Osh Markazi", "name_uz": "Zomin osh markazi", "cuisine": "Uzbek", "desc": "Famous for Jizzakh-style samsa and grilled meats", "tags": ["restaurant", "uzbek", "samsa", "grill", "local"]},
    ],
    "Kashkadarya": [
        {"type": "hotel", "name_en": "Shakhrisabz Orient", "name_uz": "Shahrisabz Orient mehmonxonasi", "star": 3, "price": 310000, "desc": "Cozy hotel steps from Ak-Saray Palace ruins", "tags": ["hotel", "cozy", "historic", "budget"]},
        {"type": "museum", "name_en": "Ak-Saray Palace", "name_uz": "Oq-Saroy saroyi", "price": 30000, "desc": "Ruins of Amir Timur's magnificent summer palace", "tags": ["museum", "palace", "history", "timur", "ruins", "unesco"]},
        {"type": "restaurant", "name_en": "Timur's Feast", "name_uz": "Temur ziyofati", "cuisine": "Uzbek", "desc": "Royal Uzbek cuisine in a traditional setting", "tags": ["restaurant", "uzbek", "royal", "traditional", "timur"]},
    ],
    "Navoiy": [
        {"type": "hotel", "name_en": "Navoiy Grand", "name_uz": "Navoiy Grand mehmonxonasi", "star": 3, "price": 260000, "desc": "Business hotel near Navoi Mining Complex", "tags": ["hotel", "business", "budget", "modern"]},
        {"type": "park", "name_en": "Sarmishsay Petroglyphs", "name_uz": "Sarmishsoy petrogliflari", "price": 35000, "desc": "Ancient rock carvings in a scenic gorge, 4000+ years old", "tags": ["park", "petroglyphs", "history", "ancient", "nature", "gorge"]},
        {"type": "restaurant", "name_en": "Kyzylkum Chaikhana", "name_uz": "Qizilqum choyxonasi", "cuisine": "Uzbek", "desc": "Desert-style tea house with camel milk tea", "tags": ["restaurant", "tea", "desert", "uzbek", "traditional", "exotic"]},
    ],
    "Namangan": [
        {"type": "hotel", "name_en": "Chartak Resort", "name_uz": "Chortoq kurorti", "star": 4, "price": 520000, "desc": "Health resort with mineral springs and mountain views", "tags": ["hotel", "resort", "spa", "health", "mountains", "springs"]},
        {"type": "park", "name_en": "Afsonalar Bogi", "name_uz": "Afsonalar bog'i", "price": 20000, "desc": "Legends Park — family amusement park with rides", "tags": ["park", "amusement", "family", "children", "rides"]},
        {"type": "restaurant", "name_en": "Namangan Garden", "name_uz": "Namangan bog'i", "cuisine": "Uzbek, Turkish", "desc": "Garden restaurant famous for Namangan apples and kebabs", "tags": ["restaurant", "garden", "uzbek", "turkish", "kebab", "family"]},
    ],
    "Samarkand": [
        {"type": "hotel", "name_en": "Registon Saroy Hotel", "name_uz": "Registon Saroy mehmonxonasi", "star": 4, "price": 550000, "desc": "Elegant hotel with Registan Square view from rooftop", "tags": ["hotel", "luxury", "view", "registan", "center", "rooftop"]},
        {"type": "museum", "name_en": "Registan Square", "name_uz": "Registon maydoni", "price": 65000, "desc": "Three magnificent madrasahs — heart of ancient Samarkand", "tags": ["museum", "unesco", "architecture", "history", "madrasah", "iconic"]},
        {"type": "restaurant", "name_en": "Samarkand Pilaf Center", "name_uz": "Samarqand osh markazi", "cuisine": "Uzbek", "desc": "The best Samarkand pilaf with chickpeas and lamb", "tags": ["restaurant", "uzbek", "pilaf", "famous", "local"]},
    ],
    "Surkhandarya": [
        {"type": "hotel", "name_en": "Termez Palace", "name_uz": "Termiz saroyi", "star": 3, "price": 290000, "desc": "Comfortable stay near archaeological sites of Old Termez", "tags": ["hotel", "archaeology", "budget", "comfort"]},
        {"type": "museum", "name_en": "Fayaz-Tepa Buddhist Temple", "name_uz": "Fayoztepa budda ibodatxonasi", "price": 25000, "desc": "2nd century Buddhist monastery with stunning frescoes", "tags": ["museum", "buddhist", "ancient", "temple", "frescoes", "unique"]},
        {"type": "restaurant", "name_en": "Amudarya Fish House", "name_uz": "Amudaryo baliq uyi", "cuisine": "Uzbek, Fish", "desc": "Fresh Amu Darya river fish specialties", "tags": ["restaurant", "fish", "river", "uzbek", "seafood"]},
    ],
    "Syrdarya": [
        {"type": "hotel", "name_en": "Guliston Hotel", "name_uz": "Guliston mehmonxonasi", "star": 2, "price": 180000, "desc": "Simple and affordable hotel in Guliston center", "tags": ["hotel", "budget", "simple", "cheap"]},
        {"type": "park", "name_en": "Syr Darya Riverside Park", "name_uz": "Sirdaryo bo'yi parki", "price": 0, "desc": "Peaceful riverside park for picnics and boat rides", "tags": ["park", "river", "picnic", "nature", "free", "family", "boats"]},
        {"type": "restaurant", "name_en": "Bakhor Cafe", "name_uz": "Bahor kafesi", "cuisine": "Uzbek, European", "desc": "Cozy family cafe with garden seating", "tags": ["restaurant", "cafe", "family", "garden", "uzbek", "european", "cozy"]},
    ],
    "Tashkent": [
        {"type": "hotel", "name_en": "Hyatt Regency Tashkent", "name_uz": "Hyatt Regency Toshkent", "star": 5, "price": 1200000, "desc": "Luxury international hotel in the business district", "tags": ["hotel", "luxury", "international", "business", "5star"]},
        {"type": "museum", "name_en": "Amir Timur Museum", "name_uz": "Amir Temur muzeyi", "price": 30000, "desc": "Blue-domed museum showcasing Timurid dynasty history", "tags": ["museum", "history", "timur", "monument", "statue", "culture"]},
        {"type": "restaurant", "name_en": "Afsona Restaurant", "name_uz": "Afsona restorani", "cuisine": "Uzbek, International", "desc": "Fine dining with live traditional music", "tags": ["restaurant", "fine dining", "music", "uzbek", "international", "luxury"]},
    ],
    "Fergana": [
        {"type": "hotel", "name_en": "Fergana Valley Hotel", "name_uz": "Farg'ona vodiysi mehmonxonasi", "star": 3, "price": 340000, "desc": "Cozy hotel surrounded by Fergana's famous gardens", "tags": ["hotel", "garden", "cozy", "nature"]},
        {"type": "museum", "name_en": "Rishton Ceramics Workshop", "name_uz": "Rishton kulolchilik ustaxonasi", "price": 15000, "desc": "Famous blue ceramics, watch masters at work", "tags": ["museum", "ceramics", "craft", "art", "workshop", "handmade"]},
        {"type": "restaurant", "name_en": "Margilan Silk Road", "name_uz": "Marg'ilon Ipak yo'li", "cuisine": "Uzbek", "desc": "Traditional cuisine near the silk factory", "tags": ["restaurant", "uzbek", "silk road", "traditional", "local"]},
    ],
    "Khorezm": [
        {"type": "hotel", "name_en": "Orient Star Khiva", "name_uz": "Orient Star Xiva", "star": 4, "price": 480000, "desc": "Inside the walls of Ichan-Kala, former madrasah turned hotel", "tags": ["hotel", "historic", "unique", "madrasah", "inside walls"]},
        {"type": "museum", "name_en": "Ichan-Kala Fortress", "name_uz": "Ichan-Qal'a qal'asi", "price": 100000, "desc": "UNESCO walled inner city of Khiva, open-air museum", "tags": ["museum", "unesco", "fortress", "history", "open-air", "walled city"]},
        {"type": "restaurant", "name_en": "Khorezm Art Restaurant", "name_uz": "Xorazm san'at restorani", "cuisine": "Uzbek, Khorezm", "desc": "Khorezm specialty dishes like shivit osh (dill pasta)", "tags": ["restaurant", "uzbek", "khorezm", "local", "art", "traditional"]},
    ],
}


def seed():
    init_db()
    db = SessionLocal()

    try:
        # Очищаем старые данные (в обратном порядке из-за foreign keys)
        db.query(PropertyTag).delete()
        db.query(PropertyUnit).delete()
        db.query(Property).delete()
        db.query(Region).delete()
        db.commit()

        # Создаём регионы
        region_map = {}
        for r_data in REGIONS_DATA:
            region = Region(
                name_en=r_data["name_en"],
                name_uz=r_data["name_uz"],
                name_ru=r_data["name_ru"],
                lat=r_data["lat"],
                lon=r_data["lon"],
                best_season=r_data["best_season"],
                description=r_data["description"],
                is_active=True,
                icon_url=f"/static/photos/regions/{r_data['name_en'].lower()}_icon.jpg",
                cover_url=f"/static/photos/regions/{r_data['name_en'].lower()}_cover.jpg",
            )
            db.add(region)
            db.flush()
            region_map[r_data["name_en"]] = region

        # Создаём объекты для каждого региона
        for region_name, properties in PROPERTIES_BY_REGION.items():
            region = region_map[region_name]
            for p_data in properties:
                if region.lat is not None and region.lon is not None:
                    lat = region.lat + (hash(p_data["name_en"]) % 100 - 50) / 500
                    lon = region.lon + (hash(p_data["name_en"] + "x") % 100 - 50) / 500
                else:
                    lat, lon = 41.0, 69.0  # default Tashkent

                prop = Property(
                    region_id=region.id,
                    property_type=p_data["type"],
                    name_en=p_data["name_en"],
                    name_uz=p_data.get("name_uz", p_data["name_en"]),
                    name_ru=p_data.get("name_ru", p_data["name_en"]),
                    description_en=p_data.get("desc", ""),
                    description_uz=p_data.get("desc", ""),
                    description_ru=p_data.get("desc", ""),
                    lat=lat,
                    lon=lon,
                    stars=p_data.get("star"),
                    cuisine_type=p_data.get("cuisine"),
                    rating_uz=round(3.5 + (hash(p_data["name_en"]) % 15) / 10, 1),
                    rating_guest=round(3.5 + (hash(p_data["name_en"] + "g") % 15) / 10, 1),
                    total_reviews=(hash(p_data["name_en"]) % 200) + 10,
                    is_active=True,
                    moderation_status="approved",
                    cover_url=f"/static/photos/properties/{p_data['name_en'].lower().replace(' ', '_')}_cover.jpg",
                    icon_url=f"/static/photos/properties/{p_data['name_en'].lower().replace(' ', '_')}_icon.jpg",
                )
                db.add(prop)
                db.flush()

                # Добавляем теги
                for tag in p_data.get("tags", []):
                    db.add(PropertyTag(property_id=prop.id, tag=tag))

                # Для отелей создаём 2-3 юнита (номера/коттеджи)
                if p_data["type"] == "hotel":
                    unit_types = [
                        {"name": "Standard Room", "price_factor": 1.0, "guests": 2},
                        {"name": "Deluxe Room", "price_factor": 1.5, "guests": 2},
                        {"name": "Family Suite", "price_factor": 2.2, "guests": 4},
                    ]
                    for i, ut in enumerate(unit_types[:2 + (hash(p_data["name_en"]) % 2)]):
                        base_price = p_data["price"] * ut["price_factor"]
                        unit = PropertyUnit(
                            property_id=prop.id,
                            unit_type="room",
                            name_en=f"{p_data['name_en']} - {ut['name']}",
                            name_uz=f"{p_data['name_uz']} - {ut['name']}",
                            base_price=base_price,
                            discount_price=base_price * 0.85 if i == 0 else None,
                            max_guests=ut["guests"],
                            bedrooms=1 if ut["guests"] <= 2 else 2,
                            is_active=True,
                        )
                        db.add(unit)
                elif p_data["type"] == "museum" and p_data.get("price", 0) > 0:
                    unit = PropertyUnit(
                        property_id=prop.id,
                        unit_type="entrance",
                        name_en="Standard Ticket",
                        name_uz="Standart chipta",
                        base_price=p_data["price"],
                        is_active=True,
                    )
                    db.add(unit)

        db.commit()
        print(f"✅ Seeded: {len(region_map)} regions, {sum(len(v) for v in PROPERTIES_BY_REGION.values())} properties with tags")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()