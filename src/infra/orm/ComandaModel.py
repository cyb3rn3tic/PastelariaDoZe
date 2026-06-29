from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from infra.database import Base

class ComandaDB(Base):
    __tablename__ = "tb_comanda"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    comanda = Column(String(100), nullable=False)
    cliente = Column(String(100), default="Cliente Balcão")
    total = Column(Float, default=0.0)
    status = Column(Integer, default=0) # 0 = Aberta, 1 = Fechada
    data_hora = Column(DateTime, default=datetime.now)