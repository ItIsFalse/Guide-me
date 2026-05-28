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
PROPERTIES_BY_REGION = {}


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