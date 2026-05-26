from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.ai import AIQueryRequest, AIResponse, AIPropertySuggestion
from app.services.ai_service import (
    search_properties, build_rich_prompt, ask_groq, generate_simple_reply
)
from app.services.weather_service import get_weather
from app.services.entity_service import (
    detect_language, extract_entities_ru, extract_entities_en, extract_entities_uz
)

router = APIRouter()


@router.post("/", response_model=AIResponse)
async def ai_chat(request: AIQueryRequest, db: Session = Depends(get_db)):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")

    # 1. Определяем язык
    lang = detect_language(request.message)

    # 2. Извлекаем сущности
    if lang == "ru":
        entities = extract_entities_ru(request.message)
    elif lang == "uz":
        entities = extract_entities_uz(request.message)
    else:
        entities = extract_entities_en(request.message)

    # 3. Бюджет из запроса
    if request.budget and request.budget > 0:
        entities["budget"] = request.budget

    # 4. Погода
    weather = None
    if request.lat and request.lon:
        weather = await get_weather(request.lat, request.lon)

    # 5. Поиск мест
    suggestions = search_properties(db, entities, limit=5)

    # 6. Промпт и ответ
    prompt = build_rich_prompt(request.message, suggestions, weather, lang)
    try:
        reply = await ask_groq(prompt)
    except Exception:
        reply = generate_simple_reply(request.message, suggestions, weather, lang)

    # 7. Формируем suggestions
    ai_suggestions = [
        AIPropertySuggestion(
            id=s["id"],
            name=s["name"],
            property_type=s["property_type"],
            description=s["description"],
            price_text=s["price_text"],
            rating=s["rating"],
            region=s["region"],
        )
        for s in suggestions
    ]

    return AIResponse(reply=reply, weather=weather, suggestions=ai_suggestions)