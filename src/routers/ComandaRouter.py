from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import datetime
from infra.database import get_db
from infra.dependencies import get_current_active_user
from infra.orm.ComandaModel import ComandaDB
from services.ComandaService import ComandaService

router = APIRouter()

class ComandaCreateRequest(BaseModel):
    comanda: str
    cliente: str
    total: float = 0.0

@router.post("/comanda/", tags=["Comanda"])
async def criar_comanda(dados: ComandaCreateRequest, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_active_user)):
    nova = ComandaDB(comanda=dados.comanda, cliente=dados.cliente, total=dados.total, status=0, data_hora=datetime.datetime.now())
    db.add(nova)
    await db.commit()
    await db.refresh(nova)
    return {"id": nova.id}

@router.get("/comanda/", tags=["Comanda"])
async def get_comandas(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_active_user)):
    return await ComandaService.listar_abertas(db)

@router.get("/comanda/historico", tags=["Comanda"])
async def get_historico(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_active_user)):
    return await ComandaService.listar_historico(db)