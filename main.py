# =============================================
# main.py - FastAPI + PostgreSQL
# =============================================
# Responsabilidades:
#   - Receber dados dos sensores via POST
#   - Rate limiting por sensor
#   - Delegar persistência ao módulo database.py
#   - Servir dashboard HTML e endpoints de leitura
# =============================================

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from contextlib import asynccontextmanager
from collections import defaultdict
import time
import os

from database import Database

# ---------- CONFIGURAÇÕES ----------
RATE_LIMIT_MAX    = int(os.getenv("RATE_LIMIT_MAX", 100))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 60))

# ---------- RATE LIMITING ----------
# { sensor_id: (count, window_start_ts) }
_rate_store: dict[str, tuple[int, float]] = defaultdict(lambda: (0, time.time()))


def check_rate_limit(sensor_id: str) -> tuple[bool, int, int]:
    """Retorna (permitido, contagem_atual, segundos_restantes)"""
    now = time.time()
    count, window_start = _rate_store[sensor_id]

    if now - window_start >= RATE_LIMIT_WINDOW:
        _rate_store[sensor_id] = (1, now)
        return True, 1, RATE_LIMIT_WINDOW

    if count >= RATE_LIMIT_MAX:
        remaining = int(RATE_LIMIT_WINDOW - (now - window_start))
        return False, count, remaining

    _rate_store[sensor_id] = (count + 1, window_start)
    return True, count + 1, int(RATE_LIMIT_WINDOW - (now - window_start))


# ---------- LIFESPAN ----------
db = Database()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando sistema...")
    await db.connect()
    print("📦 Banco de dados pronto!")
    yield
    await db.disconnect()
    print("🛑 Conexão com banco encerrada.")


# ---------- APP ----------
app = FastAPI(
    title="Monitor de Ruído ESP32",
    description="Sistema IoT com ESP32 + FastAPI + PostgreSQL + Docker",
    version="4.0",
    lifespan=lifespan,
)

templates = Jinja2Templates(directory="templates")


# ---------- MODELOS ----------
class NoiseData(BaseModel):
    sensor_id: str
    location:  str
    rms:       float
    noise_level: str
    sequence:  int
    device_uptime_ms: int


# ---------- ENDPOINTS ----------

@app.post("/api/noise", summary="Recebe leitura de um sensor")
async def receive_noise(data: NoiseData, request: Request):
    # Rate limit
    allowed, count, remaining = check_rate_limit(data.sensor_id)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limit_exceeded",
                "sensor_id": data.sensor_id,
                "count": count,
                "limit": RATE_LIMIT_MAX,
                "window_seconds": RATE_LIMIT_WINDOW,
                "retry_after_seconds": remaining,
            },
        )

    source_ip = request.client.host if request.client else "unknown"

    reading_id = await db.save_reading(data, source_ip)

    return {
        "status": "success",
        "reading_id": reading_id,
        "rate": {
            "count": count,
            "limit": RATE_LIMIT_MAX,
            "window_seconds": RATE_LIMIT_WINDOW,
        },
    }


@app.get("/api/readings", summary="Últimas 100 leituras")
async def get_readings(limit: int = 100):
    return await db.get_readings(limit=min(limit, 500))


@app.get("/api/sensors", summary="Lista sensores cadastrados")
async def get_sensors():
    return await db.get_sensors()


@app.get("/api/rate-status", summary="Status de rate limit por sensor")
async def get_rate_status():
    now = time.time()
    result = {}
    for sensor_id, (count, window_start) in _rate_store.items():
        elapsed = now - window_start
        if elapsed < RATE_LIMIT_WINDOW:
            result[sensor_id] = {
                "count": count,
                "limit": RATE_LIMIT_MAX,
                "remaining_in_window": int(RATE_LIMIT_WINDOW - elapsed),
                "percent_used": round(count / RATE_LIMIT_MAX * 100, 1),
            }
    return result


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard(request: Request):
    readings = await db.get_readings(limit=30)
    return templates.TemplateResponse(
        "index.html", {"request": request, "readings": readings}
    )


@app.get("/health", summary="Health check")
async def health():
    total = await db.count_readings()
    return {"status": "ok", "total_readings": total}