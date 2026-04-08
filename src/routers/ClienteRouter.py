from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from slowapi.errors import RateLimitExceeded
from services.AuditoriaService import AuditoriaService

# Domain Schemas
from domain.schemas.ClienteSchema import (
    ClienteCreate, 
    ClienteUpdate, 
    ClienteResponse
)
from domain.schemas.AuthSchema import FuncionarioAuth

# Infra
from infra.orm.ClienteModel import ClienteDB
from infra.database import get_db
from infra.dependencies import get_current_active_user, require_group
from infra.rate_limit import limiter, get_rate_limit

router = APIRouter()

# Criar as rotas/endpoints: GET, POST, PUT, DELETE
@router.get("/cliente/", response_model=List[ClienteResponse], tags=["Cliente"], status_code=status.HTTP_200_OK)
async def get_cliente(db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(get_current_active_user)
):
    """Retorna todos os clientes"""
    try:
        clientes = db.query(ClienteDB).all()
        return clientes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar clientes: {str(e)}"
        )

@router.get("/cliente/{id}", response_model=ClienteResponse, tags=["Cliente"], status_code=status.HTTP_200_OK)
async def get_cliente(id: int, db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(get_current_active_user)
):
    """Retorna um cliente específico pelo ID"""
    try:
        cliente = db.query(ClienteDB).filter(ClienteDB.id == id).first()
    
        if not cliente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    
        return cliente
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar cliente: {str(e)}"
        )

@router.post("/cliente/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED, tags=["Cliente"])
async def post_cliente(cliente_data: ClienteCreate, db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1,3]))                   
):
    """Cria um novo Cliente"""
    try:
        # Verifica se já existe Cliente com este CPF
        existing_cliente = db.query(ClienteDB).filter(ClienteDB.cpf == cliente_data.cpf).first()
       
        if existing_cliente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Já existe um cliente com este CPF"
            )
            
        # Cria o novo Cliente
        novo_cliente = ClienteDB(
            id=None, # Será auto-incrementado
            nome=cliente_data.nome,
            cpf=cliente_data.cpf,
            telefone=cliente_data.telefone,
        )
    
        db.add(novo_cliente)
        db.commit()
        db.refresh(novo_cliente)
    
        return novo_cliente
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao criar Cliente: {str(e)}"
        )

@router.put("/cliente/{id}", response_model=ClienteResponse, tags=["Cliente"], status_code=status.HTTP_200_OK)
@limiter.limit(get_rate_limit("critical"))
async def put_cliente(request: Request, id: int, cliente_data: ClienteUpdate, db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1,3]))  
):
    """Atualiza um Cliente existente"""
    try:
        cliente = db.query(ClienteDB).filter(ClienteDB.id == id).first()
        
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
            )
        
        # Verifica se está tentando atualizar para um CPF que já existe
        if cliente_data.cpf and cliente_data.cpf != cliente.cpf:
            existing_cliente = db.query(ClienteDB).filter(ClienteDB.cpf == cliente_data.cpf).first()
        
        if existing_cliente:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Já existe um cliente com este CPF"
            )
        
        # armazena uma copia de objeto com os dados atuais, para salvar na auditoria
        dados_antigos_obj = cliente.__dict__.copy()

        # Atualiza apenas os campos fornecidos
        update_data = cliente_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(cliente, field, value)
        db.commit()
        db.refresh(cliente)
        
        # Depois de tudo executado e antes do return, registra a ação na auditoria
        AuditoriaService.registrar_acao(
            db=db,
            funcionario_id=current_user.id,
            acao="UPDATE",
            recurso="CLIENTE",
            recurso_id=cliente.id,
            dados_antigos=dados_antigos_obj, 
            dados_novos=cliente, 
            request=request 
        )

        return cliente
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao atualizar cliente: {str(e)}"
        )

@router.delete("/cliente/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Cliente"], summary="Remover cliente")
@limiter.limit(get_rate_limit("critical"))
async def delete_cliente(request: Request, id: int, db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1]))  
):
    """Remove um cliente"""
    try:
        cliente = db.query(ClienteDB).filter(ClienteDB.id == id).first()
    
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
    
        db.delete(cliente)
        db.commit()

        # Depois de tudo executado e antes do return, registra a ação na auditoria
        AuditoriaService.registrar_acao(
            db=db,
            funcionario_id=current_user.id,
            acao="DELETE",
            recurso="CLIENTE",
            recurso_id=cliente.id,
            dados_antigos=cliente,
            dados_novos=None,
            Request=request
        )
    
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar cliente: {str(e)}"
        )

#Osmar Steffen