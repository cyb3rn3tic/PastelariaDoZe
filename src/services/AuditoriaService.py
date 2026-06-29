from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from typing import Optional, Dict, Any
from datetime import datetime
import json
from infra.orm.AuditoriaModel import AuditoriaDB

class AuditoriaService:
    @staticmethod
    async def registrar_acao(
        db: AsyncSession, funcionario_id: int, acao: str, recurso: str, 
        recurso_id: Optional[int] = None, dados_antigos: Optional[Dict[str, Any]] = None,
        dados_novos: Optional[Dict[str, Any]] = None, request: Optional[Request] = None
    ) -> bool:
        try:
            ip_address = request.client.host if request else None
            user_agent = request.headers.get("User-Agent") if request else None

            # Conversão segura para JSON
            def parse_data(data):
                if not data: return None
                if hasattr(data, '__dict__'):
                    return json.dumps({c.name: getattr(data, c.name) for c in data.__table__.columns}, default=str)
                return json.dumps(data, default=str)

            auditoria = AuditoriaDB(
                funcionario_id=funcionario_id, acao=acao, recurso=recurso, 
                recurso_id=recurso_id, dados_antigos=parse_data(dados_antigos), 
                dados_novos=parse_data(dados_novos), ip_address=ip_address, 
                user_agent=user_agent, data_hora=datetime.now()
            )
    
            db.add(auditoria)
            await db.commit() # Agora usa await
            return True
        except Exception:
            await db.rollback()
            return False