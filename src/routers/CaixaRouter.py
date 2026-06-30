from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from infra.database import get_db
from infra.dependencies import get_current_active_user
from services.ComandaService import ComandaService

router = APIRouter()

class RecebimentoRequest(BaseModel):
    comanda_ids: List[int]

@router.post("/recebimento/", tags=["Caixa"])
async def efetuar_recebimento(dados: RecebimentoRequest, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_active_user)):
    await ComandaService.fechar_comandas(db, dados.comanda_ids)
    return {"message": "Sucesso"}