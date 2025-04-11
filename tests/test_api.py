import asyncio
from datetime import datetime, timedelta
import pytest
from httpx import AsyncClient
from sqlalchemy.future import select
from sqlalchemy import text
from app.main import app
from app.database import AsyncSessionLocal, WalletQuery
import pytest_asyncio
from uvicorn import Config, Server
import threading


@pytest_asyncio.fixture(scope="module", autouse=True)
async def start_test_server():
    """Start FastAPI server in a separate thread for testing."""
    config = Config(app, host="127.0.0.1", port=8080, log_level="info")
    server = Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    try:
        yield
    finally:
        server.should_exit = True
        thread.join()


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Asynchronous fixture for working with the test database."""
    async with AsyncSessionLocal() as db:
        yield db
        await db.execute(text("DELETE FROM wallet_queries"))
        await db.commit()


@pytest_asyncio.fixture(scope="function")
async def async_client():
    """Fixture for asynchronous client."""
    async with AsyncClient(base_url="http://127.0.0.1:8080") as client:
        yield client


@pytest.mark.asyncio
async def test_pagination_behavior(test_db, async_client):
    """Test pagination behavior."""
    for i in range(15):
        query = WalletQuery(
            wallet_address=f"PAGETEST_{i}",
            timestamp=datetime.now() - timedelta(minutes=i),
        )
        test_db.add(query)
    await test_db.commit()

    response = await async_client.get("/query-history?skip=3&limit=5")
    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}"
    data = response.json()
    assert len(data) == 5
    assert data[0]["wallet_address"] == "PAGETEST_3"


@pytest.mark.asyncio
async def test_various_scenarios(async_client):
    """Test error handling scenarios."""
    response = await async_client.post("/wallet-info", json={"address": ""})
    assert response.status_code == 422

    address = "TLw6HAySiPaJqQnTavhGg3T9C4d5dFVf5z"
    response = await async_client.post(f"/wallet-info?address={address}")
    assert response.status_code == 200

    response = await async_client.get("/query-history?skip=-1&limit=0")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_concurrent_requests(test_db, async_client):
    """Test concurrent requests."""
    test_addresses = [
        "TX8QZrZ28GJQeSdMJ8QyRtZBABvqsNoxGk",
        "THRF3GuPnvvPzKoaT8pJex5XHmoCEUU3u7",
        "TYMBWf2DZJdXq1Q2Xq2Xq2Xq2Xq2Xq2Xq2X",
    ]

    async def make_request(address):
        response = await async_client.post(
            f"/wallet-info?address={address}",
            headers={"accept": "application/json"},
            content=b"",
        )
        assert (
            response.status_code == 200
        ), f"Unexpected status code: {response.status_code}. Response: {response.text}"

    await asyncio.gather(*[make_request(addr) for addr in test_addresses])

    for address in test_addresses:
        result = await test_db.execute(
            select(WalletQuery).where(WalletQuery.wallet_address == address)
        )
        assert result.scalar_one_or_none() is not None
