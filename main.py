from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import init_db
from app.api.v1.auth import router as auth_router
from app.api.v1.regions import router as regions_router
from app.api.v1.properties import router as properties_router
from app.api.v1.tours import router as tours_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.chat import router as chat_router
from app.api.v1.booking import router as booking_router
from app.api.v1.ai_chat import router as ai_chat_router
from app.api.v1.saved import router as saved_router
from app.api.v1.exchange import router as exchange_router
from app.api.v1.navigation import router as navigation_router
from app.api.v1.users import router as users_router
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    from app.core.seed_auto import auto_seed
    auto_seed()
    print("Database initialized")
    yield

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    servers=[
        {"url": "http://127.0.0.1:8000", "description": "Local dev"},
        {"url": "https://guide-me-8znn.onrender.com", "description": "Production (Render)"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if os.path.isdir(settings.STATIC_DIR):
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(regions_router, prefix="/api/v1/regions", tags=["regions"])
app.include_router(properties_router, prefix="/api/v1/properties", tags=["properties"])
app.include_router(tours_router, prefix="/api/v1/tours", tags=["tours"])
app.include_router(reviews_router, prefix="/api/v1/reviews", tags=["reviews"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(booking_router, prefix="/api/v1/booking", tags=["booking"])
app.include_router(ai_chat_router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(saved_router, prefix="/api/v1/saved", tags=["saved"])
app.include_router(exchange_router, prefix="/api/v1/exchange", tags=["exchange"])
app.include_router(navigation_router, prefix="/api/v1/navigation", tags=["navigation"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
@app.get("/")
def root():
    return {"app": settings.APP_NAME, "version": "1.0.0"}