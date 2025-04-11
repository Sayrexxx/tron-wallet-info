from datetime import datetime
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import WalletQuery, AsyncSessionLocal


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@pytest.mark.asyncio
async def test_db_write_success():
    """Test successful write to the database"""
    async with AsyncSessionLocal() as session:
        test_address = "TEST_ADDRESS_1"
        query = WalletQuery(wallet_address=test_address, timestamp=datetime.now())

        session.add(query)
        await session.commit()
        await session.refresh(query)

        assert query.id is not None
        assert query.wallet_address == test_address
        assert isinstance(query.timestamp, datetime)


@pytest.mark.asyncio
async def test_db_write_empty_address_fails():
    """Test that writing an empty address fails"""
    async with AsyncSessionLocal() as session:
        query = WalletQuery(wallet_address=None, timestamp=datetime.now())

        session.add(query)
        with pytest.raises(IntegrityError):
            await session.commit()

        await session.rollback()


@pytest.mark.asyncio
async def test_db_write_duplicate_allowed():
    """Test that duplicate addresses are allowed"""
    async with AsyncSessionLocal() as session:
        test_address = "DUPLICATE_ADDRESS"
        timestamp = datetime.now()

        query1 = WalletQuery(wallet_address=test_address, timestamp=timestamp)
        session.add(query1)
        await session.commit()
        await session.refresh(query1)

        query2 = WalletQuery(wallet_address=test_address, timestamp=timestamp)
        session.add(query2)
        await session.commit()
        await session.refresh(query2)

        assert query1.id != query2.id
        assert query1.wallet_address == query2.wallet_address


@pytest.mark.asyncio
async def test_db_timestamp_auto_set():
    """Test that timestamp is set correctly"""
    async with AsyncSessionLocal() as session:
        before_insert = datetime.now()
        query = WalletQuery(wallet_address="TIMESTAMP_TEST")

        session.add(query)
        await session.commit()
        await session.refresh(query)
        after_insert = datetime.now()

        assert query.timestamp is not None
        assert before_insert <= query.timestamp <= after_insert


@pytest.mark.asyncio
async def test_async_db_operations():
    """Test asynchronous database operations"""
    async with AsyncSessionLocal() as session:
        query = WalletQuery(wallet_address="ASYNC_TEST", timestamp=datetime.now())
        session.add(query)
        await session.commit()
        await session.refresh(query)

        assert query.id is not None

        result = await session.execute(
            select(WalletQuery).where(WalletQuery.id == query.id)
        )
        retrieved_query = result.scalar()
        assert retrieved_query is not None
