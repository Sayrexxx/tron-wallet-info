import pytest
from starlette.testclient import TestClient
from sqlalchemy.future import select
from sqlalchemy.sql import func
from datetime import datetime
from app.main import app
from app.database import AsyncSessionLocal, Base, engine
from app.database import WalletQuery

headers = {"Accept": "application/json", "Content-Type": "application/json"}


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture(scope="function")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_fetch_wallet_info_success(client: TestClient):
    address = "test_success_addr_tc"
    response = client.post(f"/wallet-info?address={address}", headers=headers)

    assert response.status_code == 200
    assert response.json().get("balance_trx") is not None


@pytest.mark.asyncio
async def test_fetch_wallet_info_db_entry(client: TestClient):
    address = "test_db_entry_addr_tc"
    response = client.post(f"/wallet-info?address={address}", headers=headers)

    assert response.status_code == 200

    async with AsyncSessionLocal() as session:
        stmt = select(WalletQuery).where(WalletQuery.wallet_address == address)
        result = await session.execute(stmt)
        query_entry = result.scalars().first()

        assert query_entry is not None
        assert query_entry.wallet_address == address
        assert query_entry.wallet_address != "null_key"


@pytest.mark.asyncio
async def test_get_query_history_success(client: TestClient):
    response = client.get("/query-history")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_query_history_pagination(client: TestClient):
    async with AsyncSessionLocal() as session:
        needed = 20
        existing_count_result = await session.execute(
            select(func.count(WalletQuery.id))
        )
        existing_count = existing_count_result.scalar_one()

        if existing_count < needed:
            new_records = []
            for i in range(existing_count + 1, needed + 1):
                new_records.append(
                    WalletQuery(
                        wallet_address=f"addr_paginate_tc_{i}", timestamp=datetime.now()
                    )
                )
            session.add_all(new_records)
            await session.commit()

    skip = 10
    limit = 5
    response = client.get("/query-history", params={"skip": skip, "limit": limit})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == limit
