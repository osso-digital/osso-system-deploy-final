# -*- coding: utf-8 -*-
# osso_agenda.py
# Módulo: Agenda (Firestore) - Implementação persistente

import datetime
from typing import List, Dict, Any, Tuple
from osso_tools import log_evento
# O osso_data.py já inicializa o Firebase. Importamos DB diretamente.
from osso_data import obter_atendimento_por_id, atualizar_status_atendimento, DB 

AGENDA_COLLECTION = 'agenda'

# --- Definições da Agenda ---
HORARIO_INICIO = 9  # 9h
HORARIO_FIM = 18  # 18h
BLOCO_MINUTOS = 60 # Blocos de 1 hora

def calcular_blocos_necessarios(duracao_horas: float) -> int:
    """Calcula quantos blocos de 60 minutos são necessários."""
    return max(1, int(duracao_horas * 60 / BLOCO_MINUTOS))

def formatar_data_firestore(data: datetime.date) -> str:
    """Formata a data como string YYYY-MM-DD para Firestore."""
    return data.strftime('%Y-%m-%d')

def _obter_agenda_dia(data_str: str) -> Dict[int, str]:
    """
    Busca o documento da agenda para o dia específico no Firestore.
    Retorna um dicionário {hora: id_atendimento}.
    """
    # Usa o cliente DB do osso_data.py
    doc_ref = DB.collection(AGENDA_COLLECTION).document(data_str)
    doc = doc_ref.get()
    
    if doc.exists:
        # A chave 'blocos' armazena o mapa da agenda
        return doc.to_dict().get('blocos', {})
    return {}

def _salvar_agenda_dia(data_str: str, blocos: Dict[int, str]):
    """Salva os blocos de agenda atualizados no Firestore."""
    # Usa o cliente DB do osso_data.py
    doc_ref = DB.collection(AGENDA_COLLECTION).document(data_str)
    doc_ref.set({'blocos': blocos})
    log_evento(f"Agenda salva no Firestore para {data_str}.", 'DEBUG', 'osso_agenda')


def verificar_disponibilidade_simulada(data_str: str, duracao_horas: float) -> List[int]:
    """
    Verifica os horários disponíveis para uma duração específica.
    """
    agenda_dia = _obter_agenda_dia(data_str)
    
    blocos_necessarios = calcular_blocos_necessarios(duracao_horas)
    horarios_livres = []

    log_evento(f"Verificando disponibilidade para {data_str} (Duração: {duracao_horas}h)...", 'INFO', 'Geral')

    for hora_inicio in range(HORARIO_INICIO, HORARIO_FIM - blocos_necessarios + 1):
        esta_livre = True
        
        # Verifica se todos os blocos necessários estão livres
        for i in range(blocos_necessarios):
            bloco_hora = hora_inicio + i
            if bloco_hora in agenda_dia:
                esta_livre = False
                break
        
        if esta_livre:
            horarios_livres.append(hora_inicio)

    return horarios_livres

def agendar_horario(
    atendimento_id: str, 
    data_str: str, 
    hora_inicio: int, 
    nome_cliente: str, 
    duracao_horas: float
) -> bool:
    """
    Bloqueia o horário no Firestore.
    """
    agenda_dia = _obter_agenda_dia(data_str)
    blocos_necessarios = calcular_blocos_necessarios(duracao_horas)
    
    # 1. Checagem dupla (para evitar conflitos de última hora)
    for i in range(blocos_necessarios):
        bloco_hora = hora_inicio + i
        if bloco_hora in agenda_dia:
            log_evento(f"ERRO: Conflito de agendamento detectado em {data_str} às {bloco_hora}h.", 'ERROR', 'Geral')
            return False

    # 2. Bloqueia os blocos
    for i in range(blocos_necessarios):
        bloco_hora = hora_inicio + i
        agenda_dia[bloco_hora] = atendimento_id # O valor é o ID do documento

    # 3. Salva no Firestore
    try:
        _salvar_agenda_dia(data_str, agenda_dia)
        
        # 4. Atualiza o status do atendimento para AGENDADO
        atualizar_status_atendimento(
            atendimento_id, 
            'AGENDADO', 
            data_agendamento=data_str, 
            hora_agendamento=hora_inicio
        )
        
        log_evento(f"SUCESSO: Agendamento criado para {nome_cliente} (ID: {atendimento_id}) em {data_str} às {hora_inicio}h. BD atualizado.", 'INFO', 'Geral')
        return True
    except Exception as e:
        log_evento(f"ERRO ao salvar o agendamento no Firestore: {e}", 'ERROR', 'Geral')
        return False