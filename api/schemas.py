from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class LeadCreate(BaseModel):
    nome: str
    email: Optional[str]
    whatsapp: str
    origem: Optional[str] = "landing"
    nicho: Optional[str] = "tattoo"
    mensagem: Optional[str]

class OrcamentoIn(BaseModel):
    pergunta: str
    parametros: Optional[dict] = {}

class AgendamentoIn(BaseModel):
    lead_id: str
    profissional: Optional[str]
    data_inicio: datetime
    data_fim: Optional[datetime] = None
    observacoes: Optional[str] = None

class AnamneseIn(BaseModel):
    lead_id: str
    respostas: dict
    termo_versao: Optional[str]
    termo_aceito: bool = False

class PresignedUrlResponse(BaseModel):
    upload_url: str
    public_url: str
    storage_key: str
