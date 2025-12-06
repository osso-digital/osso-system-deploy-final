# -*- coding: utf-8 -*-
# osso_lead.py
# Módulo: OssoLead (Agente de Geração de Leads e Follow-up)
# Gerencia a nutrição de leads que receberam orçamento mas não fecharam.

from typing import List, Dict, Any
from datetime import datetime, timedelta

# Importa as ferramentas e o módulo de dados para acessar o BD
try:
    from osso_tools import log_evento, formatar_moeda
    from osso_data import carregar_todos_atendimentos
    from osso_whatsapp import construir_mensagem_followup, enviar_mensagem_whatsapp 
except ImportError:
    def log_evento(msg, nivel='INFO'): print(f"[{nivel}] osso_lead: {msg}")
    def formatar_moeda(valor): return f'R$ {valor:.2f}'
    def carregar_todos_atendimentos(): return []
    def construir_mensagem_followup(l, d): return "Mensagem de Follow-up Simulado"
    def enviar_mensagem_whatsapp(w, m): return True # Mock

DIAS_PARA_FOLLOWUP = 3  # Regra: Fazer follow-up em leads inativos há 3 dias
STATUS_ALVO = "Orçamento Calculado" # Status que precisa de follow-up (ou seja, não agendou nem fechou)

def identificar_leads_para_followup() -> List[Dict[str, Any]]:
    """
    Lê o Banco de Dados e identifica atendimentos com status 'Orçamento Calculado'
    e que foram registrados há mais de DIAS_PARA_FOLLOWUP dias.
    """
    log_evento(f"Iniciando identificação de leads para follow-up após {DIAS_PARA_FOLLOWUP} dias.", 'PROCESS')
    
    try:
        from osso_data import Atendimento
    except ImportError:
        class Atendimento:
            def __init__(self, **kwargs):
                self.id = kwargs.get('id', 0)
                self.nome_cliente = kwargs.get('nome_cliente', 'Nome Mock')
                self.whatsapp = kwargs.get('whatsapp', '00000000000')
                self.pergunta_cliente = kwargs.get('pergunta_cliente', 'Pergunta Mock')
                self.valor_calculado = kwargs.get('valor_calculado', 0.0)
                self.status_atendimento = kwargs.get('status_atendimento', 'Novo Lead')
                self.timestamp = kwargs.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    atendimentos_bd: List[Atendimento] = carregar_todos_atendimentos()
    leads_para_nutricao = []
    
    data_limite = datetime.now() - timedelta(days=DIAS_PARA_FOLLOWUP)

    for att in atendimentos_bd:
        
        # 1. Filtra por status: Deve ter orçamento calculado (não agendou, não fechou)
        if att.status_atendimento != STATUS_ALVO:
            continue
            
        # 2. Converte o timestamp (YYYY-MM-DD HH:MM:SS) para datetime
        try:
            # Pega apenas a parte da data para a comparação
            att_data_str = att.timestamp.split(' ')[0] 
            att_data = datetime.strptime(att_data_str, '%Y-%m-%d')
        except Exception as e:
            log_evento(f"Pulando lead ID {att.id} com data inválida ({att.timestamp}): {e}", 'DEBUG')
            continue 
            
        # 3. Filtra por tempo: A data do orçamento deve ser anterior ou igual ao nosso limite
        if att_data <= data_limite:
            
            dias_pendente = (datetime.now() - att_data).days
            
            leads_para_nutricao.append({
                'id_atendimento': att.id,
                'nome': att.nome_cliente,
                'whatsapp': att.whatsapp,
                'valor_calculado': att.valor_calculado,
                'servico_original': att.pergunta_cliente,
                'data_orcamento': att_data.strftime('%Y-%m-%d'),
                'dias_pendente': dias_pendente
            })

    log_evento(f"Encontrados {len(leads_para_nutricao)} leads que precisam de follow-up.", 'INFO')
    return leads_para_nutricao


def realizar_followup(leads: List[Dict[str, Any]]):
    """
    Constrói e simula o envio de mensagens de follow-up (Ponto 7).
    """
    if not leads:
        log_evento("Nenhum lead encontrado para envio de follow-up.", 'INFO')
        return

    log_evento(f"Iniciando envio de follow-up para {len(leads)} leads...", 'PROCESS')
    
    for lead in leads:
        
        mensagem = construir_mensagem_followup(lead, lead['dias_pendente'])
        
        enviado = enviar_mensagem_whatsapp(lead['whatsapp'], mensagem)
        
        if enviado:
            log_evento(f"Follow-up enviado com sucesso para ID {lead['id_atendimento']} ({lead['nome']})", 'WHATSAPP')
        else:
            log_evento(f"Falha no envio de follow-up para ID {lead['id_atendimento']}.", 'ERROR')
            
    log_evento("Processo de follow-up concluído.", 'INFO')