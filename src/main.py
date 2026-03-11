from fastapi import FastAPI
from settings import HOST, PORT, RELOAD
import uvicorn

# Import das classes com as rotas/endpoints
from routers import FuncionarioRouter
from routers import ClienteRouter
from routers import ProdutoRouter

# import das classes com as rotas/endpoints
#from app import FuncionarioRouter
#from app import ClienteRouter

app = FastAPI()

# Mapeamento das rotas/endpoints
app.include_router(FuncionarioRouter.router)
app.include_router(ClienteRouter.router)
app.include_router(ProdutoRouter.router)

if __name__ == "__main__":
    uvicorn.run('main:app', host=HOST, port=int(PORT), reload=RELOAD)


#Osmar Steffen