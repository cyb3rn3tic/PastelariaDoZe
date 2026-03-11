from pydantic import BaseModel

class Cliente(BaseModel):
    id_cliente: int = None # onde tem "None" é opcional
    nome: str
    cpf: str
    telefone: str

    #Osmar Steffen