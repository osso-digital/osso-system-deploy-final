# -*- coding: utf-8 -*-
# followup_runner.py
# Módulo: Cron Job Simulator (Execução Noturna de Follow-up)
# Responsável por rodar o processo de Lead Nurturing para leads pendentes.

import os
from datetime import datetime

# Importa as ferramentas e a lógica de follow-up
try:
    from osso_tools import log_evento
    from osso_lead import identificar_leads_para_followup, realizar_followup
except ImportError as e:
    # Fallback para execução isolada ou ambiente de teste
    def log_evento(msg, nivel='INFO'): print(f"[{nivel}] {os.path.basename(__file__)}: {msg}")
    # Cria mocks se osso_lead falhar no import
    def identificar_leads_para_followup(): 
        log_evento("MOCK: osso_lead não disponível.", 'WARNING')
        return []
    def realizar_followup(leads):
        log_evento(f"MOCK: Não foi possível realizar follow-up para {len(leads)} leads.", 'WARNING')
    
def main():
    """
    Simula a execução noturna da rotina de follow-up (Cron Job).
    """
    timestamp_inicio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_evento(f"--- INÍCIO DA ROTINA DE FOLLOW-UP ({timestamp_inicio}) ---", 'PROCESS')
    
    try:
        # 1. Identifica quais leads estão pendentes (ex: inativos há 3 dias)
        leads_pendentes = identificar_leads_para_followup()
        
        num_pendentes = len(leads_pendentes)
        log_evento(f"Encontrados {num_pendentes} leads pendentes para follow-up.", 'PROCESS')
        
        if num_pendentes > 0:
            # 2. Executa a ação de follow-up (envio de WhatsApp)
            realizar_followup(leads_pendentes)
            log_evento(f"Follow-up realizado com sucesso para {num_pendentes} leads.", 'PROCESS')
        else:
            log_evento("Nenhum lead elegível para follow-up encontrado. Rotina encerrada.", 'PROCESS')

    except Exception as e:
        log_evento(f"ERRO CRÍTICO durante a execução do follow-up runner: {e}", 'CRITICAL')
        
    timestamp_fim = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_evento(f"--- FIM DA ROTINA DE FOLLOW-UP ({timestamp_fim}) ---", 'PROCESS')

if __name__ == '__main__':
    main()