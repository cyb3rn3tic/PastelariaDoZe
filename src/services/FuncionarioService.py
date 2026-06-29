from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from infra.orm.FuncionarioModel import FuncionarioDB
from infra.security import get_password_hash
from domain.schemas.FuncionarioSchema import FuncionarioCreate, FuncionarioUpdate

class FuncionarioService:
    
    @staticmethod
    async def listar_todos(db: AsyncSession):
        # O novo padrão do SQLAlchemy 2.0 para buscas Async
        result = await db.execute(select(FuncionarioDB))
        return result.scalars().all()

    @staticmethod
    async def criar(db: AsyncSession, dados: FuncionarioCreate):
        # Verifica CPF duplicado
        result = await db.execute(select(FuncionarioDB).where(FuncionarioDB.cpf == dados.cpf))
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Já existe um funcionário com este CPF")
        
        novo = FuncionarioDB(
            nome=dados.nome,
            matricula=dados.matricula,
            cpf=dados.cpf,
            telefone=dados.telefone,
            grupo=dados.grupo,
            senha=get_password_hash(dados.senha)
        )
        db.add(novo)
        await db.commit()
        await db.refresh(novo)
        return novo