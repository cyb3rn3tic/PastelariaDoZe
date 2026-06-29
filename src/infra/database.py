from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from settings import STR_DATABASE

# Cria o engine assíncrono
engine = create_async_engine(STR_DATABASE, echo=True)

# Cria a fábrica de sessões assíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

# Cria as tabelas de forma assíncrona
async def cria_tabelas():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
# Dependência injetável para as rotas
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()