from fastapi import FastAPI, Depends, Query
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.tron_service import get_wallet_info
from app.database import AsyncSessionLocal, WalletQuery
from fastapi.openapi.docs import get_swagger_ui_html
from datetime import datetime
from typing import Annotated

app = FastAPI(docs_url=None, redoc_url=None)


@app.get("/", include_in_schema=False)
async def root():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="API Documentation",
    )


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@app.post("/wallet-info")
async def fetch_wallet_info(address: str, db: Annotated[AsyncSession, Depends(get_db)]):
    data = await get_wallet_info(address)
    current_time = datetime.now()
    db_query = WalletQuery(wallet_address=address, timestamp=current_time)
    db.add(db_query)
    await db.commit()
    return data


skip_arg = Query(default=0, ge=0)
limit_arg = Query(default=10, ge=1, le=100)


@app.get("/query-history")
async def get_query_history(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = skip_arg,
    limit: int = limit_arg,
):
    stmt = select(WalletQuery).offset(skip).limit(limit)
    result = await db.execute(stmt)
    queries = result.scalars().all()
    return queries
