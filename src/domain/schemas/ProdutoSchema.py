from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional

class ProdutoCreate(BaseModel):
    nome: str
    descricao: str 
    foto: bytes
    valor_unitario: Decimal

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    foto: Optional[bytes] = None
    valor_unitario: Optional[Decimal] = None

class ProdutoPublicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    nome: str
    descricao: str
    foto: bytes

class ProdutoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: str
    foto: bytes
    valor_unitario: Decimal

#Osmar Steffen