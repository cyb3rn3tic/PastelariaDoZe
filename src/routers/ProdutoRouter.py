from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from domain.schemas.ProdutoSchema import ProdutoCreate, ProdutoUpdate, ProdutoResponse, ProdutoPublicResponse
from domain.schemas.AuthSchema import FuncionarioAuth
from infra.database import get_db
from infra.dependencies import get_current_active_user, require_group
from services.ProdutoService import ProdutoService
from services.AuditoriaService import AuditoriaService
from infra.rate_limit import limiter, get_rate_limit

router = APIRouter()

@router.get("/publico/", response_model=List[ProdutoPublicResponse], tags=["Produto"])
async def get_produtos_publico(db: AsyncSession = Depends(get_db)):
    return await ProdutoService.listar_todos(db)

@router.get("/produto/", response_model=List[ProdutoResponse], tags=["Produto"])
async def get_produtos(db: AsyncSession = Depends(get_db), current_user: FuncionarioAuth = Depends(get_current_active_user)):
    return await ProdutoService.listar_todos(db)

@router.get("/produto/{id}", response_model=ProdutoResponse, tags=["Produto"])
async def get_produto(id: int, db: AsyncSession = Depends(get_db), current_user: FuncionarioAuth = Depends(get_current_active_user)):
    return await ProdutoService.buscar_por_id(db, id)

@router.post("/produto/", response_model=ProdutoResponse, status_code=201, tags=["Produto"])
async def post_produto(request: Request, dados: ProdutoCreate, db: AsyncSession = Depends(get_db), current_user: FuncionarioAuth = Depends(require_group([1]))):
    novo = await ProdutoService.criar(db, dados)
    await AuditoriaService.registrar_acao(db, current_user.id, "CREATE", "PRODUTO", novo.id, None, novo, request)
    return novo

@router.put("/produto/{id}", response_model=ProdutoResponse, tags=["Produto"])
@limiter.limit(get_rate_limit("critical"))
async def put_produto(request: Request, id: int, dados: ProdutoUpdate, db: AsyncSession = Depends(get_db), current_user: FuncionarioAuth = Depends(require_group([1]))):
    antigo = await ProdutoService.buscar_por_id(db, id)
    dados_antigos = antigo.__dict__.copy()
    atualizado = await ProdutoService.atualizar(db, id, dados)
    await AuditoriaService.registrar_acao(db, current_user.id, "UPDATE", "PRODUTO", id, dados_antigos, atualizado, request)
    return atualizado

@router.delete("/produto/{id}", status_code=204, tags=["Produto"])
@limiter.limit(get_rate_limit("critical"))
async def delete_produto(request: Request, id: int, db: AsyncSession = Depends(get_db), current_user: FuncionarioAuth = Depends(require_group([1]))):
    produto = await ProdutoService.deletar(db, id)
    await AuditoriaService.registrar_acao(db, current_user.id, "DELETE", "PRODUTO", id, produto, None, request)
    return None