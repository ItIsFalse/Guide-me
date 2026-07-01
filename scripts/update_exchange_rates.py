import sys
sys.path.insert(0, ".")

import requests
from datetime import datetime
from app.core.database import SessionLocal, init_db
from app.models.exchange_rate import ExchangeRate

API_URL = "https://cbu.uz/ru/arkhiv-kursov-valyut/json/"

# Какие валюты сохраняем
TARGET_CURRENCIES = {"USD", "EUR", "RUB"}


def update_rates():
    init_db()
    db = SessionLocal()

    try:
        print(f"[{datetime.now()}] Fetching rates from CBU...")
        response = requests.get(API_URL, timeout=15)
        data = response.json()

        if not data:
            print("Empty response from API")
            return

        # Берём самые свежие записи для каждой валюты
        seen = set()
        fresh = []
        for item in data:
            code = item.get("Ccy")
            if code in TARGET_CURRENCIES and code not in seen:
                seen.add(code)
                fresh.append(item)

        print(f"Found {len(fresh)} currencies")

        # Сохраняем в БД
        for curr in fresh:
            rate_obj = ExchangeRate(
                currency_code=curr["Ccy"],
                nominal=int(curr["Nominal"]),
                rate=float(curr["Rate"]),
                date=datetime.strptime(curr["Date"], "%d.%m.%Y").date(),
                name_uz=curr.get("CcyNm_UZ", curr["Ccy"]),
            )
            db.add(rate_obj)

        db.commit()

        # Показываем USD
        usd = next((c for c in fresh if c["Ccy"] == "USD"), None)
        if usd:
            rate = float(usd["Rate"])
            print(f"💵 1 USD = {rate:,.2f} UZS")
            print(f"💱 1200 UZS = {1200/rate:.4f} USD")

        print(f"✅ Updated {len(fresh)} currencies")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    update_rates()