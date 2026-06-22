from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.photo import PhotoResponse, PhotoCreateRequest
from app.schemas.common import DataResponse
from app.services.photo_service import get_photos_by_entity, add_photo, delete_photo

router = APIRouter()


@router.get("/{entity_type}/{entity_id}", response_model=DataResponse[list[PhotoResponse]])
def get_photos(
        entity_type: str,
        entity_id: int,
        db: Session = Depends(get_db),
):
    """Получить все фото для сущности (region, property, property_unit)."""
    if entity_type not in ["region", "property", "property_unit"]:
        raise HTTPException(status_code=400, detail="Invalid entity_type")

    photos = get_photos_by_entity(db, entity_type, entity_id)
    return DataResponse(
        data=[PhotoResponse.model_validate(p) for p in photos],
        message=f"Found {len(photos)} photos"
    )


@router.post("/", response_model=DataResponse[PhotoResponse])
def create_photo(
        data: PhotoCreateRequest,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    """Добавить фото (только для админов)."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    photo = add_photo(db, data)
    return DataResponse(
        data=PhotoResponse.model_validate(photo),
        message="Photo added successfully"
    )


@router.delete("/{photo_id}", response_model=DataResponse)
def remove_photo(
        photo_id: int,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    """Удалить фото (только для админов)."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    delete_photo(db, photo_id)
    return DataResponse(message="Photo deleted successfully")