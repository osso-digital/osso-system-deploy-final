# osso_data.py
# Módulo: OssoData (O Arquivista) - VERSÃO FINAL ESTÁVEL COM BD (Removido o campo 'email' problemático)

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Dict, Any, List 
import os

# Importa as ferramentas de log e a estrutura do banco de dados
try:
    from osso_tools import log_evento
    from osso_models import SessionLocal, criar_tabelas, Atendimento 
except ImportError as e:
    log_evento(f"ERRO CRÍTICO: Falha ao importar dependências do BD. {e}", 'CRITICAL')
    class StubSession:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass
    SessionLocal = StubSession 

def inicializar_banco_dados():
    try:
        criar_tabelas()
        log_evento("Estrutura do banco de dados inicializada (BD).", 'INFO')
    except Exception as e:
        log_evento(f"Erro ao criar tabelas do BD: {e}", 'CRITICAL')

def registrar_novo_atendimento(dados_cliente: dict) -> Atendimento | None:
    """
    Cria uma nova entrada de atendimento no BD.
    CORRIGIDO: O campo 'email' foi removido para evitar o erro de chave inválida.
    """
    
    # 1. Cria um dicionário limpo com apenas os campos do BD
    dados_limpos = {
        'nome_cliente': dados_cliente.get('nome_cliente', 'Sem Nome'),
        'whatsapp': dados_cliente.get('whatsapp', 'N/A'),
        # 'email' FOI REMOVIDO PARA EVITAR O ERRO CRÍTICO DE CHAVE INVÁLIDA NO SQLAlchemy
        'pergunta_cliente': dados_cliente.get('pergunta_cliente', 'Vazio'),
        'status_atendimento': "Orçamento Pendente"
    }
    
    novo_atendimento = Atendimento(**dados_limpos)
    
    # 2. Salva no BD
    try:
        with SessionLocal() as session:
            session.add(novo_atendimento)
            session.commit() 
            session.refresh(novo_atendimento) 
        log_evento(f"Novo atendimento registrado para '{novo_atendimento.nome_cliente}' (ID: {novo_atendimento.id}).", 'INFO')
        return novo_atendimento
    except Exception as e:
        log_evento(f"Erro ao registrar novo atendimento no BD: {e}", 'ERROR')
        return None

def carregar_todos_atendimentos() -> List[Atendimento]:
    # Lógica de leitura...
    try:
        with SessionLocal() as session:
            stmt = select(Atendimento)
            atendimentos = session.execute(stmt).scalars().all()
        return atendimentos
    except Exception as e:
        log_evento(f"Erro ao carregar atendimentos do BD: {e}", 'ERROR')
        return []

def obter_resumo_atendimentos(atendimentos: List[Atendimento]) -> Dict[str, Any]:
    # Lógica de resumo...
    if not atendimentos:
        return {'total_atendimentos': 0, 'clientes_unicos': 0, 'contagem_status': {}}

    df = pd.DataFrame([{
        'nome_cliente': a.nome_cliente,
        'status_atendimento': a.status_atendimento
    } for a in atendimentos])

    total_atendimentos = len(df)
    clientes_unicos = df['nome_cliente'].nunique()
    contagem_status = df['status_atendimento'].value_counts().to_dict()

    return {
        'total_atendimentos': total_atendimentos,
        'clientes_unicos': clientes_unicos,
        'contagem_status': contagem_status
    }

def atualizar_orcamento_atendimento(atendimento_id: int, valor: float, id_orcamento: str) -> bool:
    # Lógica de atualização...
    try:
        with SessionLocal() as session:
            atendimento = session.get(Atendimento, atendimento_id)
            if not atendimento:
                log_evento(f"Atendimento ID {atendimento_id} não encontrado para atualização.", 'WARNING')
                return False
            
            atendimento.valor_calculado = valor
            atendimento.id_orcamento = id_orcamento
            atendimento.status_atendimento = "Orçamento Calculado"
            
            session.commit()
            return True
    except Exception as e:
        log_evento(f"Erro ao atualizar orçamento no BD: {e}", 'ERROR')
        return False

# --- Bloco de Testes ---
if __name__ == '__main__':
    log_evento("Iniciando testes do Módulo OssoData...", 'INFO')
    inicializar_banco_dados()
    log_evento("Testes do osso_data.py concluídos.", 'INFO')