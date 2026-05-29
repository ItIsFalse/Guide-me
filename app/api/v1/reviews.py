from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.review import ReviewCreateRequest, ReviewResponse, ReviewListResponse
from app.schemas.common import DataResponse
from app.services.review_service import get_reviews, create_review
from app.models.review import Review

router = APIRouter()


@router.get("/property/{property_id}", response_model=ReviewListResponse)
def list_reviews(property_id: int, db: Session = Depends(get_db)):
    """Все отзывы объекта."""
    reviews, rating_uz, rating_guest = get_reviews(db, property_id)
    return ReviewListResponse(
        data=[ReviewResponse.model_validate(r) for r in reviews],
        total=len(reviews),
        rating_uz=rating_uz,
        rating_guest=rating_guest,
    )


@router.post("/", response_model=DataResponse[ReviewResponse])
def add_review(
    data: ReviewCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Оставить отзыв или ответ."""
    if not data.parent_id and (data.rating < 1 or data.rating > 5):
        raise HTTPException(status_code=400, detail="Rating must be 1-5")
    review = create_review(db, user, data.model_dump())
    return DataResponse(data=ReviewResponse.model_validate(review), message="Review added")

@router.get("/my", response_model=DataResponse[list[ReviewResponse]])
def my_reviews(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Все отзывы текущего пользователя."""
    reviews = (
        db.query(Review)
        .filter(Review.user_id == user.id, Review.is_active == True)
        .order_by(Review.created_at.desc())
        .all()
    )
    return DataResponse(data=[ReviewResponse.model_validate(r) for r in reviews])