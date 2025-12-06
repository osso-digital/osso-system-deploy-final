# -*- coding: utf-8 -*-
# osso_agent.py
# Módulo: Agente Principal (Orquestrador)

import os
import datetime
from typing import Dict, Any, Optional, Tuple

# Importa módulos auxiliares
from osso_tools import log_evento, calcular_proximo_dia_util
# ATENÇÃO: 'atualizar_orcamento' FOI REMOVIDO e a lógica foi mesclada em 'atualizar_status_atendimento'
# O osso_data agora usa FIRETORE
from osso_data import registrar_novo_atendimento, obter_atendimento_por_id, atualizar_status_atendimento, reset_bd_simulado, dump_atendimento, AtendimentoRef
from osso_agenda import verificar_disponibilidade_simulada, agendar_horario

# --- 1. Definições de Negócio (Simuladas) ---

# Tabela de preços e durações (Simulação de ML/IA)
TABELA_ESTIMATIVA = {
    'minimalista': {'preco': 250.00, 'duracao_h': 1.0},
    'pequena': {'preco': 500.00, 'duracao_h': 1.5},
    'media': {'preco': 1000.00, 'duracao_h': 3.0},
    'grande': {'preco': 2000.00, 'duracao_h': 5.0}
}

# --- 2. Funções do Agente ---

def determinar_tamanho_e_preco(ideia_tatuagem: str) -> Tuple[str, float, float]:
    """
    Simula a determinação do tamanho, preço e duração.
    """
    # Lógica de simulação simples baseada em palavras-chave
    if "minimalista" in ideia_tatuagem.lower() or "traco fino" in ideia_tatuagem.lower():
        tamanho_chave = 'minimalista'
    elif len(ideia_tatuagem) < 30:
        tamanho_chave = 'pequena'
    elif len(ideia_tatuagem) < 60:
        tamanho_chave = 'media'
    else:
        tamanho_chave = 'grande'
        
    estimativa = TABELA_ESTIMATIVA[tamanho_chave]
    preco = estimativa['preco']
    duracao = estimativa['duracao_h']
    
    log_evento(f"Determinado: {tamanho_chave} (R$ {preco:.2f}, {duracao:.1f}h)", 'DEBUG', 'osso_agent')
    return tamanho_chave, preco, duracao

def calculo_orcamento_e_duracao(atendimento_id: str, ideia_tatuagem: str) -> AtendimentoRef:
    """
    Calcula o orçamento e a duração e persiste no BD.
    """
    tamanho_chave, orcamento_base, duracao_horas = determinar_tamanho_e_preco(ideia_tatuagem)
    
    atendimento = obter_atendimento_por_id(atendimento_id)

    # CORREÇÃO: Usando a função atualizada para salvar orçamento e duração
    atualizar_status_atendimento(
        atendimento_id, 
        atendimento.status, # Mantém o status atual (ORCAMENTO_PENDENTE)
        orcamento_base=orcamento_base, 
        duracao_estimada=duracao_horas
    )
    
    return obter_atendimento_por_id(atendimento_id) # Retorna a ref atualizada

def gerar_resposta_orcamento(atendimento: AtendimentoRef, tamanho_chave: str) -> str:
    """
    Gera a mensagem de resposta com o orçamento.
    """
    orcamento = atendimento.orcamento_base
    desconto = orcamento * 0.1
    orcamento_pix = orcamento - desconto
    
    resposta = f"""Olá {atendimento.nome_cliente}, sou o Osso, assistente virtual do estúdio.

Com base na sua ideia, que parece ser uma tatuagem de tamanho **{tamanho_chave.upper()}**.
O valor base para uma tatuagem de tamanho **{tamanho_chave.upper()}** é de R$ {orcamento:.2f}.
Condição de pagamento:
- Valor à vista (Pix/Dinheiro) com 10% de desconto: **R$ {orcamento_pix:.2f}**.
- Em até 3x no cartão: **R$ {orcamento:.2f}** (sem juros).

Podemos prosseguir com o agendamento após a confirmação do pagamento de um sinal.

Você gostaria de prosseguir com o pagamento de sinal para reservar sua vaga?
"""
    return resposta

def gerar_resposta_agendamento_sucesso(atendimento: AtendimentoRef) -> str:
    """
    Gera a mensagem de confirmação de agendamento.
    """
    data = atendimento.data_agendamento
    hora = atendimento.hora_agendamento
    duracao = atendimento.duracao_estimada
    
    resposta = f"""
✅ **Agendamento Confirmado!**

Seu horário foi reservado com sucesso:
- **Data:** {data}
- **Início:** {hora}:00h
- **Duração Estimada:** {duracao:.1f} horas
- **Valor Total:** R$ {atendimento.orcamento_base:.2f}

Obrigado por confirmar o pagamento do sinal. Você receberá um lembrete no dia anterior.

Te esperamos no estúdio!
"""
    return resposta


# --- 3. Função Principal de Processamento ---

def processar_atendimento(
    dados_lead: Dict[str, str], 
    status_simulacao: str,
    atendimento_id_existente: Optional [str] = None
) -> Tuple[str, AtendimentoRef]:
    """
    Função principal que simula o fluxo do agente.
    """
    if atendimento_id_existente:
        atendimento_id = atendimento_id_existente
        atendimento = obter_atendimento_por_id(atendimento_id)
        if not atendimento:
            raise ValueError(f"Atendimento ID {atendimento_id} não encontrado.")
    else:
        # Se não existe, registra um novo atendimento
        atendimento = registrar_novo_atendimento(dados_lead, 'ORCAMENTO_PENDENTE')
        atendimento_id = atendimento.id

    log_evento(f"Processando atendimento ID {atendimento_id}. Status de Simulação: {status_simulacao}", 'INFO', 'osso_agent')

    # --- Fluxo de Orçamento (ORCAMENTO_PENDENTE -> ORCAMENTO_APRESENTADO) ---
    if atendimento.status == 'ORCAMENTO_PENDENTE':
        
        # 1. Determina o orçamento e duração, e salva no BD
        atendimento = calculo_orcamento_e_duracao(atendimento_id, atendimento.ideia_tatuagem)
        # Atenção: Esta linha pressupõe que orcamento_base é um valor único, o que é válido para simulação
        tamanho_chave = next(k for k, v in TABELA_ESTIMATIVA.items() if v['preco'] == atendimento.orcamento_base)
        
        # 2. Gera a resposta
        resposta = gerar_resposta_orcamento(atendimento, tamanho_chave)
        
        # 3. Atualiza o status
        atualizar_status_atendimento(atendimento_id, 'ORCAMENTO_APRESENTADO')
        
        return resposta, obter_atendimento_por_id(atendimento_id)

    # --- Fluxo de Agendamento (ORCAMENTO_APRESENTADO -> AGENDADO) ---
    if status_simulacao == 'AGENDADO':
        
        # 1. Simula a confirmação de pagamento
        atualizar_status_atendimento(atendimento_id, 'AGUARDANDO_PAGAMENTO')
        atualizar_status_atendimento(atendimento_id, 'PAGAMENTO_CONFIRMADO')
        log_evento(f"Simulação: Pagamento confirmado para ID {atendimento_id}.", 'INFO', 'osso_agent')
        
        # 2. Busca data alvo (próximo dia útil) e duração
        data_alvo = calcular_proximo_dia_util()
        data_alvo_str = data_alvo.strftime('%Y-%m-%d')
        duracao = atendimento.duracao_estimada
        
        # 3. Verifica disponibilidade
        # ATENÇÃO: verificar_disponibilidade_simulada precisa ser adaptada para o Firestore no osso_agenda.py!
        horarios_livres = verificar_disponibilidade_simulada(data_alvo_str, duracao)
        
        if not horarios_livres:
            return "Infelizmente não encontramos horários livres para a duração da sua tatuagem neste dia. Por favor, tente outra data.", atendimento
            
        # 4. Escolhe o primeiro horário livre
        hora_escolhida = horarios_livres[0]
        
        # 5. Tenta agendar (isso também atualiza o status para 'AGENDADO' no BD)
        if agendar_horario(atendimento_id, data_alvo_str, hora_escolhida, dados_lead['nome_cliente'], duracao):
            
            ref_agendada = obter_atendimento_por_id(atendimento_id)
            resposta = gerar_resposta_agendamento_sucesso(ref_agendada)
            return resposta, ref_agendada
        else:
            return "Houve um erro ao tentar bloquear o horário. A vaga pode ter sido preenchida.", atendimento

    # Outros status...
    return "Status não tratado na simulação.", atendimento