from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from settings import STR_DATABASE

engine = create_async_engine(STR_DATABASE, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def cria_tabelas():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

#Osmar Steffen