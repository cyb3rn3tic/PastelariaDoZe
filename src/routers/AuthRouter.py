from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta

from domain.schemas.AuthSchema import LoginRequest, TokenResponse, RefreshTokenRequest, FuncionarioAuth
from infra.orm.FuncionarioModel import FuncionarioDB
from infra.database import get_db
from infra.security import verify_password, get_password_hash, create_access_token, create_refresh_token, verify_refresh_token
from infra.dependencies import get_current_active_user
from infra.rate_limit import limiter, get_rate_limit
from services.AuditoriaService import AuditoriaService
from settings import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

router = APIRouter()

# Rota especial para semear o banco (Cria o seu Admin ou reseta a senha)
@router.post("/auth/setup", tags=["Autenticação"], summary="Criar ou Resetar Usuário Admin")
async def setup_admin(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FuncionarioDB).where(FuncionarioDB.cpf == "1"))
    admin = result.scalars().first()
    
    if admin:
        # Se o admin já existe, força a atualização da senha para a criptografia correta!
        admin.senha = get_password_hash("123")
        await db.commit()
        return {"message": "Admin já existia! A senha foi resetada e criptografada novamente para '123'!"}
    
    # Se não existe, cria do zero
    novo_admin = FuncionarioDB(
        nome="Osmar Steffen (Admin)", matricula="0001", cpf="1", 
        telefone="49999999999", grupo=1, senha=get_password_hash("123")
    )
    db.add(novo_admin)
    await db.commit()
    return {"message": "Admin criado com sucesso! CPF: 1, Senha: 123"}

@router.post("/auth/login", response_model=TokenResponse, tags=["Autenticação"])
@limiter.limit(get_rate_limit("critical"))
async def login(request: Request, login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FuncionarioDB).where(FuncionarioDB.cpf == login_data.cpf))
    funcionario = result.scalars().first()
    
    if not funcionario or not verify_password(login_data.senha, funcionario.senha):
        raise HTTPException(status_code=401, detail="CPF ou senha inválidos")

    access_token = create_access_token(
        data={"sub": funcionario.cpf, "id": funcionario.id, "grupo": funcionario.grupo},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data={"sub": funcionario.cpf, "id": funcionario.id, "grupo": funcionario.grupo}
    )

    await AuditoriaService.registrar_acao(db, funcionario.id, "LOGIN", "AUTH", None, None, None, request)

    return TokenResponse(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60, refresh_expires_in=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

@router.post("/auth/refresh", response_model=TokenResponse, tags=["Autenticação"])
@limiter.limit(get_rate_limit("critical"))
async def refresh_token(request: Request, refresh_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    payload = verify_refresh_token(refresh_data.refresh_token)
    result = await db.execute(select(FuncionarioDB).where(FuncionarioDB.cpf == payload.get("sub")))
    funcionario = result.scalars().first()
    
    if not funcionario: raise HTTPException(status_code=401, detail="Funcionário não encontrado")

    access_token = create_access_token(
        data={"sub": funcionario.cpf, "id": funcionario.id, "grupo": funcionario.grupo},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    new_refresh_token = create_refresh_token(data={"sub": funcionario.cpf, "id": funcionario.id, "grupo": funcionario.grupo})
    return TokenResponse(
        access_token=access_token, refresh_token=new_refresh_token, token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60, refresh_expires_in=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

@router.get("/auth/me", response_model=FuncionarioAuth, tags=["Autenticação"])
async def get_current_user_info(current_user: FuncionarioAuth = Depends(get_current_active_user)):
    return current_user

#Osmar Steffen