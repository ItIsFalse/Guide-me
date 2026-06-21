from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.tour import (
    TourResponse, TourDetailResponse, TourCreateRequest,
    TourExpenseRequest, TourExpenseResponse, TourAverageResponse,
    NavigationStepResponse, )
from app.schemas.common import DataResponse
from app.services.tour_service import (
    get_tours, get_tour_by_id, create_tour,
    save_tour_expense, get_region_averages,
)
from app.services.navigation_service import calculate_navigation
from datetime import datetime
from app.models.tour import TourStop
from app.models.property import Property
from app.schemas.tour import TourStopPropertyBrief
from app.models.property_unit import PropertyUnit

router = APIRouter()


@router.get("/", response_model=DataResponse[list[TourResponse]])
def list_tours(
        region_id: Optional[int] = Query(None),
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db),
):
    """Список готовых тур-пакетов."""
    tours, total = get_tours(db, region_id=region_id, is_template=True, page=page, page_size=page_size)
    return DataResponse(
        data=[TourResponse.model_validate(t) for t in tours],
        message=f"Found {total} tours",
    )


@router.get("/{tour_id}", response_model=DataResponse[TourDetailResponse])
def get_tour(tour_id: int, db: Session = Depends(get_db)):
    """Детали тура с остановками и информацией о местах."""
    tour = get_tour_by_id(db, tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    result = TourDetailResponse.model_validate(tour)

    # Добавляем property в каждый stop
    for stop in result.stops:
        prop = db.query(Property).filter(Property.id == stop.property_id).first()
        if prop:
            # Считаем минимальную цену
            min_price = db.query(PropertyUnit.base_price).filter(
                PropertyUnit.property_id == prop.id,
                PropertyUnit.is_active == True
            ).order_by(PropertyUnit.base_price.asc()).first()

            price_text = f"{min_price[0]:,.0f} UZS" if min_price else "Free"

            stop.property = TourStopPropertyBrief(
                id=prop.id,
                name_en=prop.name_en,
                name_uz=prop.name_uz,
                name_ru=prop.name_ru,
                property_type=prop.property_type,
                cover_url=prop.cover_url,
                rating_guest=prop.rating_guest,
                description_en=prop.description_en,
                price_text=price_text,
                lat=prop.lat,
                lon=prop.lon,
            )

    return DataResponse(data=result)


@router.post("/", response_model=DataResponse[TourDetailResponse])
def create_new_tour(
        data: TourCreateRequest,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    """Создать свой маршрут."""
    tour = create_tour(db, user, data)
    return DataResponse(data=TourDetailResponse.model_validate(tour), message="Tour created")


@router.get("/{tour_id}/navigation", response_model=DataResponse[list[NavigationStepResponse]])
def get_navigation(tour_id: int, db: Session = Depends(get_db)):
    """Пошаговая навигация по туру."""
    tour = get_tour_by_id(db, tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    steps = calculate_navigation(db, tour)
    return DataResponse(data=steps, message=f"Navigation: {len(steps)} steps")


@router.post("/expenses", response_model=DataResponse[TourExpenseResponse])
def add_expense(
        data: TourExpenseRequest,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    """Записать траты после тура."""
    expense = save_tour_expense(db, user.id, data.model_dump())
    return DataResponse(data=TourExpenseResponse.model_validate(expense), message="Expense recorded")


@router.get("/averages/regions", response_model=DataResponse[list[TourAverageResponse]])
def region_averages(db: Session = Depends(get_db)):
    """Средние траты туристов по областям."""
    averages = get_region_averages(db)
    return DataResponse(data=averages, message=f"Averages for {len(averages)} regions")


@router.patch("/{tour_id}/transport", response_model=DataResponse[TourDetailResponse])
def update_tour_transport(
        tour_id: int,
        transport_type: str,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    """Сменить транспорт в туре."""
    tour = get_tour_by_id(db, tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    if transport_type not in ("walking", "public", "car", "bicycle"):
        raise HTTPException(status_code=400, detail="Invalid transport type")

    tour.transport_type = transport_type
    tour.updated_at = datetime.utcnow()
    db.commit()

    return DataResponse(data=TourDetailResponse.model_validate(tour), message=f"Transport updated to {transport_type}")


@router.patch("/{tour_id}/stops/{stop_id}", response_model=DataResponse[TourDetailResponse])
def replace_tour_stop(
        tour_id: int,
        stop_id: int,
        new_property_id: int,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    """Заменить место в туре на другое."""
    # 1. Проверяем что тур существует
    tour = get_tour_by_id(db, tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    # 2. Проверяем что остановка в этом туре
    stop = db.query(TourStop).filter(TourStop.id == stop_id, TourStop.tour_id == tour_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")

    # 3. Проверяем что новое место существует
    new_prop = db.query(Property).filter(Property.id == new_property_id, Property.is_active == True).first()
    if not new_prop:
        raise HTTPException(status_code=404, detail="New property not found")

    # 4. Заменяем
    stop.property_id = new_property_id
    db.commit()
    db.refresh(tour)

    return DataResponse(data=TourDetailResponse.model_validate(tour), message=f"Stop replaced with {new_prop.name_en}")
