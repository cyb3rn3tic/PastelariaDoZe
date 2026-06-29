from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from domain.schemas.ClienteSchema import ClienteCreate, ClienteUpdate, ClienteResponse
from domain.schemas.AuthSchema import FuncionarioAuth
from infra.database import get_db
from infra.dependencies import get_current_active_user, require_group
from services.ClienteService import ClienteService
from services.AuditoriaService import AuditoriaService
from infra.rate_limit import limiter, get_rate_limit

router = APIRouter()

@router.get("/cliente/", response_model=List[ClienteResponse], tags=["Cliente"])
async def get_clientes(db: AsyncSession = Depends(get_db), current_user: FuncionarioAuth = Depends(get_current_active_user)):
    return await ClienteService.listar_todos(db)

@router.get("/cliente/{id}", response_model=ClienteResponse, tags=["Cliente"])
async def get_cliente(id: int, db: AsyncSession = Depends(get_db), current_user: FuncionarioAuth = Depends(get_current_active_user)):
    return await ClienteService.buscar_por_id(db, id)

@router.post("/cliente/", response_model=ClienteResponse, status_code=201, tags=["Cliente"])
async def post_cliente(request: Request, dados: ClienteCreate, db: AsyncSession = Depends(get_db), current_user: FuncionarioAuth = Depends(require_group([1,3]))):
    novo_cliente = await ClienteService.criar(db, dados)
    await AuditoriaService.registrar_acao(db, current_user.id, "CREATE", "CLIENTE", novo_cliente.id, None, novo_cliente, request)
    return novo_cliente

@router.put("/cliente/{id}", response_model=ClienteResponse, tags=["Cliente"])
@limiter.limit(get_rate_limit("critical"))
async def put_cliente(request: Request, id: int, dados: ClienteUpdate, db: AsyncSession = Depends(get_db), current_user: FuncionarioAuth = Depends(require_group([1,3]))):
    cliente_antigo = await ClienteService.buscar_por_id(db, id)
    dados_antigos = cliente_antigo.__dict__.copy()
    cliente_atualizado = await ClienteService.atualizar(db, id, dados)
    await AuditoriaService.registrar_acao(db, current_user.id, "UPDATE", "CLIENTE", id, dados_antigos, cliente_atualizado, request)
    return cliente_atualizado

@router.delete("/cliente/{id}", status_code=204, tags=["Cliente"])
@limiter.limit(get_rate_limit("critical"))
async def delete_cliente(request: Request, id: int, db: AsyncSession = Depends(get_db), current_user: FuncionarioAuth = Depends(require_group([1]))):
    cliente = await ClienteService.deletar(db, id)
    await AuditoriaService.registrar_acao(db, current_user.id, "DELETE", "CLIENTE", id, cliente, None, request)
    return None