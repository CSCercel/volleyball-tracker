import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.database import Base
import os


async def test_migration():
    # Create test database
    test_url = "sqlite+aiosqlite:///./test_migration.db"
    engine = create_async_engine(test_url)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Migration test passed!")
    
    # Cleanup
    await engine.dispose()
    os.remove("test_migration.db")

if __name__ == "__main__":
    asyncio.run(test_migration())
