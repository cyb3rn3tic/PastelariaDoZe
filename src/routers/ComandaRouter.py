from fastapi import APIRouter, Depends
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
    nova_comanda = ComandaDB(comanda=dados.comanda, cliente=dados.cliente, total=dados.total, status=0, data_hora=datetime.datetime.now())
    db.add(nova_comanda)
    await db.commit()
    await db.refresh(nova_comanda)
    return {"message": "Comanda aberta com sucesso!", "id": nova_comanda.id}

@router.get("/comanda/", tags=["Comanda"])
async def listar_comandas_abertas(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_active_user)):
    return await ComandaService.listar_abertas(db)

@router.get("/comanda/historico", tags=["Comanda"])
async def listar_historico(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_active_user)):
    return await ComandaService.listar_historico(db)