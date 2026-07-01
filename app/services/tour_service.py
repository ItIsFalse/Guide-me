from sqlalchemy.orm import Session, joinedload  # <--- добавили joinedload
from sqlalchemy import func
from app.models.tour import Tour, TourStop, UserTourExpense
from app.models.region import Region
from app.models.property import Property
from app.models.user import User
from app.schemas.tour import TourCreateRequest
from fastapi import HTTPException


def get_tours(
    db: Session,
    region_id: int | None = None,
    is_template: bool = True,
    page: int = 1,
    page_size: int = 20,
):
    query = db.query(Tour).filter(Tour.is_active == True, Tour.is_template == is_template)
    if region_id:
        query = query.filter(Tour.region_id == region_id)

    total = query.count()
    tours = query.offset((page - 1) * page_size).limit(page_size).all()
    return tours, total


def get_tour_by_id(db: Session, tour_id: int) -> Tour | None:
    return db.query(Tour).filter(
        Tour.id == tour_id,
        Tour.is_active == True
    ).options(joinedload(Tour.stops)).first()   # <--- ИСПРАВЛЕНО


def create_tour(db: Session, user: User, data: TourCreateRequest) -> Tour:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create tour packages")

    if data.property_ids:
        count = db.query(Property).filter(
            Property.id.in_(data.property_ids),
            Property.is_active == True,
        ).count()
        if count != len(data.property_ids):
            raise HTTPException(status_code=400, detail="Some properties not found or inactive")

    tour = Tour(
        region_id=data.region_id,
        creator_id=user.id,
        name_en=data.name_en,
        name_uz=data.name_uz,
        name_ru=data.name_ru,
        description_en=data.description_en,
        duration_days=data.duration_days,
        transport_type=data.transport_type,
        is_template=True,
    )
    db.add(tour)
    db.flush()

    for i, prop_id in enumerate(data.property_ids):
        stop = TourStop(
            tour_id=tour.id,
            property_id=prop_id,
            stop_order=i + 1,
            duration_minutes=60,
        )
        db.add(stop)

    db.commit()
    db.refresh(tour)
    return tour


def save_tour_expense(db: Session, user_id: int, data: dict) -> UserTourExpense:
    expense = UserTourExpense(
        user_id=user_id,
        tour_id=data.get("tour_id"),
        region_id=data.get("region_id"),
        total_spent=data.get("total_spent", 0),
        accommodation_spent=data.get("accommodation_spent", 0),
        food_spent=data.get("food_spent", 0),
        transport_spent=data.get("transport_spent", 0),
        entertainment_spent=data.get("entertainment_spent", 0),
        other_spent=data.get("other_spent", 0),
        currency=data.get("currency", "UZS"),
        comment=data.get("comment"),
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    _update_tour_averages(db, data.get("tour_id"))
    return expense


def _update_tour_averages(db: Session, tour_id: int | None):
    if not tour_id:
        return

    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        return

    result = db.query(
        func.avg(UserTourExpense.total_spent).label("avg_total"),
        func.avg(UserTourExpense.accommodation_spent).label("avg_acc"),
        func.avg(UserTourExpense.food_spent).label("avg_food"),
        func.avg(UserTourExpense.transport_spent).label("avg_trans"),
        func.avg(UserTourExpense.entertainment_spent).label("avg_ent"),
    ).filter(UserTourExpense.tour_id == tour_id).first()

    if result and result.avg_total:
        tour.avg_total_cost = round(result.avg_total, 2)
        tour.avg_accommodation_cost = round(result.avg_acc or 0, 2)
        tour.avg_food_cost = round(result.avg_food or 0, 2)
        tour.avg_transport_cost = round(result.avg_trans or 0, 2)
        tour.avg_entertainment_cost = round(result.avg_ent or 0, 2)
        db.commit()


def get_region_averages(db: Session) -> list[dict]:
    results = (
        db.query(
            UserTourExpense.region_id,
            func.count(UserTourExpense.id).label("total_reports"),
            func.avg(UserTourExpense.total_spent).label("avg_total"),
            func.avg(UserTourExpense.accommodation_spent).label("avg_acc"),
            func.avg(UserTourExpense.food_spent).label("avg_food"),
            func.avg(UserTourExpense.transport_spent).label("avg_trans"),
            func.avg(UserTourExpense.entertainment_spent).label("avg_ent"),
        )
        .filter(UserTourExpense.region_id.isnot(None))
        .group_by(UserTourExpense.region_id)
        .all()
    )

    regions = {r.id: r.name_en for r in db.query(Region).all()}
    return [
        {
            "region_id": r.region_id,
            "region_name": regions.get(r.region_id, "Unknown"),
            "total_reports": r.total_reports,
            "avg_total": round(r.avg_total or 0, 2),
            "avg_accommodation": round(r.avg_acc or 0, 2),
            "avg_food": round(r.avg_food or 0, 2),
            "avg_transport": round(r.avg_trans or 0, 2),
            "avg_entertainment": round(r.avg_ent or 0, 2),
        }
        for r in results
    ]