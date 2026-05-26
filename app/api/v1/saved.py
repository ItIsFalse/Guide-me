from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.saved import SavedItem
from app.schemas.common import DataResponse

router = APIRouter()


@router.get("/", response_model=DataResponse)
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
    return DataResponse(data=[{"id": i.id, "item_type": i.item_type, "item_id": i.item_id} for i in items])


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
    return DataResponse(message="Saved")


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