from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import datetime

from infra.database import get_db
from infra.dependencies import get_current_active_user
from infra.orm.ComandaModel import ComandaDB

router = APIRouter()

# 1. Estrutura para receber os dados do POST
class ComandaCreateRequest(BaseModel):
    comanda: str
    cliente: str
    total: float = 0.0

# 2. Rota para ABRIR a comanda
@router.post("/comanda/", tags=["Comanda"], summary="Abrir nova comanda")
def criar_comanda(
    dados: ComandaCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    try:
        nova_comanda = ComandaDB(
            comanda=dados.comanda,
            cliente=dados.cliente,
            total=dados.total,
            status=0, # 0 = Aberta
            data_hora=datetime.datetime.now()
        )
        
        db.add(nova_comanda)
        db.commit()
        db.refresh(nova_comanda) # Pega o ID gerado pelo banco
        
        return {
            "message": "Comanda aberta com sucesso!",
            "id": nova_comanda.id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao abrir comanda: {str(e)}")

# 3. Rota GET (Ajustada para síncrono)
@router.get("/comanda/", tags=["Comanda"], summary="Listar comandas abertas")
def listar_comandas_abertas(
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    try:
        # Busca apenas as comandas com status 0 (Aberta)
        comandas = db.query(ComandaDB).filter(ComandaDB.status == 0).all()
        return comandas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar comandas: {str(e)}")

# 4. Rota PUT (Ajustada para síncrono)
@router.put("/comanda/{id}/fechar", tags=["Comanda"], summary="Fechar comanda")
def fechar_comanda(
    id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    try:
        comanda = db.query(ComandaDB).filter(ComandaDB.id == id).first()
        if not comanda:
            raise HTTPException(status_code=404, detail="Comanda não encontrada")
        
        comanda.status = 1 # 1 = Fechada
        comanda.data_hora = datetime.datetime.now()
        db.commit()
        return {"message": "Comanda fechada com sucesso!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao fechar comanda: {str(e)}")
    
    # Adicione no final do ComandaRouter.py
@router.get("/comanda/historico", tags=["Comanda"], summary="Listar TODAS as comandas")
def listar_historico_comandas(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    try:
        return db.query(ComandaDB).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar histórico: {str(e)}")