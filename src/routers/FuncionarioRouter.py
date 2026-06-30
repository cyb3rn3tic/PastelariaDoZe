from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from domain.schemas.FuncionarioSchema import FuncionarioCreate, FuncionarioResponse
from domain.schemas.AuthSchema import FuncionarioAuth
from infra.database import get_db
from infra.dependencies import get_current_active_user, require_group
from services.FuncionarioService import FuncionarioService
from services.AuditoriaService import AuditoriaService

router = APIRouter()

@router.get("/funcionario/", response_model=List[FuncionarioResponse], tags=["Funcionário"])
async def get_funcionarios(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1]))
): 
    return await FuncionarioService.listar_todos(db)

@router.post("/funcionario/", response_model=FuncionarioResponse, status_code=201, tags=["Funcionário"])
async def post_funcionario(
    request: Request, 
    dados: FuncionarioCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1]))
):
    novo_func = await FuncionarioService.criar(db, dados)
    
    await AuditoriaService.registrar_acao(
        db=db, funcionario_id=current_user.id, acao="CREATE", recurso="FUNCIONARIO",
        recurso_id=novo_func.id, dados_antigos=None, dados_novos=novo_func, request=request
    )
    return novo_func

@router.delete("/funcionario/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Funcionário"])
async def delete_funcionario(
    id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1]))
):
    await FuncionarioService.deletar(db, id)
    
    # Registro automático da exclusão na tabela de auditoria
    await AuditoriaService.registrar_acao(
        db=db, funcionario_id=current_user.id, acao="DELETE", recurso="FUNCIONARIO",
        recurso_id=id, dados_antigos=None, dados_novos=None, request=request
    )
    return None

#Osmar Steffen