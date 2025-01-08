from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.core.database import get_session

from src.api import router as router_api


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Allow all origins. Replace "*" with specific origins for production.
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


app.include_router(router_api)


@app.get("/healthcheck")
async def check_health(session: AsyncSession = Depends(get_session)):
    result = await session.execute(text("SELECT version()"))
    return {"msg": result.scalar_one()}
