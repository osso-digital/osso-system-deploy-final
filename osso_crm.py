# -*- coding: utf-8 -*-
# osso_crm.py
# Módulo: CRM de Leads (Customer Relationship Management)
# Gerencia a persistência dos dados de leads e atendimentos, simulando
# a interação com um sistema de CRM externo via API.

import json
import os
import datetime
from typing import Dict, Any, List, Optional, Tuple

# O nome do arquivo onde os dados serão armazenados (simulação de um BD)
CRM_FILE = 'crm_database.json'
CALENDARIO_FILE = 'calendario_database.json'

# --- Estruturas de Dados Mock ---

class LeadRef:
    """Uma classe de referência simples para imitar um objeto de registro de BD/CRM."""
    def __init__(self, lead_id: int, data: Dict[str, Any]):
        self.id = lead_id
        self._data = data

    def __getitem__(self, key):
        return self._data.get(key)

    def to_dict(self):
        return {"id": self.id, **self._data}
        
# --- Funções de Persistência (Simulação de CRUD via Arquivo) ---

def _carregar_dados() -> Tuple[Dict[int, Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    """Carrega dados dos leads e do calendário dos arquivos JSON."""
    
    # 1. Carregar Dados do CRM (Leads/Atendimentos)
    leads = {}
    if os.path.exists(CRM_FILE) and os.path.getsize(CRM_FILE) > 0:
        try:
            with open(CRM_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Garantir que as chaves sejam inteiros, não strings
                leads = {int(k): v for k, v in data.items()}
        except json.JSONDecodeError:
            print(f"ERRO: Falha ao decodificar JSON em {CRM_FILE}. Iniciando vazio.")
    
    # 2. Carregar Dados do Calendário
    calendario = {}
    if os.path.exists(CALENDARIO_FILE) and os.path.getsize(CALENDARIO_FILE) > 0:
        try:
            with open(CALENDARIO_FILE, 'r', encoding='utf-8') as f:
                calendario = json.load(f)
        except json.JSONDecodeError:
            print(f"ERRO: Falha ao decodificar JSON em {CALENDARIO_FILE}. Iniciando vazio.")
            
    return leads, calendario

def _salvar_dados(leads: Dict[int, Dict[str, Any]], calendario: Dict[str, List[Dict[str, Any]]]):
    """Salva dados dos leads e do calendário nos arquivos JSON."""
    try:
        with open(CRM_FILE, 'w', encoding='utf-8') as f:
            # Salvar Leads (chaves como string)
            json.dump(leads, f, indent=4, ensure_ascii=False)
            
        with open(CALENDARIO_FILE, 'w', encoding='utf-8') as f:
            # Salvar Calendário
            json.dump(calendario, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        print(f"ERRO: Não foi possível salvar dados nos arquivos. Detalhe: {e}")

# --- Funções do CRM (Interface de API) ---

def criar_lead(dados_lead: Dict[str, Any]) -> LeadRef:
    """
    Simula a criação de um novo registro de Lead no CRM.
    Inicializa o status e gera um ID único.
    """
    leads, calendario = _carregar_dados()
    
    # Gera um ID incremental (simulando ID do BD)
    if leads:
        novo_id = max(leads.keys()) + 1
    else:
        novo_id = 1
        
    novo_registro = {
        'id': novo_id,
        'status': 'NOVO_LEAD',
        'data_criacao': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'orcamento_base': 0.0,
        'data_agendamento': None,
        'hora_agendamento': None,
        **dados_lead # Adiciona nome_cliente, whatsapp, pergunta_cliente etc.
    }
    
    leads[novo_id] = novo_registro
    _salvar_dados(leads, calendario)
    
    print(f"[CRM] Lead criado com ID: {novo_id}. Status: {novo_registro['status']}")
    return LeadRef(novo_id, novo_registro)

def obter_lead_por_id(lead_id: int) -> Optional[LeadRef]:
    """Busca um lead específico pelo seu ID."""
    leads, _ = _carregar_dados()
    lead_data = leads.get(lead_id)
    if lead_data:
        return LeadRef(lead_id, lead_data)
    return None

def obter_todos_leads() -> List[LeadRef]:
    """Retorna a lista completa de todos os leads/atendimentos."""
    leads, _ = _carregar_dados()
    return [LeadRef(id, data) for id, data in leads.items()]

def atualizar_propriedades_lead(lead_id: int, propriedades: Dict[str, Any]) -> bool:
    """
    Atualiza propriedades específicas do lead (ex: orcamento, status, data_agendamento).
    """
    leads, calendario = _carregar_dados()
    if lead_id not in leads:
        print(f"[CRM] ERRO: Lead ID {lead_id} não encontrado para atualização.")
        return False
        
    registro = leads[lead_id]
    
    # Atualiza apenas as propriedades fornecidas
    registro.update(propriedades)
    
    # Se o status foi alterado, loga
    if 'status' in propriedades:
        print(f"[CRM] Lead ID {lead_id} status atualizado para: {propriedades['status']}")

    _salvar_dados(leads, calendario)
    return True

# --- Funções de Calendário (Agenda) ---

def obter_agendamentos_dia(data_str: str) -> List[Dict[str, Any]]:
    """Busca todos os agendamentos registrados para uma data específica (YYYY-MM-DD)."""
    _, calendario = _carregar_dados()
    # Retorna uma lista vazia se a data não estiver no calendário
    return calendario.get(data_str, [])

def adicionar_agendamento(data_str: str, agendamento_data: Dict[str, Any]) -> bool:
    """
    Adiciona um novo agendamento ao calendário.
    Assume que a verificação de disponibilidade já foi feita.
    """
    leads, calendario = _carregar_dados()
    
    if data_str not in calendario:
        calendario[data_str] = []
        
    calendario[data_str].append(agendamento_data)
    
    # Ordena os agendamentos por hora para facilitar a leitura e verificação futura
    calendario[data_str].sort(key=lambda x: x['hora']) 
    
    _salvar_dados(leads, calendario)
    print(f"[CRM] Agendamento adicionado para {data_str} às {agendamento_data['hora']}:00h.")
    return True

# -----------------------------------------------------------------
if __name__ == '__main__':
    # Teste de inicialização e salvamento
    print("--- Teste de osso_crm.py ---")
    
    # 1. Criação de um lead
    dados_teste = {'nome_cliente': 'João Teste', 'whatsapp': '11999998888', 'pergunta_cliente': 'teste de criação'}
    lead_ref = criar_lead(dados_teste)
    
    # 2. Atualização de propriedades
    sucesso_atualizacao = atualizar_propriedades_lead(
        lead_ref.id, 
        {'status': 'AGUARDANDO_PAGAMENTO', 'orcamento_base': 450.00}
    )
    
    # 3. Busca e exibição
    lead_atualizado = obter_lead_por_id(lead_ref.id)
    if lead_atualizado and sucesso_atualizacao:
        print(f"\nLead {lead_atualizado.id} após atualização:")
        for k, v in lead_atualizado.to_dict().items():
            print(f" - {k}: {v}")
    
    # 4. Teste de agendamento
    hoje_str = datetime.datetime.now().strftime('%Y-%m-%d')
    novo_agendamento = {
        'lead_id': lead_ref.id,
        'nome_cliente': lead_atualizado['nome_cliente'],
        'hora': 14,
        'duracao_horas': 2.0
    }
    adicionar_agendamento(hoje_str, novo_agendamento)
    
    agendamentos_hoje = obter_agendamentos_dia(hoje_str)
    print(f"\nAgendamentos para hoje ({hoje_str}): {len(agendamentos_hoje)} registros.")
    
    print("\n--- Teste concluído ---")