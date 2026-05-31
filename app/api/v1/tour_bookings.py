from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tour import Tour
from app.models.tour_booking import TourBooking
from app.schemas.tour_booking import TourBookingRequest, TourBookingResponse
from app.schemas.common import DataResponse

router = APIRouter()


@router.post("/tours/{tour_id}/book", response_model=DataResponse[TourBookingResponse])
def book_tour(
    tour_id: int,
    request: TourBookingRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Забронировать тур."""
    tour = db.query(Tour).filter(Tour.id == tour_id, Tour.is_active == True).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    # Базовая цена (можно улучшить логику)
    base_price = tour.avg_total_cost if tour.avg_total_cost > 0 else 500000
    total = base_price * request.duration_days

    # Промокод (простая логика)
    discount = 0.0
    if request.promo_code:
        if request.promo_code.upper() == "GUIDEME":
            discount = total * 0.1  # 10% скидка
        elif request.promo_code.upper() == "WELCOME":
            discount = total * 0.15  # 15% скидка

    total_price = total - discount

    booking = TourBooking(
        tour_id=tour_id,
        user_id=user.id,
        transport_type=request.transport_type,
        duration_days=request.duration_days,
        total_price=total_price,
        discount_applied=discount,
        promo_code=request.promo_code,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    return DataResponse(data=TourBookingResponse.model_validate(booking), message="Tour booked successfully")