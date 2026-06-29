from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from slowapi.errors import RateLimitExceeded
import uvicorn

from settings import HOST, PORT, RELOAD
from infra.rate_limit import limiter, rate_limit_exceeded_handler

# Import das rotas
from routers import FuncionarioRouter, ClienteRouter, ProdutoRouter, AuthRouter, AuditoriaRouter, HealthRouter, ComandaRouter, CaixaRouter

# Lifespan
from infra import database
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("API has started")
    await database.cria_tabelas()
    yield
    print("API is shutting down")

# Criação da Aplicação
app = FastAPI(lifespan=lifespan)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Configuração de Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Tratamento Global de Erros de Banco de Dados
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, SQLAlchemyError):
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno no Banco de Dados.", "erro_tecnico": str(exc)}
        )
    raise exc

# Rota Padrão
@app.get("/", tags=["Root"], status_code=200)
async def root():
    return {"detail":"API Pastelaria", "Swagger UI": "http://127.0.0.1:8000/docs"}

# Mapeamento das Rotas
app.include_router(AuthRouter.router)
app.include_router(FuncionarioRouter.router)
app.include_router(ClienteRouter.router)
app.include_router(ProdutoRouter.router)
app.include_router(AuditoriaRouter.router)
app.include_router(HealthRouter.router)
app.include_router(ComandaRouter.router)
app.include_router(CaixaRouter.router)

if __name__ == "__main__":
    uvicorn.run('main:app', host=HOST, port=int(PORT), reload=RELOAD)