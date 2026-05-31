from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.models.promo_code import PromoCode
from app.schemas.promo import PromoValidateRequest, PromoValidateResponse

router = APIRouter()


@router.post("/validate", response_model=PromoValidateResponse)
def validate_promo(
    request: PromoValidateRequest,
    db: Session = Depends(get_db),
):
    """Проверить промокод."""
    promo = db.query(PromoCode).filter(
        PromoCode.code == request.code.upper(),
        PromoCode.is_active == True,
    ).first()

    if not promo:
        return PromoValidateResponse(valid=False)

    # Проверка срока
    if promo.expires_at and promo.expires_at < datetime.utcnow():
        return PromoValidateResponse(valid=False, description="Promo code expired")

    # Проверка лимита
    if promo.used_count >= promo.max_uses:
        return PromoValidateResponse(valid=False, description="Promo code usage limit reached")

    return PromoValidateResponse(
        valid=True,
        discount_percent=promo.discount_percent,
        description=promo.description,
    )