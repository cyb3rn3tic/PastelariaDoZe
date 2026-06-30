from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from infra.orm.ClienteModel import ClienteDB
from domain.schemas.ClienteSchema import ClienteCreate, ClienteUpdate

class ClienteService:
    @staticmethod
    async def listar_todos(db: AsyncSession):
        result = await db.execute(select(ClienteDB))
        return result.scalars().all()

    @staticmethod
    async def buscar_por_id(db: AsyncSession, id: int):
        result = await db.execute(select(ClienteDB).where(ClienteDB.id == id))
        cliente = result.scalars().first()
        if not cliente: raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return cliente

    @staticmethod
    async def criar(db: AsyncSession, dados: ClienteCreate):
        result = await db.execute(select(ClienteDB).where(ClienteDB.cpf == dados.cpf))
        if result.scalars().first(): raise HTTPException(status_code=400, detail="CPF já cadastrado")
        
        novo = ClienteDB(nome=dados.nome, cpf=dados.cpf, telefone=dados.telefone)
        db.add(novo)
        await db.commit()
        await db.refresh(novo)
        return novo

    @staticmethod
    async def atualizar(db: AsyncSession, id: int, dados: ClienteUpdate):
        cliente = await ClienteService.buscar_por_id(db, id)
        
        if dados.cpf and dados.cpf != cliente.cpf:
            result = await db.execute(select(ClienteDB).where(ClienteDB.cpf == dados.cpf))
            if result.scalars().first(): raise HTTPException(status_code=400, detail="CPF já em uso")
            
        update_data = dados.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(cliente, field, value)
            
        await db.commit()
        await db.refresh(cliente)
        return cliente

    @staticmethod
    async def deletar(db: AsyncSession, id: int):
        cliente = await ClienteService.buscar_por_id(db, id)
        await db.delete(cliente)
        await db.commit()
        return cliente
    
    #Osmar Steffen