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
TARGET_CURRENCIES = {"USD", "EUR"}  # Только доллар и евро


def fetch_and_save_rates(db: Session):
    """Загружает курсы из API ЦБ если нет данных за сегодня."""
    today = date.today()

    # Проверяем есть ли курс за сегодня
    existing = db.query(ExchangeRate).filter(
        ExchangeRate.date == today
    ).first()

    if existing:
        return  # сегодня уже обновляли

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

        # Удаляем записи старше 30 дней (после добавления новых)
        oldest = today - timedelta(days=20)
        db.query(ExchangeRate).filter(ExchangeRate.date < oldest).delete()

        db.commit()
    except Exception as e:
        print(f"Failed to fetch rates: {e}")
        db.rollback()


@router.get("/", response_model=DataResponse)
def get_latest_rates(db: Session = Depends(get_db)):
    """Последние курсы валют в формате {USD: 12750.0, EUR: 13967.87}."""
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

    # Возвращаем как словарь
    result = {r.currency_code: r.rate for r in rates}
    result["UZS"] = 1.0

    return DataResponse(data=result, message="Latest exchange rates")