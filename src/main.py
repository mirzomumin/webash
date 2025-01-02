from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.database import get_session

from src.users.router import router as user_router
# from src.products.router import router as products_router


app = FastAPI()


app.include_router(user_router, prefix="/users", tags=["users"])
# app.include_router(products_router, prefix="/products", tags=["products"])


@app.get("/healthcheck")
async def check_health(session: AsyncSession = Depends(get_session)):
    result = await session.execute(text("SELECT version()"))
    return {"msg": result.scalar_one()}
