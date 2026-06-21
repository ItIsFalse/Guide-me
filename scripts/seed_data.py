import sys
sys.path.insert(0, ".")

from app.core.database import SessionLocal, init_db
from app.models.region import Region
from app.models.property import Property
from app.models.property_unit import PropertyUnit
from app.models.property_tag import PropertyTag
from app.models.property_hotel import PropertyHotel
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

from scripts.data.regions import REGIONS_DATA
from scripts.data.properties import PROPERTIES_BY_REGION
from scripts.data.tours import TOURS_DATA

import json
import random


def seed():
    init_db()
    db = SessionLocal()

    try:
        # Очистка — порядок важен из-за foreign keys
        db.query(TourBooking).delete()
        db.query(TourStop).delete()
        db.query(Tour).delete()
        db.query(PropertyHotel).delete()
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
                icon_url=r_data.get("icon_url", ""),
                cover_url=r_data.get("cover_url", ""),
            )
            db.add(region)
            db.flush()
            region_map[r_data["name_en"]] = region

        # Свойства
        for region_name, properties in PROPERTIES_BY_REGION.items():
            region = region_map[region_name]
            for p_data in properties:
                lat = p_data.get("lat") or (region.lat + random.uniform(-0.05, 0.05) if region.lat else 41.0)
                lon = p_data.get("lon") or (region.lon + random.uniform(-0.05, 0.05) if region.lon else 69.0)

                prop = Property(
                    region_id=region.id,
                    property_type=p_data["type"],
                    name_en=p_data["name_en"],
                    name_uz=p_data.get("name_uz", p_data["name_en"]),
                    name_ru=p_data.get("name_ru", p_data["name_en"]),
                    description_en=p_data.get("desc_en", ""),
                    description_uz=p_data.get("desc_uz", ""),
                    description_ru=p_data.get("desc_ru", ""),
                    lat=lat, lon=lon,
                    website=p_data.get("website"),
                    phone=p_data.get("phone"),
                    address=p_data.get("address"),
                    working_hours=p_data.get("working_hours"),
                    weekend=p_data.get("weekend"),
                    cuisine_type=p_data.get("cuisine"),
                    price_level=p_data.get("price_level"),
                    stars=p_data.get("stars"),
                    has_wifi=p_data.get("has_wifi", False),
                    has_parking=p_data.get("has_parking", False),
                    has_breakfast=p_data.get("has_breakfast", False),
                    has_pool=p_data.get("has_pool", False),
                    has_gym=p_data.get("has_gym", False),
                    has_spa=p_data.get("has_spa", False),
                    has_restaurant=p_data.get("has_restaurant", False),
                    has_24h_front_desk=p_data.get("has_24h_front_desk", False),
                    pet_friendly=p_data.get("pet_friendly", False),
                    has_delivery=p_data.get("has_delivery", False),
                    has_takeaway=p_data.get("has_takeaway", False),
                    chat_enabled=p_data.get("chat_enabled", False),
                    cover_url=p_data.get("cover_url", f"/static/photos/properties/placeholder_{p_data['type']}.jpg"),
                    icon_url=p_data.get("icon_url", f"/static/photos/properties/placeholder_{p_data['type']}.jpg"),
                    rating_uz=round(3.5 + random.random() * 1.5, 1),
                    rating_guest=round(3.5 + random.random() * 1.5, 1),
                    total_reviews=random.randint(10, 200),
                    is_active=True,
                    moderation_status="approved",
                )
                db.add(prop)
                db.flush()

                # Теги
                for tag in p_data.get("tags", []):
                    db.add(PropertyTag(property_id=prop.id, tag=tag))

                # Отели → PropertyHotel
                if p_data["type"] == "hotel":
                    hotel_units = p_data.get("hotels", [])
                    if hotel_units:
                        for hu in hotel_units:
                            db.add(PropertyHotel(
                                property_id=prop.id,
                                name_en=hu.get("name_en", "Standard Room"),
                                name_uz=hu.get("name_uz"),
                                name_ru=hu.get("name_ru"),
                                description_en=hu.get("desc_en"),
                                stars=hu.get("stars", p_data.get("stars")),
                                base_price=hu.get("price", 0),
                                discount_price=hu.get("discount"),
                                max_guests=hu.get("guests", 2),
                                bedrooms=hu.get("bedrooms", 1),
                                beds=hu.get("beds", 1),
                                bathrooms=hu.get("bathrooms", 1),
                                lat=hu.get("lat"),
                                lon=hu.get("lon"),
                                features=json.dumps(hu.get("features", [])),
                                distance_to=hu.get("distance_to"),
                                photo_urls=hu.get("photo_urls"),
                            ))
                    else:
                        db.add(PropertyHotel(
                            property_id=prop.id,
                            name_en="Standard Room",
                            base_price=p_data.get("price", 0),
                            max_guests=2,
                        ))
                # Не-отели с ценой → PropertyUnit
                elif p_data.get("price", 0) > 0:
                    db.add(PropertyUnit(
                        property_id=prop.id,
                        base_price=p_data["price"],
                        max_guests=1,
                    ))

        # Тур-пакеты
        for t_data in TOURS_DATA:
            tour_region = t_data.get("region", "Tashkent")
            tour = Tour(
                region_id=region_map[tour_region].id,
                name_en=t_data["name_en"],
                name_uz=t_data.get("name_uz"),
                name_ru=t_data.get("name_ru"),
                description_en=t_data.get("desc_en"),
                description_uz=t_data.get("desc_uz"),
                description_ru=t_data.get("desc_ru"),
                duration_days=t_data["days"],
                transport_type=t_data["transport"],
                avg_total_cost=t_data.get("total_cost", 0),
                avg_accommodation_cost=t_data.get("acc_cost", 0),
                avg_food_cost=t_data.get("food_cost", 0),
                avg_transport_cost=t_data.get("trans_cost", 0),
                avg_entertainment_cost=t_data.get("ent_cost", 0),
                cover_url=t_data.get("cover_url"),
                is_template=True,
                is_active=True,
            )
            db.add(tour)
            db.flush()

            for i, stop_name in enumerate(t_data["stops"]):
                prop = db.query(Property).filter(Property.name_en == stop_name).first()
                if prop:
                    db.add(TourStop(
                        tour_id=tour.id,
                        property_id=prop.id,
                        stop_order=i + 1,
                        duration_minutes=90,
                    ))

        # Промокоды
        promos = [
            {"code": "GUIDEME", "discount_percent": 10, "description": "10% off your tour"},
            {"code": "WELCOME", "discount_percent": 15, "description": "15% off for new users"},
            {"code": "SUMMER", "discount_percent": 20, "description": "20% summer special", "max_uses": 50},
        ]
        for p in promos:
            db.add(PromoCode(
                code=p["code"],
                discount_percent=p["discount_percent"],
                description=p["description"],
                max_uses=p.get("max_uses", 100),
            ))

        db.commit()
        print(f"✅ Seeded: {len(region_map)} regions, {sum(len(v) for v in PROPERTIES_BY_REGION.values())} properties, {len(TOURS_DATA)} tours")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()