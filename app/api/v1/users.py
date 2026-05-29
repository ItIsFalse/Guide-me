from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.review import Review
from app.schemas.common import DataResponse

router = APIRouter()


@router.get("/me/stats", response_model=DataResponse)
def my_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Статистика пользователя."""
    total_reviews = db.query(func.count(Review.id)).filter(
        Review.user_id == user.id, Review.is_active == True
    ).scalar() or 0

    return DataResponse(data={
        "total_reviews": total_reviews,
    })