from datetime import date, datetime, timedelta
import requests
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.exchange_rate import ExchangeRate
from app.schemas.common import DataResponse

router = APIRouter()
API_URL = "https://cbu.uz/ru/arkhiv-kursov-valyut/json/"
TARGET_CURRENCIES = {"USD", "EUR", "RUB", "GBP", "CNY"}


def fetch_and_save_rates(db: Session):
    """Загружает курсы из API ЦБ если нет свежих данных."""
    today = date.today()
    yesterday = today - timedelta(days=1)

    existing = db.query(ExchangeRate).filter(
        ExchangeRate.date >= yesterday
    ).first()

    if existing:
        return  # курс актуальный

    try:
        response = requests.get(API_URL, timeout=10)
        data = response.json()
        seen = set()
        for item in data:
            code = item.get("Ccy")
            if code in TARGET_CURRENCIES and code not in seen:
                seen.add(code)
                rate = ExchangeRate(
                    currency_code=code,
                    nominal=int(item["Nominal"]),
                    rate=float(item["Rate"]),
                    date=datetime.strptime(item["Date"], "%d.%m.%Y").date(),
                    name_uz=item.get("CcyNm_UZ", code),
                )
                db.add(rate)
        db.commit()
    except Exception as e:
        print(f"Failed to fetch rates: {e}")


@router.get("/", response_model=DataResponse)
def get_latest_rates(db: Session = Depends(get_db)):
    """Последние курсы валют (автообновление раз в день)."""
    fetch_and_save_rates(db)

    subquery = (
        db.query(
            ExchangeRate.currency_code,
            func.max(ExchangeRate.date).label("max_date")
        )
        .group_by(ExchangeRate.currency_code)
        .subquery()
    )

    rates = (
        db.query(ExchangeRate)
        .join(
            subquery,
            (ExchangeRate.currency_code == subquery.c.currency_code) &
            (ExchangeRate.date == subquery.c.max_date)
        )
        .all()
    )

    result = [
        {
            "currency": r.currency_code,
            "nominal": r.nominal,
            "rate": r.rate,
            "date": str(r.date),
            "name_uz": r.name_uz,
        }
        for r in rates
    ]

    return DataResponse(data=result, message=f"Exchange rates for {len(result)} currencies")