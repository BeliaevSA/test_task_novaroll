"""
Точка входа FastAPI-приложения.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models  # noqa: F401
from app.api.call_summary import router as call_summary_router
from app.api.calls import router as calls_router
from app.api.managers import router as managers_router

# Создаём таблицы при старте, если их ещё нет
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Сводка по звонкам")

# CORS нужен для локальной разработки фронта (npm run dev, порт 5173),
# который обращается к backend напрямую, минуя nginx-прокси.
# В продакшене (за nginx на одном домене) можно сузить allow_origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(managers_router)
app.include_router(calls_router)
app.include_router(call_summary_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}