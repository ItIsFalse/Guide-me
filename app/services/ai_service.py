import asyncio
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.config import settings
from app.models.property import Property
from app.models.property_unit import PropertyUnit
from app.models.region import Region
from app.models.property_tag import PropertyTag
from app.services.entity_service import detect_language, extract_entities_ru, extract_entities_en, extract_entities_uz


def build_message_content(prompt: str, image_base64: str | None = None) -> list[dict]:
    """Строит контент сообщения с опциональным изображением."""
    content = [{"type": "text", "text": prompt}]
    if image_base64:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
        })
    return content


def search_properties(db: Session, entities: dict, limit: int = 10) -> list[dict]:
    """Умный поиск мест с учётом тегов, типа, бюджета, города."""
    query = db.query(Property).filter(
        Property.is_active == True,
        Property.moderation_status == "approved",
    )

    if entities.get("city"):
        region = db.query(Region).filter(Region.name_en == entities["city"]).first()
        if region:
            print(f"Found region: {region.name_en}, id={region.id}")
            query = query.filter(Property.region_id == region.id)
        else:
            region = db.query(Region).filter(Region.name_ru.ilike(f"%{entities['city']}%")).first()
            if region:
                print(f"Found by Russian name: {region.name_en}")
                query = query.filter(Property.region_id == region.id)

    if entities.get("type"):
        query = query.filter(Property.property_type == entities["type"])

    if entities.get("stars"):
        query = query.filter(Property.stars >= entities["stars"])

    base_query = query

    if entities.get("tags"):
        tag_filters = []
        for tag in entities["tags"]:
            tag_filters.append(Property.tags.any(PropertyTag.tag == tag))
        if tag_filters:
            query = query.filter(or_(*tag_filters))

    results = query.limit(limit * 2).all()

    if not results and entities.get("tags"):
        results = base_query.limit(limit * 2).all()

    suggestions = []
    for prop in results:
        min_price = (
            db.query(PropertyUnit.base_price)
            .filter(PropertyUnit.property_id == prop.id, PropertyUnit.is_active == True)
            .order_by(PropertyUnit.base_price.asc())
            .first()
        )
        price_value = min_price[0] if min_price else 0

        if entities.get("budget") and price_value > entities["budget"]:
            continue

        region = db.query(Region).filter(Region.id == prop.region_id).first()
        price_text = f"{price_value:,.0f} UZS" if price_value > 0 else "Free"
        tags = [t.tag for t in prop.tags] if prop.tags else []

        suggestions.append({
            "id": prop.id,
            "name": prop.name_en,
            "name_uz": prop.name_uz or prop.name_en,
            "name_ru": prop.name_ru or prop.name_en,
            "property_type": prop.property_type,
            "description": (prop.description_en or "")[:200],
            "description_uz": (prop.description_uz or "")[:200],
            "description_ru": (prop.description_ru or "")[:200],
            "price_text": price_text,
            "price_value": price_value,
            "rating": prop.rating_guest,
            "rating_uz": prop.rating_uz,
            "total_reviews": prop.total_reviews,
            "region": region.name_en if region else "",
            "stars": prop.stars,
            "tags": tags,
            "has_wifi": prop.has_wifi,
            "has_pool": prop.has_pool,
            "has_parking": prop.has_parking,
            "has_breakfast": prop.has_breakfast,
            "cuisine_type": prop.cuisine_type,
        })

        if len(suggestions) >= limit:
            break

    return suggestions


def build_rich_prompt(message: str, suggestions: list[dict], weather: dict | None, lang: str) -> str:
    """Строит подробный промпт для Groq."""
    system_prompts = {
        "ru": "Ты — дружелюбный AI-гид по Узбекистану. Помогаешь туристам находить отели, музеи, рестораны. Отвечай кратко, полезно, на русском языке.",
        "uz": "Siz O'zbekiston bo'yicha do'stona AI-gidsiz. Sayyohlarga mehmonxonalar, muzeylar, restoranlar topishda yordam berasiz. Qisqa, foydali va o'zbek tilida javob bering.",
        "en": "You are a friendly AI guide for Uzbekistan. Help tourists find hotels, museums, restaurants. Answer concisely in English.",
    }

    system = system_prompts.get(lang, system_prompts["en"])

    context = ""
    if suggestions:
        context = "Available places from database:\n"
        for s in suggestions:
            stars_str = f"⭐{s['stars']}" if s['stars'] else ""
            context += f"""
- {s['name']} ({s['property_type']}) {stars_str}
  📍 {s['region']} | Rating: {s['rating']}/5 ({s['total_reviews']} reviews)
  💰 {s['price_text']}
  🏷 {', '.join(s['tags'][:5]) if s['tags'] else 'no tags'}
  📝 {s['description'][:150]}
"""
    else:
        context = "No places found in database matching this query."

    weather_str = ""
    if weather:
        weather_str = f"\nCurrent weather: {weather['temp']}°C, {weather['description']}, humidity {weather['humidity']}%"

    prompt = f"""{system}

{context}
{weather_str}

User question: {message}

Instructions:
- ONLY recommend places from the "Available places" list above
- If the list is empty, say so honestly and suggest broader search
- DO NOT invent or make up places that are not in the list
- Consider ratings, prices, and weather
- Be concise but helpful (2-4 sentences max)
- Respond in the same language as the user

Answer:"""

    return prompt


async def ask_groq(prompt: str, image_base64: str | None = None, max_retries: int = 3) -> str:
    """Отправляет запрос к Groq API с повторными попытками при ошибках."""
    if not settings.GROQ_API_KEY:
        return "AI service is not configured. Please add GROQ_API_KEY."

    if not settings.GROQ_API_KEY.startswith("gsk_"):
        return "AI API key is invalid or has been revoked. Please update the GROQ_API_KEY."

    last_error = None

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.GROQ_MODEL,
                        "messages": [{"role": "user", "content": build_message_content(prompt, image_base64)}],
                        "temperature": 0.7,
                        "max_tokens": 500,
                    },
                )

                if response.status_code == 401:
                    return "AI API key is invalid or expired. Please update the GROQ_API_KEY."
                elif response.status_code == 429:
                    return "AI service rate limit exceeded. Please try again in a few minutes."
                elif response.status_code == 500:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    return "AI service is temporarily unavailable. Please try again later."
                elif response.status_code != 200:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)
                        continue
                    return f"AI service error (status {response.status_code}). Please try again later."

                data = response.json()
                return data["choices"][0]["message"]["content"].strip()

        except httpx.TimeoutException:
            last_error = "Timeout"
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue
            return "AI service is taking too long. Please try again."
        except httpx.ConnectError:
            last_error = "Connection error"
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
                continue
            return "Cannot connect to AI service. Please check your internet connection."
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue
            return f"AI error: {str(e)[:100]}"

    return f"AI service failed after {max_retries} attempts. Last error: {last_error}"


def generate_simple_reply(message: str, suggestions: list[dict], weather: dict | None, lang: str) -> str:
    """Fallback если Groq недоступен."""
    if not suggestions:
        replies = {
            "ru": "К сожалению, ничего не найдено. Попробуйте изменить запрос.",
            "uz": "Afsuski, hech narsa topilmadi. So'rovingizni o'zgartirib ko'ring.",
            "en": "Nothing found. Try a different search.",
        }
        return replies.get(lang, replies["en"])

    names = [f"{s['name']} — {s['price_text']} (⭐{s['rating']})" for s in suggestions[:5]]

    if lang == "ru":
        return f"Найдено {len(suggestions)} мест:\n" + "\n".join(f"• {n}" for n in names)
    elif lang == "uz":
        return f"{len(suggestions)} ta joy topildi:\n" + "\n".join(f"• {n}" for n in names)
    else:
        return f"Found {len(suggestions)} places:\n" + "\n".join(f"• {n}" for n in names)