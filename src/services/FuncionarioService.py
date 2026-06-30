from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from infra.orm.FuncionarioModel import FuncionarioDB
from infra.security import get_password_hash
from domain.schemas.FuncionarioSchema import FuncionarioCreate, FuncionarioUpdate

class FuncionarioService:
    
    @staticmethod
    async def listar_todos(db: AsyncSession):
        result = await db.execute(select(FuncionarioDB))
        return result.scalars().all()

    @staticmethod
    async def criar(db: AsyncSession, dados: FuncionarioCreate):
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

    @staticmethod
    async def deletar(db: AsyncSession, id: int):
        # 1. Busca o funcionário pelo ID
        result = await db.execute(select(FuncionarioDB).where(FuncionarioDB.id == id))
        funcionario = result.scalars().first()
        
        # 2. Se não encontrar, retorna erro 404
        if not funcionario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Funcionário não encontrado"
            )
        
        # 3. Deleta o registro e comita a transação
        await db.delete(funcionario)
        await db.commit()
        return True
    
    #Osmar Steffen