from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
import datetime
from infra.orm.ComandaModel import ComandaDB
from typing import List

class ComandaService:
    @staticmethod
    async def listar_abertas(db: AsyncSession):
        result = await db.execute(select(ComandaDB).where(ComandaDB.status == 0))
        return result.scalars().all()

    @staticmethod
    async def listar_historico(db: AsyncSession):
        result = await db.execute(select(ComandaDB))
        return result.scalars().all()

    @staticmethod
    async def fechar_comandas(db: AsyncSession, ids: List[int]):
        result = await db.execute(select(ComandaDB).where(ComandaDB.id.in_(ids)))
        comandas = result.scalars().all()
        
        if not comandas: raise HTTPException(status_code=404, detail="Nenhuma comanda encontrada")
        
        for comanda in comandas:
            comanda.status = 1
            comanda.data_hora = datetime.datetime.now()
            
        await db.commit()
        return comandas
    
    #Osmar Steffen