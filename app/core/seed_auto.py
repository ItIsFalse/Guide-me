from app.core.database import SessionLocal
from app.models.region import Region


def auto_seed():
    """Автоматически загружает данные если БД пустая."""
    db = SessionLocal()
    try:
        if db.query(Region).count() == 0:
            from scripts.seed_data import seed
            seed()
            print("✅ Auto-seeded database")
        else:
            print("✅ Database already populated")
    finally:
        db.close()