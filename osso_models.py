# osso_models.py
# Módulo: Modelagem de Dados (Camada de Abstração) - VERSÃO FINAL CORRIGIDA

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker 
from typing import Optional # Mantém a tipagem limpa
import os
import pandas as pd 

# Importa as ferramentas e o NOVO MÓDULO DE CONFIGURAÇÃO
try:
    from osso_tools import log_evento
    from osso_config import DATABASE_URL 
except ImportError:
    DATABASE_URL = "sqlite:///osso_database.db"
    def log_evento(msg, nivel='INFO'): print(f"[{nivel}] osso_models: {msg}")

Base = declarative_base()

class Estudio(Base):
    __tablename__ = 'estudio'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)

class Atendimento(Base):
    __tablename__ = 'atendimento'
    
    id = Column(Integer, primary_key=True)
    id_estudio = Column(Integer, default=1) 
    
    timestamp = Column(DateTime)
    nome_cliente = Column(String(100))
    whatsapp = Column(String(20))
    pergunta_cliente = Column(String(500))
    
    status_atendimento = Column(String(50)) 
    resposta_osobot = Column(String(1000)) 
    
    valor_calculado = Column(Float)
    id_orcamento = Column(String(50)) 

    def __repr__(self):
        return f"<Atendimento(id={self.id}, cliente='{self.nome_cliente}', status='{self.status_atendimento}')>"

engine = create_engine(DATABASE_URL) 
SessionLocal = sessionmaker(bind=engine) 

def criar_tabelas():
    Base.metadata.create_all(bind=engine)

def iniciar_estrutura_banco():
    try:
        criar_tabelas()
        log_evento("Estrutura do banco de dados inicializada.", 'INFO')
    except Exception as e:
        log_evento(f"Erro ao criar tabelas do BD: {e}", 'CRITICAL')