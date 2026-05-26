from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.property import Property
from app.models.property_unit import PropertyUnit


def get_properties(
    db: Session,
    region_id: int | None = None,
    property_type: str | None = None,
    stars: int | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    query = db.query(Property).filter(Property.is_active == True, Property.moderation_status == "approved")

    if region_id:
        query = query.filter(Property.region_id == region_id)
    if property_type:
        query = query.filter(Property.property_type == property_type)
    if stars:
        query = query.filter(Property.stars == stars)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Property.name_en.ilike(search_term),
                Property.name_uz.ilike(search_term),
                Property.name_ru.ilike(search_term),
                Property.description_en.ilike(search_term),
            )
        )

    total = query.count()
    properties = query.offset((page - 1) * page_size).limit(page_size).all()

    return properties, total


def get_property_by_id(db: Session, property_id: int) -> Property | None:
    return db.query(Property).filter(Property.id == property_id, Property.is_active == True).first()


def get_property_units(db: Session, property_id: int) -> list[PropertyUnit]:
    return db.query(PropertyUnit).filter(PropertyUnit.property_id == property_id, PropertyUnit.is_active == True).all()