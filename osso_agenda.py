# osso_agenda.py
# Módulo: OssoAgenda (Agente de Agendamento)
# Gerencia a disponibilidade do estúdio e o agendamento.

import os
import datetime
from typing import List, Dict, Any, Tuple

# Importa as ferramentas essenciais
try:
    from osso_tools import log_evento, obter_data_hora_atual
    # OssoData seria usado aqui para atualizar o status do atendimento para "AGENDADO"
    # from osso_data import atualizar_status_atendimento 
except ImportError:
    def log_evento(msg, nivel='INFO'): print(f"[{nivel}] osso_agenda: {msg}")
    def obter_data_hora_atual(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- SIMULAÇÃO DO CALENDÁRIO (Substitui a API do Google Calendar) ---
# Horários fixos indisponíveis (Data, Hora de Início)
CALENDARIO_SIMULADO = [
    ("2025-11-10", 10), # Segunda, 10h ocupada
    ("2025-11-10", 14), # Segunda, 14h ocupada
    ("2025-11-11", 11), # Terça, 11h ocupada
]
HORARIO_INICIO = 9
HORARIO_FIM = 18

def verificar_disponibilidade_simulada(data_alvo: str, duracao_horas: int = 2) -> List[int]:
    """
    Verifica quais horários estão livres para agendamento em uma data alvo.
    Retorna uma lista de horas livres (9, 11, 13, etc.).
    """
    log_evento(f"Verificando disponibilidade para {data_alvo}...", 'INFO')
    
    try:
        data_hoje = datetime.datetime.strptime(obter_data_hora_atual()[:10], '%Y-%m-%d').date()
        data_check = datetime.datetime.strptime(data_alvo, '%Y-%m-%d').date()
    except ValueError:
        log_evento("Formato de data inválido. Use AAAA-MM-DD.", 'ERROR')
        return []

    # Ignora datas passadas
    if data_check <= data_hoje:
        log_evento("Data inválida ou no passado.", 'WARNING')
        return []

    horarios_livres = []
    
    for hora in range(HORARIO_INICIO, HORARIO_FIM):
        is_livre = True
        
        # 1. Verifica se a hora de início ou o slot de duração estão bloqueados
        for i in range(duracao_horas):
            if (data_alvo, hora + i) in CALENDARIO_SIMULADO or (hora + i) >= HORARIO_FIM:
                is_livre = False
                break
        
        if is_livre:
            horarios_livres.append(hora)
            
    return horarios_livres

def agendar_horario(atendimento_id: int, data: str, hora: int, cliente: str) -> bool:
    """
    Simula a criação de um evento no Google Calendar (Ponto 5).
    """
    log_evento(f"Tentando agendar {cliente} para {data} às {hora}h...", 'INFO')
    
    # 1. Checagem final (simulando 2 horas de duração)
    horarios_disponiveis = verificar_disponibilidade_simulada(data, duracao_horas=2)
    if hora not in horarios_disponiveis:
        log_evento(f"Falha: O horário {hora}h em {data} não está mais disponível.", 'ERROR')
        return False
        
    # 2. Simulação de Criação do Evento
    # Se fosse real, isso chamaria a API do Google Calendar e o osso_data.py
    
    # 3. Simulação de Inserção no Calendário Fictício (para teste)
    CALENDARIO_SIMULADO.append((data, hora))
    # Bloqueia a próxima hora para o teste de 2 horas
    CALENDARIO_SIMULADO.append((data, hora + 1)) 
    
    log_evento(f"SUCESSO: Agendamento criado para {cliente} às {hora}h em {data}. ID: {atendimento_id}", 'INFO')
    
    # OBS: Aqui o osso_data.py seria chamado para mudar o status do atendimento no BD para "AGENDADO"
    
    return True

# --- Bloco de Testes ---
if __name__ == '__main__':
    log_evento(f"Iniciando testes do {os.path.basename(__file__)} (OssoAgenda)", 'INFO')
    
    # Testa a disponibilidade na Segunda-feira (2025-11-10)
    print("\n--- Teste 1: Disponibilidade na Segunda (10/11) ---")
    data_segunda = "2025-11-10"
    livres_segunda = verificar_disponibilidade_simulada(data_segunda, duracao_horas=2)
    print(f"Horários livres em {data_segunda} (2h): {livres_segunda}") 
    
    # Tenta agendar para a Segunda às 12h (2h de duração)
    print("\n--- Teste 2: Agendamento e Bloqueio ---")
    cliente_teste = "Cliente Agenda Teste"
    hora_alvo = 12
    
    if agendar_horario(999, data_segunda, hora_alvo, cliente_teste):
        print(f"Resultado: Agendamento SUCEEDED para {hora_alvo}h.")
    else:
        print(f"Resultado: Agendamento FAILED para {hora_alvo}h.")
        
    # Verifica a disponibilidade novamente (o horário 12h e 13h devem ter sumido)
    print("\n--- Teste 3: Verificação Pós-Agendamento ---")
    livres_depois = verificar_disponibilidade_simulada(data_segunda, duracao_horas=2)
    print(f"Horários livres em {data_segunda} (DEPOIS): {livres_depois}")

    log_evento("Testes do osso_agenda.py concluídos.", 'INFO')