from sqlalchemy.orm import Session
from app.models.photo import Photo
from app.schemas.photo import PhotoCreateRequest
from fastapi import HTTPException


def get_photos_by_entity(db: Session, entity_type: str, entity_id: int) -> list[Photo]:
    """Получить все фото для сущности."""
    return db.query(Photo).filter(
        Photo.entity_type == entity_type,
        Photo.entity_id == entity_id
    ).order_by(Photo.sort_order).all()


def add_photo(db: Session, data: PhotoCreateRequest) -> Photo:
    """Добавить фото для сущности."""
    photo = Photo(
        entity_type=data.entity_type,
        entity_id=data.entity_id,
        photo_url=data.photo_url,
        sort_order=data.sort_order,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def delete_photo(db: Session, photo_id: int) -> bool:
    """Удалить фото."""
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    db.delete(photo)
    db.commit()
    return True