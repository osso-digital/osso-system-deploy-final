# osso_orcamento.py
# Módulo: OssoPreço (O Vendedor/Calculista)
# Responsável pela lógica de cálculo de valor e atualização do BD.

import random
from typing import Dict, Any, List
import os
import pandas as pd # Mantido para compatibilidade com o fluxo de dados

# Importa as ferramentas e o módulo de dados (que agora usa BD)
try:
    from osso_tools import log_evento, formatar_moeda, obter_data_hora_atual
    # Importa as funções do BD
    from osso_data import carregar_todos_atendimentos, atualizar_orcamento_atendimento
    from osso_models import Atendimento # Necessário para tipagem
except ImportError as e:
    # Fallback se os módulos não forem encontrados
    def log_evento(msg, nivel='INFO'):
        print(f"[{nivel}] osso_orcamento: {msg}")
    def formatar_moeda(valor):
        return f'R$ {valor:.2f}'
    def obter_data_hora_atual():
        return "2025-10-31 19:00:00"
    def carregar_todos_atendimentos():
        log_evento("AVISO: Módulo osso_data/BD não carregado.", 'WARNING')
        return []

# Tabela de preços base para serviços (Pode ser movida para a tabela Configuracao do BD)
TABELA_PRECOS_BASE = {
    'FÊNIX': {'base': 800.00, 'complexidade_min': 1.2, 'complexidade_max': 1.8},
    'FLORAL': {'base': 250.00, 'complexidade_min': 1.0, 'complexidade_max': 1.5},
    'GEOMÉTRICA': {'base': 400.00, 'complexidade_min': 1.3, 'complexidade_max': 2.0},
    'OUTRO': {'base': 100.00, 'complexidade_min': 1.0, 'complexidade_max': 1.0},
}
TAXA_COR = 0.35 
TAXA_TAMANHO_GRANDE = 0.50 

def _identificar_servico_base(pergunta: str) -> str:
    # ... (Lógica de identificação de serviço permanece a mesma) ...
    pergunta_upper = pergunta.upper()
    for termo, _ in TABELA_PRECOS_BASE.items():
        if termo in pergunta_upper:
            return termo
    return 'OUTRO' 

def calcular_novo_orcamento(pergunta_cliente: str, detalhes: Dict[str, Any]) -> Dict[str, Any]:
    # ... (Lógica de cálculo permanece a mesma) ...
    servico_base_nome = _identificar_servico_base(pergunta_cliente)
    preco_info = TABELA_PRECOS_BASE.get(servico_base_nome, TABELA_PRECOS_BASE['OUTRO'])
    preco_base = preco_info['base']
    valor_adicional = 0.0
    
    fator_complexidade = detalhes.get('complexidade', 
        random.uniform(preco_info.get('complexidade_min', 1.0), preco_info.get('complexidade_max', 1.0)))
    preco_base *= fator_complexidade

    if detalhes.get('cor', False):
        valor_adicional += preco_base * TAXA_COR
    if detalhes.get('tamanho', '').lower() == 'grande':
        valor_adicional += preco_base * TAXA_TAMANHO_GRANDE
    
    valor_bruto = preco_base + valor_adicional
    
    return {
        'status': 'ORÇAMENTO CALCULADO',
        'data_calculo': obter_data_hora_atual(),
        'servico_base': servico_base_nome,
        'valor_bruto': valor_bruto,
        'valor_final': formatar_moeda(valor_bruto) 
    }

def processar_atendimentos_pendentes() -> List[Dict[str, Any]]:
    """
    Carrega *todos* os atendimentos do BD e processa aqueles com status 'Orçamento Pendente'.
    """
    # NOVO: Carrega todos os objetos Atendimento do BD (não mais DataFrame do CSV)
    atendimentos = carregar_todos_atendimentos() 
    resultados = []
    
    # 1. Filtra os atendimentos pendentes no objeto Python
    pendentes = [
        att for att in atendimentos 
        if att.status_atendimento and att.status_atendimento.strip().lower() == 'orçamento pendente'
    ]
    log_evento(f"Encontrados {len(pendentes)} atendimentos pendentes para processamento no BD.", 'INFO')

    # 2. Itera e processa
    for att in pendentes:
        pergunta = att.pergunta_cliente
        cliente = att.nome_cliente
        
        # Simulação de extração de detalhes:
        detalhes = {
            'cor': 'colorida' in pergunta.lower(), 
            'tamanho': 'grande', 
            'complexidade': 1.5 
        }
        
        orcamento = calcular_novo_orcamento(pergunta, detalhes)
        
        # NOVO: Atualiza o banco de dados com o valor e o status
        id_orcamento = f"OSSO-{att.id}-{random.randint(100,999)}"
        atualizar_orcamento_atendimento(att.id, orcamento['valor_bruto'], id_orcamento)
        
        resultados.append({
            'cliente': cliente,
            'pergunta_original': pergunta,
            **orcamento 
        })

    return resultados

# --- Bloco de Testes ---
if __name__ == '__main__':
    log_evento(f"Iniciando testes do {os.path.basename(__file__)} (BD Refatorado)", 'INFO')
    
    # IMPORTANTE: Este teste exige que o BD já tenha registros com status 'Orçamento Pendente'!
    # Como o seu BD atual SÓ tem um registro como 'Orçamento Calculado', vamos adicionar um novo:
    
    from osso_data import registrar_novo_atendimento
    
    novo_atendimento = registrar_novo_atendimento({
        'nome_cliente': 'Alice',
        'whatsapp': '5521912345678',
        'pergunta_cliente': 'Quanto custa uma tattoo de Fênix colorida, tamanho grande?',
    })
    
    if novo_atendimento:
        log_evento(f"Novo lead de teste (Alice) adicionado com sucesso.", 'INFO')
        
    # Processa os atendimentos pendentes no BD
    resultados_processados = processar_atendimentos_pendentes()

    print("\n--- Resultados do Processamento de Orçamentos Pendentes ---")
    if resultados_processados:
        for res in resultados_processados:
            print("-" * 30)
            print(f"CLIENTE: {res['cliente']}")
            print(f"SERVIÇO: {res['servico_base']}")
            print(f"VALOR CALCULADO: {res['valor_final']}")
    else:
        print("Nenhum atendimento pendente encontrado ou processado.")

    log_evento("Testes do osso_orcamento.py concluídos.", 'INFO')