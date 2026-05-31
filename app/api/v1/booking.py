from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user, get_current_owner
from app.models.user import User
from app.models.booking import BookingRequest
from app.models.property import Property
from app.schemas.booking import BookingRequestCreate, BookingRequestResponse, BookingPropertyBrief
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
    bookings = (
        db.query(BookingRequest)
        .filter(BookingRequest.user_id == user.id)
        .order_by(BookingRequest.created_at.desc())
        .all()
    )
    result = []
    for b in bookings:
        br = BookingRequestResponse.model_validate(b)
        if b.property_id:
            prop = db.query(Property).filter(Property.id == b.property_id).first()
            if prop:
                br.property = BookingPropertyBrief.model_validate(prop)
        result.append(br)
    return DataResponse(data=result)


@router.get("/owner", response_model=DataResponse[list[BookingRequestResponse]])
def get_owner_bookings(
        user: User = Depends(get_current_owner),
        db: Session = Depends(get_db),
):
    """Владелец видит заявки на свои объекты."""
    bookings = (
        db.query(BookingRequest)
        .join(Property, BookingRequest.property_id == Property.id)
        .filter(Property.owner_id == user.id)
        .order_by(BookingRequest.created_at.desc())
        .all()
    )
    result = []
    for b in bookings:
        br = BookingRequestResponse.model_validate(b)
        if b.property_id:
            prop = db.query(Property).filter(Property.id == b.property_id).first()
            if prop:
                br.property = BookingPropertyBrief.model_validate(prop)
        result.append(br)
    return DataResponse(data=result)


@router.put("/{booking_id}/status", response_model=DataResponse[BookingRequestResponse])
def update_booking_status(
        booking_id: int,
        status: str,
        user: User = Depends(get_current_owner),
        db: Session = Depends(get_db),
):
    """Сменить статус заявки."""
    if status not in ("pending", "contacted", "confirmed", "cancelled", "rejected"):
        raise HTTPException(status_code=400, detail="Invalid status")

    booking = db.query(BookingRequest).filter(BookingRequest.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    prop = db.query(Property).filter(Property.id == booking.property_id).first()
    if prop.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your property")

    booking.status = status
    booking.updated_at = datetime.utcnow()
    db.commit()

    br = BookingRequestResponse.model_validate(booking)
    if booking.property_id and prop:
        br.property = BookingPropertyBrief.model_validate(prop)

    return DataResponse(data=br, message=f"Status updated to {status}")