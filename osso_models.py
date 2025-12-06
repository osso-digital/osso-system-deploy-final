# -*- coding: utf-8 -*-
# osso_models.py
# Módulo: OssoModels (Definição de Modelos ORM)
# Define a estrutura de dados e conexão com o banco SQLite.

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import os
from osso_tools import log_evento

# --- Configuração do Banco de Dados ---
# Usamos um arquivo SQLite chamado 'osso_database.db' no diretório atual.
DATABASE_FILE = 'osso_database.db'
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# Cria o motor de conexão
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Necessário para SQLite com FastAPI/Flask
)

# Cria a classe Base para os modelos declarativos
Base = declarative_base()

# Cria a sessão de acesso ao BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Definição do Modelo (Tabela) ---

class Atendimento(Base):
    """Modelo ORM para a tabela 'atendimentos' que armazena os leads e orçamentos."""
    
    __tablename__ = "atendimentos"

    # Campos obrigatórios
    id = Column(Integer, primary_key=True, index=True)
    timestamp_registro = Column(DateTime, default=datetime.now, nullable=False)
    nome_cliente = Column(String, index=True, nullable=False)
    whatsapp = Column(String, index=True, nullable=False)
    pergunta_cliente = Column(String, nullable=False)
    
    # Campos de Orçamento/Status
    status_atendimento = Column(String, default="Orçamento Pendente", nullable=False)
    valor_calculado = Column(Float, default=0.0)
    id_orcamento = Column(String, default=None)

    # Campos de Agendamento (preenchidos se o agendamento ocorrer)
    data_agendamento = Column(String, default=None)
    hora_agendamento = Column(String, default=None)
    
    def to_dict(self):
        """Converte o objeto ORM para um dicionário padrão, ignorando a sessão ORM."""
        return {
            "id": self.id,
            "timestamp_registro": self.timestamp_registro.isoformat() if self.timestamp_registro else None,
            "nome_cliente": self.nome_cliente,
            "whatsapp": self.whatsapp,
            "pergunta_cliente": self.pergunta_cliente,
            "status_atendimento": self.status_atendimento,
            "valor_calculado": self.valor_calculado,
            "id_orcamento": self.id_orcamento,
            "data_agendamento": self.data_agendamento,
            "hora_agendamento": self.hora_agendamento,
        }

# --- Função de Inicialização ---

def criar_tabelas():
    """Cria todas as tabelas no banco de dados, se não existirem."""
    Base.metadata.create_all(bind=engine)

# --- Bloco de Testes ---
if __name__ == '__main__':
    log_evento("Iniciando inicialização de BD via osso_models.py", 'INFO')
    criar_tabelas()
    log_evento(f"Banco de dados SQLite '{DATABASE_FILE}' está pronto.", 'INFO')