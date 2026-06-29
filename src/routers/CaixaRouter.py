from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import datetime # Alterado para evitar qualquer conflito
from typing import List
from pydantic import BaseModel

# Importações corrigidas para o seu banco síncrono
from infra.database import get_db
from infra.dependencies import get_current_active_user
from infra.orm.ComandaModel import ComandaDB

router = APIRouter()

class RecebimentoRequest(BaseModel):
    comanda_ids: List[int]
    desconto: float = 0.0
    acrescimo: float = 0.0
    observacao: str = ""

# A função NÃO deve ser 'async'
@router.post("/recebimento/", tags=["Caixa"], summary="Efetuar recebimento de comandas")
def efetuar_recebimento(
    dados: RecebimentoRequest,
    db: Session = Depends(get_db), # Injeção de sessão SÍNCRONA
    current_user = Depends(get_current_active_user)
):
    try:
        # Busca síncrona
        comandas = db.query(ComandaDB).filter(ComandaDB.id.in_(dados.comanda_ids)).all()

        if not comandas:
            raise HTTPException(status_code=404, detail="Nenhuma comanda encontrada")

        for comanda in comandas:
            comanda.status = 1
            # Correção blindada chamando o módulo e a classe
            comanda.data_hora = datetime.datetime.now()
        
        # Commit síncrono
        db.commit()
        return {"message": "Recebimento efetuado com sucesso!"}
    
    except Exception as e:
        # Rollback síncrono (SEM AWAIT)
        db.rollback() 
        raise HTTPException(status_code=500, detail=f"Erro ao processar recebimento: {str(e)}")