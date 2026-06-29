from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # 1. Adicionado este import
from settings import HOST, PORT, RELOAD
from infra.rate_limit import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import uvicorn

# Import das classes com as rotas/endpoints
from routers import FuncionarioRouter, ClienteRouter, ProdutoRouter, AuthRouter, AuditoriaRouter, HealthRouter, ComandaRouter, CaixaRouter

# lifespan - ciclo de vida da aplicação
from infra import database
from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # executa no startup
    print("API has started")
    # cria, caso não existam, as tabelas de todos os modelos que encontrar na aplicação (importados)
    await database.cria_tabelas()
    yield
    # executa no shutdown
    print("API is shutting down")

# FastAPI criação da aplicação
app = FastAPI(lifespan=lifespan)

# 2. Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Configuração de Rate Limiting
app.state.limiter = limiter

# Registra handler personalizado ANTES de incluir rotas
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# rota padrão
@app.get("/", tags=["Root"], status_code=200)
async def root():
    return {"detail":"API Pastelaria", "Swagger UI": "http://127.0.0.1:8000/docs", "ReDoc": "http://127.0.0.1:8000/redoc" }

# Mapeamento das rotas/endpoints
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

#Osmar Steffen