from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from settings import STR_DATABASE
from sqlalchemy.orm import Session

# engine/conexão -> engine = create_engine("sqlite:///pastelaria_db.db", echo = True)
# cria o engine do banco de dados
engine = create_engine(STR_DATABASE, echo=True)

# session -> Session = sessionmaker(bind=engine)
# cria a sessão do banco de dados
Session = sessionmaker(bind=engine, autocommit=False, autoflush=True)

# base/ORM -> Base = declarative_base()
# para trabalhar com tabelas
Base = declarative_base()

# cria, caso não existam, as tabelas de todos os modelos que encontrar na aplicação (importados)
async def cria_tabelas():
    Base.metadata.create_all(engine)
    
# dependência para injetar a sessão do banco de dados nas rotas
def get_db():
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()
        




