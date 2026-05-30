import json
from app.core.config import settings

try:
    import spacy
    nlp_ru = spacy.load("ru_core_news_sm")
    nlp_en = spacy.load("en_core_web_sm")
except Exception:
    nlp_ru = None
    nlp_en = None


def detect_language(text: str) -> str:
    text_lower = text.lower()
    uz_words = [
        "qayerda", "qanday", "qancha", "bor", "kerak", "maslahat",
        "mehmonxona", "muzey", "osh", "ovqat", "borish", "ko'rish",
        "tavsiya", "yaxshi", "arzon", "qimmat", "yaqin", "uzoq",
        "oilaviy", "dam", "olish", "tarixiy", "joylar", "qayerda",
        "qachon", "nima", "qaysi", "qancha", "qanday", "qanaqa",
        "bormoq", "kelmoq", "ketmoq", "turmoq", "yotmoq",
        "so'm", "sum", "dollar", "yevro",
    ]
    uz_count = sum(1 for w in uz_words if w in text_lower)
    ru_letters = sum(1 for c in text if c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
    if uz_count >= 2:
        return "uz"
    elif ru_letters > 3:
        return "ru"
    else:
        return "en"


# ==================== РУССКИЙ ====================

def extract_entities_ru(text: str) -> dict:
    if nlp_ru is None:
        return _fallback_extract(text)
    doc = nlp_ru(text)
    result = {"city": None, "type": None, "tags": [], "budget": None, "stars": None}

    cities_map = {
        "андижан": "Andijan", "андижане": "Andijan", "андижана": "Andijan",
        "бухара": "Bukhara", "бухаре": "Bukhara", "бухары": "Bukhara", "бухоро": "Bukhara",
        "джизак": "Jizzakh", "джизаке": "Jizzakh", "джизака": "Jizzakh",
        "кашкадарья": "Kashkadarya", "кашкадарье": "Kashkadarya",
        "навои": "Navoiy", "навоий": "Navoiy",
        "наманган": "Namangan", "намангане": "Namangan",
        "самарканд": "Samarkand", "самарканде": "Samarkand", "самарканда": "Samarkand",
        "сурхандарья": "Surkhandarya",
        "сырдарья": "Syrdarya",
        "ташкент": "Tashkent", "ташкенте": "Tashkent", "тошкент": "Tashkent",
        "фергана": "Fergana", "фергане": "Fergana", "фаргона": "Fergana",
        "хорезм": "Khorezm", "хива": "Khorezm", "хиве": "Khorezm", "хивы": "Khorezm",
        "ургенч": "Khorezm", "ургенче": "Khorezm",
        "шахрисабз": "Kashkadarya", "шахрисабзе": "Kashkadarya",
        "термез": "Surkhandarya", "термезе": "Surkhandarya",
        "коканд": "Fergana", "коканде": "Fergana",
        "маргилан": "Fergana", "маргилане": "Fergana",
        "гулистан": "Syrdarya", "гулистане": "Syrdarya",
        "нукус": "Kashkadarya", "нукусе": "Kashkadarya",
    }
    for key, val in cities_map.items():
        if key in text.lower():
            result["city"] = val
            break

    type_map = {
        "отель": "hotel", "отеля": "hotel", "отеле": "hotel", "отели": "hotel",
        "гостиница": "hotel", "гостиницы": "hotel", "гостинице": "hotel", "гостиниц": "hotel",
        "мехмонхона": "hotel", "хостел": "hotel", "ночлег": "hotel",
        "переночевать": "hotel", "остановиться": "hotel", "жильё": "hotel",
        "жилье": "hotel", "ночевать": "hotel", "ночлежка": "hotel",
        "забронировать": "hotel", "снять": "hotel", "арендовать": "hotel",
        "музей": "museum", "музея": "museum", "музее": "museum", "музеи": "museum",
        "выставка": "museum", "галерея": "museum",
        "памятник": "museum", "памятника": "museum", "памятники": "museum",
        "статуя": "museum", "статую": "museum", "статуи": "museum",
        "монумент": "museum", "мемориал": "museum",
        "мавзолей": "museum", "мавзолея": "museum",
        "медресе": "museum", "мечеть": "museum", "мечети": "museum",
        "крепость": "museum", "крепости": "museum",
        "цитадель": "museum", "дворец": "museum", "дворца": "museum",
        "собор": "museum", "храм": "museum", "храма": "museum",
        "некрополь": "museum", "городище": "museum",
        "обсерватория": "museum", "минарет": "museum",
        "достопримечательность": "museum", "достопримечательности": "museum",
        "парк": "park", "парка": "park", "парке": "park", "парки": "park",
        "сквер": "park", "сад": "park", "сада": "park",
        "озеро": "park", "озера": "park", "водохранилище": "park",
        "заповедник": "park", "национальный парк": "park",
        "пляж": "park", "каньон": "park", "ущелье": "park",
        "пикник": "park", "прогулка": "park", "гулять": "park",
        "ресторан": "restaurant", "ресторана": "restaurant",
        "кафе": "restaurant", "кафешка": "restaurant",
        "столовая": "restaurant", "чайхана": "restaurant",
        "чайхона": "restaurant", "закусочная": "restaurant",
        "фастфуд": "restaurant", "фаст фуд": "restaurant",
        "поесть": "restaurant", "покушать": "restaurant", "кушать": "restaurant",
        "еда": "restaurant", "обед": "restaurant", "ужин": "restaurant",
        "завтрак": "restaurant", "перекус": "restaurant",
        "плов": "restaurant", "шашлык": "restaurant", "самса": "restaurant",
        "магазин": "shop", "базар": "shop", "рынок": "shop",
        "сувенир": "shop", "сувениры": "shop",
        "шоппинг": "shop", "покупки": "shop",
        "развлечение": "entertainment", "развлечения": "entertainment",
        "аттракцион": "entertainment", "аттракционы": "entertainment",
        "аквапарк": "entertainment", "цирк": "entertainment",
        "театр": "entertainment", "кино": "entertainment",
        "концерт": "entertainment", "фестиваль": "entertainment",
    }
    print(f"Looking for type in: {text.lower()}")
    for key, val in type_map.items():
        if key in text.lower() and not result["type"]:
            print(f"  FOUND type: {key} -> {val}")
            result["type"] = val
            break
    print(f"  RESULT type: {result['type']}")

    tag_map = {
        "дешёвый": "cheap", "дешево": "cheap", "дешёво": "cheap",
        "недорогой": "cheap", "недорого": "cheap", "не дорого": "cheap",
        "бюджетный": "cheap", "бюджетно": "cheap", "эконом": "cheap",
        "дешевле": "cheap", "дешёвые": "cheap", "низкая цена": "cheap",
        "дорогой": "luxury", "дорого": "luxury", "роскошный": "luxury",
        "роскошно": "luxury", "люкс": "luxury", "премиум": "luxury",
        "элитный": "luxury", "вип": "luxury", "vip": "luxury",
        "бесплатный": "free", "бесплатно": "free", "бесплатные": "free",
        "даром": "free", "без денег": "free", "без оплаты": "free",
        "история": "history", "исторический": "history", "историческое": "history",
        "древний": "ancient", "древняя": "ancient", "античный": "ancient",
        "средневековый": "history", "вековой": "history",
        "архитектура": "architecture", "архитектурный": "architecture",
        "культура": "culture", "культурный": "culture",
        "традиционный": "traditional", "традиции": "traditional",
        "национальный": "uzbek", "узбекский": "uzbek", "узбекская": "uzbek",
        "наследие": "heritage", "юнеско": "unesco", "unesco": "unesco",
        "семейный": "family", "семья": "family", "для семьи": "family",
        "дети": "children", "детский": "children", "для детей": "children",
        "ребенок": "children", "ребёнок": "children", "малыш": "children",
        "природа": "nature", "природный": "nature",
        "горы": "mountains", "горный": "mountains", "гора": "mountains",
        "озеро": "lake", "озерный": "lake", "река": "lake", "речной": "lake",
        "лес": "nature", "лесной": "nature", "роща": "nature",
        "пустыня": "nature", "степь": "nature",
        "пещера": "nature", "водопад": "nature", "родник": "nature",
        "бассейн": "pool", "спа": "spa", "сауна": "spa", "баня": "spa",
        "тренажерный": "gym", "фитнес": "gym", "спортзал": "gym",
        "wi-fi": "wifi", "wifi": "wifi", "вайфай": "wifi",
        "парковка": "parking", "стоянка": "parking",
        "завтрак включен": "breakfast", "завтрак": "breakfast",
        "кондиционер": "ac",
        "современный": "modern", "новый": "modern",
        "старый": "historic", "винтажный": "vintage",
        "романтический": "romantic", "романтик": "romantic",
        "уютный": "cozy", "уютно": "cozy", "комфортный": "comfort",
        "плов": "pilaf", "шашлык": "grill", "манты": "uzbek",
        "лагман": "uzbek", "самса": "bakery", "лепёшка": "bakery",
        "чай": "tea", "кофе": "coffee",
        "вегетарианский": "vegetarian", "халяль": "halal",
        "фестиваль": "festival", "праздник": "festival",
        "концерт": "music", "живая музыка": "music",
        "выставка": "exhibition",
        "безопасный": "safe", "тихий": "quiet", "спокойный": "quiet",
        "красивый": "beautiful", "популярный": "popular",
        "известный": "famous", "лучший": "best", "хороший": "good",
    }
    for key, val in tag_map.items():
        if f" {key} " in f" {text.lower()} " or text.lower().startswith(key + " ") or text.lower().endswith(" " + key) or text.lower() == key:
            result["tags"].append(val)

    for token in doc:
        if token.like_num:
            num = int(token.text)
            if num <= 5 and ("звезд" in text.lower() or "star" in text.lower()):
                result["stars"] = num
            elif num > 100:
                result["budget"] = float(num)
    return result


# ==================== АНГЛИЙСКИЙ ====================

def extract_entities_en(text: str) -> dict:
    if nlp_en is None:
        return _fallback_extract(text)
    doc = nlp_en(text)
    result = {"city": None, "type": None, "tags": [], "budget": None, "stars": None}

    cities_map = {
        "andijan": "Andijan", "bukhara": "Bukhara", "jizzakh": "Jizzakh",
        "kashkadarya": "Kashkadarya", "navoiy": "Navoiy", "namangan": "Namangan",
        "samarkand": "Samarkand", "surkhandarya": "Surkhandarya",
        "syrdarya": "Syrdarya", "tashkent": "Tashkent",
        "fergana": "Fergana", "khorezm": "Khorezm", "khiva": "Khorezm",
        "urgentch": "Khorezm", "shakhrisabz": "Kashkadarya",
        "termez": "Surkhandarya", "kokand": "Fergana",
        "margilan": "Fergana", "gulistan": "Syrdarya", "nukus": "Kashkadarya",
    }
    for key, val in cities_map.items():
        if key in text.lower():
            result["city"] = val
            break

    type_map = {
        "hotel": "hotel", "hostel": "hotel", "inn": "hotel", "motel": "hotel",
        "lodging": "hotel", "stay": "hotel", "accommodation": "hotel",
        "room": "hotel", "overnight": "hotel", "book": "hotel", "reserve": "hotel",
        "museum": "museum", "gallery": "museum", "exhibition": "museum",
        "monument": "museum", "statue": "museum", "memorial": "museum",
        "mausoleum": "museum", "madrasah": "museum", "mosque": "museum",
        "fortress": "museum", "citadel": "museum", "palace": "museum",
        "temple": "museum", "necropolis": "museum", "minaret": "museum",
        "observatory": "museum", "sight": "museum", "landmark": "museum",
        "attraction": "museum", "historical": "museum",
        "park": "park", "garden": "park", "square": "park",
        "lake": "park", "beach": "park", "canyon": "park",
        "reserve": "park", "national park": "park",
        "picnic": "park", "hiking": "park", "nature": "park",
        "restaurant": "restaurant", "cafe": "restaurant", "dining": "restaurant",
        "food": "restaurant", "eat": "restaurant", "cuisine": "restaurant",
        "breakfast": "restaurant", "lunch": "restaurant", "dinner": "restaurant",
        "pilaf": "restaurant", "plov": "restaurant", "kebab": "restaurant",
        "shop": "shop", "market": "shop", "bazaar": "shop",
        "souvenir": "shop", "shopping": "shop", "store": "shop",
        "entertainment": "entertainment", "amusement": "entertainment",
        "waterpark": "entertainment", "circus": "entertainment",
        "theater": "entertainment", "cinema": "entertainment",
    }
    for key, val in type_map.items():
        if key in text.lower() and not result["type"]:
            result["type"] = val
            break

    tag_map = {
        "cheap": "cheap", "affordable": "cheap", "budget": "cheap",
        "inexpensive": "cheap", "low cost": "cheap", "economy": "cheap",
        "luxury": "luxury", "expensive": "luxury", "premium": "luxury",
        "vip": "luxury", "exclusive": "luxury", "high end": "luxury",
        "free": "free", "no cost": "free", "complimentary": "free",
        "history": "history", "historical": "history", "ancient": "ancient",
        "medieval": "history", "old": "historic",
        "architecture": "architecture", "cultural": "culture",
        "traditional": "traditional", "uzbek": "uzbek",
        "heritage": "heritage", "unesco": "unesco",
        "family": "family", "children": "children", "kids": "children",
        "nature": "nature", "mountain": "mountains", "lake": "lake",
        "river": "lake", "desert": "nature", "forest": "nature",
        "waterfall": "nature", "cave": "nature",
        "pool": "pool", "spa": "spa", "sauna": "spa",
        "gym": "gym", "fitness": "gym",
        "wifi": "wifi", "parking": "parking", "breakfast": "breakfast",
        "modern": "modern", "romantic": "romantic",
        "cozy": "cozy", "comfortable": "comfort", "quiet": "quiet",
        "safe": "safe", "halal": "halal", "vegetarian": "vegetarian",
        "beautiful": "beautiful", "popular": "popular",
        "famous": "famous", "best": "best", "top": "best",
    }
    for key, val in tag_map.items():
        if f" {key} " in f" {text.lower()} " or text.lower().startswith(key + " ") or text.lower().endswith(" " + key) or text.lower() == key:
            result["tags"].append(val)

    for token in doc:
        if token.like_num:
            num = int(token.text)
            if num <= 5 and "star" in text.lower():
                result["stars"] = num
            elif num > 10:
                result["budget"] = float(num)
    return result


# ==================== УЗБЕКСКИЙ ====================

def extract_entities_uz(text: str) -> dict:
    return _extract_keywords_uz(text)


def _extract_keywords_uz(text: str) -> dict:
    text_lower = text.lower()
    result = {"city": None, "type": None, "tags": [], "budget": None, "stars": None}

    cities = {
        "andijon": "Andijan", "buxoro": "Bukhara", "jizzax": "Jizzakh",
        "qashqadaryo": "Kashkadarya", "navoiy": "Navoiy", "namangan": "Namangan",
        "samarqand": "Samarkand", "surxondaryo": "Surkhandarya",
        "sirdaryo": "Syrdarya", "toshkent": "Tashkent",
        "farg'ona": "Fergana", "xorazm": "Khorezm", "xiva": "Khorezm",
        "urgentch": "Khorezm", "shahrisabz": "Kashkadarya",
        "termiz": "Surkhandarya", "qo'qon": "Fergana",
        "marg'ilon": "Fergana", "guliston": "Syrdarya", "nukus": "Kashkadarya",
    }
    for key, val in cities.items():
        if key in text_lower:
            result["city"] = val
            break

    types = {
        "mehmonxona": "hotel", "mehmonxonasi": "hotel",
        "hostel": "hotel", "yotoqxona": "hotel", "tunash": "hotel",
        "muzey": "museum", "muzeyi": "museum", "muzeylar": "museum",
        "ko'rgazma": "museum", "galereya": "museum",
        "haykal": "museum", "yodgorlik": "museum", "monument": "museum",
        "maqbara": "museum", "madrasa": "museum", "masjid": "museum",
        "qal'a": "museum", "saroy": "museum", "ibodatxona": "museum",
        "park": "park", "bog'": "park", "bog'i": "park",
        "ko'l": "park", "sohil": "park", "plyaj": "park",
        "qo'riqxona": "park", "daralar": "park",
        "restoran": "restaurant", "oshxona": "restaurant",
        "kafe": "restaurant", "choyxona": "restaurant",
        "ovqat": "restaurant", "yemoq": "restaurant",
        "taom": "restaurant", "osh": "restaurant",
        "do'kon": "shop", "bozor": "shop", "savdo": "shop",
    }
    for key, val in types.items():
        if key in text_lower:
            result["type"] = val
            break

    tags_map = {
        "arzon": "cheap", "arzonroq": "cheap", "hamyonbop": "cheap",
        "qimmat": "luxury", "hashamatli": "luxury", "lyuks": "luxury",
        "bepul": "free", "tekin": "free", "pulsiz": "free",
        "tarixiy": "history", "tarix": "history", "qadimiy": "ancient",
        "oilaviy": "family", "oila": "family", "bolalar": "children",
        "tabiat": "nature", "tog'": "mountains", "ko'l": "lake",
        "daryo": "lake", "cho'l": "nature",
        "milliy": "uzbek", "an'anaviy": "traditional",
        "zamonaviy": "modern", "yangi": "modern",
        "basseyn": "pool", "spa": "spa", "hammom": "spa",
        "wifi": "wifi", "mashina joyi": "parking",
        "nonushta": "breakfast", "romantik": "romantic",
        "sokin": "quiet", "xavfsiz": "safe",
        "chiroyli": "beautiful", "mashhur": "famous",
        "eng yaxshi": "best", "yaxshi": "good",
    }
    for key, val in tags_map.items():
        if key in text_lower:
            result["tags"].append(val)

    return result


# ==================== FALLBACK ====================

def _fallback_extract(text: str) -> dict:
    text_lower = text.lower()
    result = {"city": None, "type": None, "tags": [], "budget": None, "stars": None}

    cities = {
        "андижан": "Andijan", "andijan": "Andijan", "бухара": "Bukhara", "bukhara": "Bukhara",
        "джизак": "Jizzakh", "jizzakh": "Jizzakh", "кашкадарья": "Kashkadarya",
        "навои": "Navoiy", "navoiy": "Navoiy", "наманган": "Namangan", "namangan": "Namangan",
        "самарканд": "Samarkand", "samarkand": "Samarkand", "сурхандарья": "Surkhandarya",
        "сырдарья": "Syrdarya", "ташкент": "Tashkent", "tashkent": "Tashkent",
        "фергана": "Fergana", "fergana": "Fergana", "хорезм": "Khorezm", "khorezm": "Khorezm",
        "хива": "Khorezm", "khiva": "Khorezm", "тошкент": "Tashkent", "бухоро": "Bukhara",
    }
    for key, val in cities.items():
        if key in text_lower:
            result["city"] = val
            break

    types = {
        "отель": "hotel", "отели": "hotel", "отелей": "hotel", "hotel": "hotel", "hotels": "hotel",
        "мехмонхона": "hotel",
        "музей": "museum", "музеи": "museum", "музеев": "museum", "museum": "museum", "museums": "museum",
        "muzey": "museum",
        "парк": "park", "парки": "park", "парков": "park", "park": "park", "parks": "park",
        "ресторан": "restaurant", "рестораны": "restaurant", "ресторанов": "restaurant", "restaurant": "restaurant",
        "restaurants": "restaurant", "кафе": "restaurant", "cafe": "restaurant",
        "памятник": "museum", "памятники": "museum", "monument": "museum", "статуя": "museum", "статуи": "museum",
    }
    for key, val in types.items():
        if key in text_lower:
            result["type"] = val
            break

    return result