from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.saved import SavedItem
from app.models.property import Property
from app.models.tour import Tour
from app.schemas.saved import SavedItemResponse
from app.schemas.common import DataResponse

router = APIRouter()


@router.get("/", response_model=DataResponse[list[SavedItemResponse]])
def get_saved(
    item_type: str = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Мои сохранённые."""
    query = db.query(SavedItem).filter(SavedItem.user_id == user.id)
    if item_type:
        query = query.filter(SavedItem.item_type == item_type)
    items = query.order_by(SavedItem.created_at.desc()).all()

    result = []
    for item in items:
        si = SavedItemResponse(
            id=item.id,
            item_type=item.item_type,
            item_id=item.item_id,
            created_at=item.created_at,
        )
        if item.item_type == "property":
            prop = db.query(Property).filter(Property.id == item.item_id).first()
            if prop:
                # Получаем минимальную цену
                from app.models.property_unit import PropertyUnit
                min_price = db.query(PropertyUnit.base_price).filter(
                    PropertyUnit.property_id == prop.id, PropertyUnit.is_active == True
                ).order_by(PropertyUnit.base_price.asc()).first()
                price_text = f"{min_price[0]:,.0f} UZS" if min_price else "Free"

                si.property = {
                    "id": prop.id,
                    "name_en": prop.name_en,
                    "name_uz": prop.name_uz,
                    "name_ru": prop.name_ru,
                    "property_type": prop.property_type,
                    "cover_url": prop.cover_url,
                    "address": prop.address,
                    "rating_guest": prop.rating_guest,
                    "price_text": price_text,
                }
        elif item.item_type == "tour":
            tour = db.query(Tour).filter(Tour.id == item.item_id).first()
            if tour:
                si.tour = {
                    "id": tour.id,
                    "name_en": tour.name_en,
                    "name_uz": tour.name_uz,
                    "name_ru": tour.name_ru,
                    "cover_url": tour.cover_url,
                    "duration_days": tour.duration_days,
                    "transport_type": tour.transport_type,
                }
        result.append(si)

    return DataResponse(data=result)


@router.post("/", response_model=DataResponse)
def save_item(
    item_type: str,
    item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Сохранить место или тур."""
    if item_type not in ("property", "tour"):
        raise HTTPException(status_code=400, detail="item_type must be 'property' or 'tour'")

    exists = db.query(SavedItem).filter(
        SavedItem.user_id == user.id,
        SavedItem.item_type == item_type,
        SavedItem.item_id == item_id,
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Already saved")

    item = SavedItem(user_id=user.id, item_type=item_type, item_id=item_id)
    db.add(item)
    db.commit()
    return DataResponse(data={"id": item.id, "item_type": item.item_type, "item_id": item.item_id}, message="Saved")


@router.delete("/{saved_id}", response_model=DataResponse)
def remove_saved(
    saved_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Удалить из сохранённого."""
    item = db.query(SavedItem).filter(SavedItem.id == saved_id, SavedItem.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return DataResponse(message="Removed")