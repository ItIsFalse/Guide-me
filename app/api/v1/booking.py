from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.booking import BookingRequest
from app.schemas.booking import BookingRequestCreate, BookingRequestResponse
from app.schemas.common import DataResponse

router = APIRouter()


@router.post("/", response_model=DataResponse[BookingRequestResponse])
def create_booking_request(
    data: BookingRequestCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Создать запрос на связь (придержать)."""
    booking = BookingRequest(
        user_id=user.id,
        unit_id=data.unit_id,
        property_id=data.property_id,
        check_in_date=data.check_in_date,
        check_out_date=data.check_out_date,
        rooms=data.rooms,
        guests=data.guests,
        message=data.message,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return DataResponse(
        data=BookingRequestResponse.model_validate(booking),
        message="Request sent. Owner will contact you.",
    )


@router.get("/", response_model=DataResponse[list[BookingRequestResponse]])
def get_my_requests(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Мои запросы."""
    bookings = db.query(BookingRequest).filter(BookingRequest.user_id == user.id).order_by(BookingRequest.created_at.desc()).all()
    return DataResponse(data=[BookingRequestResponse.model_validate(b) for b in bookings])