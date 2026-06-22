from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.review import Review
from app.models.saved import SavedItem
from app.models.tour_booking import TourBooking
from app.schemas.common import DataResponse
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/me", response_model=DataResponse[UserResponse])
def get_me(
    user: User = Depends(get_current_user),
):
    """Получить профиль текущего пользователя."""
    return DataResponse(data=UserResponse.model_validate(user))


@router.get("/me/stats", response_model=DataResponse)
def my_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Статистика пользователя."""
    total_reviews = db.query(func.count(Review.id)).filter(
        Review.user_id == user.id, Review.is_active == True
    ).scalar() or 0

    total_saved = db.query(func.count(SavedItem.id)).filter(
        SavedItem.user_id == user.id
    ).scalar() or 0

    total_bookings = db.query(func.count(TourBooking.id)).filter(
        TourBooking.user_id == user.id,
        TourBooking.is_active == True
    ).scalar() or 0

    return DataResponse(data={
        "total_reviews": total_reviews,
        "total_saved": total_saved,
        "total_bookings": total_bookings,
    })