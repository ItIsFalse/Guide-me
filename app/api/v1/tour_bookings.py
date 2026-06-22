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
    # 1. Проверяем что тур существует
    tour = db.query(Tour).filter(Tour.id == tour_id, Tour.is_active == True).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    # 2. Проверяем нет ли уже активного тура у пользователя
    existing_booking = db.query(TourBooking).filter(
        TourBooking.user_id == user.id,
        TourBooking.status.in_(["pending", "confirmed"]),
        TourBooking.is_active == True
    ).first()

    if existing_booking:
        raise HTTPException(
            status_code=400,
            detail="You already have an active tour. Complete or cancel it first."
        )

    # 3. Расчет цены
    base_price = tour.avg_total_cost if tour.avg_total_cost > 0 else 500000
    total = base_price * request.duration_days

    # 4. Промокод
    discount = 0.0
    if request.promo_code:
        if request.promo_code.upper() == "GUIDEME":
            discount = total * 0.1
        elif request.promo_code.upper() == "WELCOME":
            discount = total * 0.15

    total_price = total - discount

    # 5. Создаем бронь со статусом "confirmed"
    booking = TourBooking(
        tour_id=tour_id,
        user_id=user.id,
        transport_type=request.transport_type,
        duration_days=request.duration_days,
        total_price=total_price,
        discount_applied=discount,
        promo_code=request.promo_code,
        status="confirmed",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    return DataResponse(
        data=TourBookingResponse.model_validate(booking),
        message="Tour started successfully!"
    )