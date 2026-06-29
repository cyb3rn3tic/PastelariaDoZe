from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from infra.database import get_db
from infra.orm.FuncionarioModel import FuncionarioDB
from infra.security import verify_access_token
from domain.schemas.AuthSchema import FuncionarioAuth

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> FuncionarioAuth:
    
    payload = verify_access_token(credentials.credentials)
    cpf: str = payload.get("sub")
    id_funcionario: int = payload.get("id")
    
    if cpf is None or id_funcionario is None:
        raise HTTPException(status_code=401, detail="Token inválido - dados incompletos")

    result = await db.execute(select(FuncionarioDB).where(FuncionarioDB.id == id_funcionario))
    funcionario = result.scalars().first()
    
    if not funcionario or funcionario.cpf != cpf:
        raise HTTPException(status_code=401, detail="Funcionário não encontrado ou CPF não corresponde")

    return FuncionarioAuth(
        id=funcionario.id, nome=funcionario.nome, matricula=funcionario.matricula, 
        cpf=funcionario.cpf, grupo=funcionario.grupo
    )

async def get_current_active_user(current_user: FuncionarioAuth = Depends(get_current_user)) -> FuncionarioAuth:
    return current_user

def require_group(group_required: list[int] = None):
    async def check_group(current_user: FuncionarioAuth = Depends(get_current_active_user)) -> FuncionarioAuth:
        if group_required is None:
            return current_user
        
        if current_user.grupo not in group_required:
            raise HTTPException(status_code=403, detail="Permissão negada - nível insuficiente")
        return current_user
    return check_group