from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from infra.orm.ProdutoModel import ProdutoDB
from domain.schemas.ProdutoSchema import ProdutoCreate, ProdutoUpdate

class ProdutoService:
    @staticmethod
    async def listar_todos(db: AsyncSession):
        result = await db.execute(select(ProdutoDB))
        return result.scalars().all()

    @staticmethod
    async def buscar_por_id(db: AsyncSession, id: int):
        result = await db.execute(select(ProdutoDB).where(ProdutoDB.id == id))
        produto = result.scalars().first()
        if not produto: raise HTTPException(status_code=404, detail="Produto não encontrado")
        return produto

    @staticmethod
    async def criar(db: AsyncSession, dados: ProdutoCreate):
        result = await db.execute(select(ProdutoDB).where(ProdutoDB.descricao == dados.descricao))
        if result.scalars().first(): raise HTTPException(status_code=400, detail="Produto com esta descrição já existe")
        
        novo = ProdutoDB(nome=dados.nome, descricao=dados.descricao, foto=dados.foto, valor_unitario=dados.valor_unitario)
        db.add(novo)
        await db.commit()
        await db.refresh(novo)
        return novo

    @staticmethod
    async def atualizar(db: AsyncSession, id: int, dados: ProdutoUpdate):
        produto = await ProdutoService.buscar_por_id(db, id)
        
        if dados.descricao and dados.descricao != produto.descricao:
            result = await db.execute(select(ProdutoDB).where(ProdutoDB.descricao == dados.descricao))
            if result.scalars().first(): raise HTTPException(status_code=400, detail="Descrição já em uso")
            
        for field, value in dados.model_dump(exclude_unset=True).items():
            setattr(produto, field, value)
            
        await db.commit()
        await db.refresh(produto)
        return produto

    @staticmethod
    async def deletar(db: AsyncSession, id: int):
        produto = await ProdutoService.buscar_por_id(db, id)
        await db.delete(produto)
        await db.commit()
        return produto