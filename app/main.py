from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.tron_service import get_wallet_info
from app.database import AsyncSessionLocal, WalletQuery
from datetime import datetime
from typing import Annotated

app = FastAPI()


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
