import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from app import database
from app.routes import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("listing-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.client = AsyncIOMotorClient(database.MONGO_URI, serverSelectionTimeoutMS=10000)
    # Fail fast if MongoDB is unreachable so Docker / Kubernetes restarts the container
    await database.client.admin.command("ping")
    log.info("Listing Service connected to MongoDB")
    db = database.get_db()
    await db.listings.create_index("city")
    await db.listings.create_index("status")
    yield
    database.client.close()


app = FastAPI(title="Listing Service", version="1.0.0", lifespan=lifespan)
app.include_router(router)


# Liveness / readiness probe endpoint
@app.get("/health", tags=["health"])
async def health():
    try:
        await database.client.admin.command("ping")
        return {"service": "listing-service", "status": "UP"}
    except Exception:
        return JSONResponse(status_code=503, content={"service": "listing-service", "status": "DOWN"})
