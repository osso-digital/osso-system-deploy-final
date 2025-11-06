# osso_lead.py
# Módulo: OssoLead (Agente de Geração de Leads e Follow-up)
# Gerencia a nutrição de leads que receberam orçamento mas não fecharam.

import os
from typing import List, Dict, Any
from datetime import datetime, timedelta

# Importa as ferramentas e o módulo de dados para acessar o BD
try:
    from osso_tools import log_evento
    from osso_data import carregar_todos_atendimentos
    from osso_tools import formatar_moeda # Para formatar o valor no follow-up
except ImportError:
    def log_evento(msg, nivel='INFO'): print(f"[{nivel}] osso_lead: {msg}")
    def formatar_moeda(valor): return f'R$ {valor:.2f}'
    def carregar_todos_atendimentos(): return []


DIAS_PARA_FOLLOWUP = 3  # Regra: Fazer follow-up em leads inativos há 3 dias
STATUS_ALVO = "Orçamento Calculado" # Status que precisa de follow-up

def identificar_leads_para_followup() -> List[Dict[str, Any]]:
    """
    Lê o Banco de Dados e identifica atendimentos com orçamento calculado
    que não foram fechados nem tiveram follow-up nos últimos DIAS_PARA_FOLLOWUP.
    """
    log_evento(f"Iniciando identificação de leads para follow-up após {DIAS_PARA_FOLLOWUP} dias.", 'INFO')
    
    atendimentos_bd = carregar_todos_atendimentos()
    leads_para_nutricao = []
    
    data_limite = datetime.now() - timedelta(days=DIAS_PARA_FOLLOWUP)

    for att in atendimentos_bd:
        
        # 1. Filtra por status: Deve ter orçamento calculado E não estar fechado
        if att.status_atendimento != STATUS_ALVO:
            continue
            
        # 2. Converte o timestamp (que é uma string no BD) para datetime
        try:
            att_data = datetime.strptime(str(att.timestamp)[:10], '%Y-%m-%d')
        except:
            # Ignora registros com formato de data inválido
            continue 
            
        # 3. Filtra por tempo: A data do orçamento deve ser anterior ao nosso limite
        if att_data < data_limite:
            
            # OBS: Em uma versão real, verificaríamos uma coluna "data_ultimo_followup"
            # Como não a temos, usamos a data do atendimento como proxy.
            
            leads_para_nutricao.append({
                'id_atendimento': att.id,
                'nome': att.nome_cliente,
                'whatsapp': att.whatsapp,
                'valor': formatar_moeda(att.valor_calculado),
                'servico_original': att.pergunta_cliente,
                'data_orcamento': att_data.strftime('%Y-%m-%d')
            })

    log_evento(f"Encontrados {len(leads_para_nutricao)} leads que precisam de follow-up.", 'INFO')
    return leads_para_nutricao


def simular_envio_followup(leads: List[Dict[str, Any]]):
    """
    Simula o envio de mensagens de follow-up (Ponto 7).
    """
    if not leads:
        log_evento("Nenhum lead encontrado para envio de follow-up.", 'INFO')
        return

    log_evento(f"Simulando envio de follow-up para {len(leads)} leads...", 'INFO')
    
    for lead in leads:
        mensagem = (
            f"🤖 Olá {lead['nome']}! Aqui é do Estúdio. "
            f"Vimos que seu orçamento de {lead['valor']} está pendente há {DIAS_PARA_FOLLOWUP} dias. "
            f"Podemos reservar seu horário para a sua tattoo?"
        )
        
        # OBS: O envio real chamaria o módulo osso_whatsapp.py
        
        log_evento(f"Mensagem de follow-up gerada para {lead['nome']} ({lead['whatsapp']})", 'DEBUG')
        print(">> MENSAGEM SIMULADA:", mensagem)
        
        # Aqui, o osso_data.py seria chamado para atualizar a coluna "data_ultimo_followup" no BD
        
    log_evento("Simulação de envio de follow-up concluída.", 'INFO')


# --- Bloco de Testes ---
if __name__ == '__main__':
    log_evento(f"Iniciando testes do {os.path.basename(__file__)} (OssoLead)", 'INFO')
    
    # IMPORTANTE: Este teste só encontrará leads se o seu BD tiver registros antigos!
    
    # 1. Identifica os leads (OssoLead)
    leads_pendentes = identificar_leads_para_followup()
    
    # 2. Simula o envio (OssoPós/OssoLead)
    simular_envio_followup(leads_pendentes)
    
    log_evento("Testes do osso_lead.py concluídos.", 'INFO')