from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
import datetime
from sqlalchemy.future import select

from infra.database import get_db
from infra.dependencies import get_current_active_user, require_group
from infra.orm.ComandaModel import ComandaDB
from services.ComandaService import ComandaService

router = APIRouter()

class ComandaCreateRequest(BaseModel):
    comanda: str
    cliente: str
    total: float = 0.0

@router.post("/comanda/", tags=["Comanda"], summary="Abrir nova comanda")
async def criar_comanda(
    dados: ComandaCreateRequest, 
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(require_group([1]))
):
    try:
        nova = ComandaDB(
            comanda=dados.comanda, 
            cliente=dados.cliente, 
            total=dados.total, 
            status=0, 
            data_hora=datetime.datetime.now()
        )
        db.add(nova)
        await db.commit()
        await db.refresh(nova)
        return {"message": "Comanda aberta com sucesso!", "id": nova.id}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao abrir comanda: {str(e)}")

@router.get("/comanda/", tags=["Comanda"], summary="Listar comandas abertas")
async def get_comandas(
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    # Chamando o serviço em vez de fazer o select direto
    return await ComandaService.listar_abertas(db)

@router.get("/comanda/historico", tags=["Comanda"], summary="Listar TODAS as comandas")
async def get_historico(
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    # Chamando o serviço em vez de fazer o select direto
    return await ComandaService.listar_historico(db)

@router.delete("/comanda/{id}", status_code=204, tags=["Comanda"], summary="Excluir comanda")
async def delete_comanda(
    id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(require_group([1]))
):
    try:
        result = await db.execute(select(ComandaDB).where(ComandaDB.id == id))
        comanda = result.scalars().first()
        
        if not comanda:
            raise HTTPException(status_code=404, detail=f"Comanda não encontrada {current_user.id}")
        
        await db.delete(comanda)
        await db.commit()
        return None
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao excluir comanda: {str(e)}")
    
    #Osmar Steffen
