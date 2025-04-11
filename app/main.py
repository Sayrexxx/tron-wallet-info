from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.services.tron_service import get_wallet_info
from app.database import SessionLocal, WalletQuery
from datetime import datetime
from typing import Annotated

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/wallet-info")
async def fetch_wallet_info(address: str, db: Annotated[Session, Depends(get_db)]):
    data = await get_wallet_info(address)
    current_time = datetime.now()
    db_query = WalletQuery(wallet_address=address, timestamp=current_time)
    db.add(db_query)
    db.commit()
    return data
