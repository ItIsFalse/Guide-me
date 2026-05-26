from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.review import Review
from app.models.property import Property
from app.models.user import User
from fastapi import HTTPException


def get_reviews(db: Session, property_id: int) -> tuple[list[Review], float, float]:
    """Все отзывы свойства + средние рейтинги."""
    reviews = (
        db.query(Review)
        .filter(Review.property_id == property_id, Review.is_active == True)
        .order_by(Review.created_at.desc())
        .all()
    )

    # Средние рейтинги
    resident_avg = db.query(func.avg(Review.rating)).filter(
        Review.property_id == property_id,
        Review.is_active == True,
        Review.is_from_resident == True,
        Review.parent_id.is_(None),
    ).scalar()

    guest_avg = db.query(func.avg(Review.rating)).filter(
        Review.property_id == property_id,
        Review.is_active == True,
        Review.is_from_resident == False,
        Review.parent_id.is_(None),
    ).scalar()

    return reviews, round(resident_avg or 0, 1), round(guest_avg or 0, 1)


def create_review(db: Session, user: User, data: dict) -> Review:
    # Если это ответ (parent_id есть), то только owner или admin
    if data.get("parent_id"):
        parent = db.query(Review).filter(Review.id == data["parent_id"]).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent review not found")

        property = db.query(Property).filter(Property.id == parent.property_id).first()
        if user.role not in ("owner", "admin") or (user.role == "owner" and property.owner_id != user.id):
            raise HTTPException(status_code=403, detail="Only property owner can reply")

    # Гость не может оставить больше одного отзыва на свойство (кроме ответов)
    if not data.get("parent_id"):
        existing = db.query(Review).filter(
            Review.user_id == user.id,
            Review.property_id == data["property_id"],
            Review.parent_id.is_(None),
        ).first()
        if existing and user.role == "guest":
            raise HTTPException(status_code=400, detail="You already reviewed this property")

    review = Review(
        user_id=user.id,
        property_id=data["property_id"],
        parent_id=data.get("parent_id"),
        rating=data.get("rating") if not data.get("parent_id") else None,
        text_en=data.get("text_en"),
        text_uz=data.get("text_uz"),
        text_ru=data.get("text_ru"),
        is_from_resident=(user.role == "resident"),
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    # Обновляем кэш рейтингов в property
    _update_property_ratings(db, data["property_id"])

    return review


def _update_property_ratings(db: Session, property_id: int):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        return

    rating_uz = db.query(func.avg(Review.rating)).filter(
        Review.property_id == property_id,
        Review.is_active == True,
        Review.is_from_resident == True,
        Review.parent_id.is_(None),
    ).scalar()

    rating_guest = db.query(func.avg(Review.rating)).filter(
        Review.property_id == property_id,
        Review.is_active == True,
        Review.is_from_resident == False,
        Review.parent_id.is_(None),
    ).scalar()

    total = db.query(func.count(Review.id)).filter(
        Review.property_id == property_id,
        Review.is_active == True,
        Review.parent_id.is_(None),
    ).scalar()

    property.rating_uz = round(rating_uz or 0, 1)
    property.rating_guest = round(rating_guest or 0, 1)
    property.total_reviews = total or 0
    db.commit()