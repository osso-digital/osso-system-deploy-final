# -*- coding: utf-8 -*-
# osso_brain.py
# Módulo: OssoBrain (O Gerente/Analista de Dados)
# Responsável por análises de dados, relatórios e geração de insights.

import pandas as pd
import os
from typing import Dict, Any, List

# Importa as ferramentas e o novo módulo de dados baseado em BD
try:
    from osso_tools import log_evento, formatar_moeda
    from osso_data import exportar_para_dataframe # Usamos este para análise Pandas
except ImportError as e:
    # Fallback/Mock para testes isolados
    def log_evento(msg, nivel='INFO'):
        print(f"[{nivel}] osso_brain: {msg}")
    def formatar_moeda(valor):
        return f'R$ {valor:.2f}'
    def exportar_para_dataframe():
        log_evento("AVISO: Módulo osso_data ou Pandas não carregados. Retornando DF vazio.", 'WARNING')
        return pd.DataFrame() # Retorna DataFrame vazio no mock

def gerar_relatorio_analise_semanal() -> Dict[str, Any]:
    """
    Gera um relatório de análise de dados (Ponto 9).
    Calcula KPIs essenciais para o estúdio.
    """
    log_evento("Iniciando geração de relatório analítico.", 'INFO')
    df = exportar_para_dataframe()

    if df.empty:
        log_evento("Banco de dados vazio. Não é possível gerar relatórios.", 'WARNING')
        return {'status': 'BD Vazio', 'total_atendimentos': 0}

    try:
        total_atendimentos = len(df)
        
        # Converte a coluna de valores para garantir que os cálculos funcionem
        df['valor_calculado'] = pd.to_numeric(df['valor_calculado'], errors='coerce').fillna(0)
        
        # Filtra registros com data válida para evitar erros
        df_validos = df[df['timestamp'].notna() & (df['timestamp'] != '')]

        # Faturamento total (soma de todos os orçamentos calculados)
        total_faturado = df['valor_calculado'].sum()
        
        # KPIs de Atendimento
        total_orcamentos = len(df[df['status_atendimento'].isin(['Orçamento Calculado', 'Agendamento Provisório Sugerido'])])
        total_agendamentos = len(df[df['status_atendimento'] == 'Agendamento Provisório Sugerido'])
        
        # Taxas de Conversão
        taxa_orcamento = (total_orcamentos / total_atendimentos) * 100 if total_atendimentos > 0 else 0
        taxa_agendamento = (total_agendamentos / total_atendimentos) * 100 if total_atendimentos > 0 else 0

        # Análise de Status (Ponto 8)
        contagem_status = df['status_atendimento'].value_counts().to_dict()
        
        relatorio = {
            'status': 'SUCESSO',
            'timestamp_max': df_validos['timestamp'].max() if not df_validos.empty else 'N/A', 
            'total_atendimentos': total_atendimentos,
            'clientes_unicos': df['nome_cliente'].nunique(),
            'total_faturado_bruto': formatar_moeda(total_faturado),
            'media_orcamento': formatar_moeda(df['valor_calculado'].mean() if total_atendimentos > 0 else 0),
            'orcamentos_concluidos': total_orcamentos,
            'agendamentos_sugeridos': total_agendamentos,
            'taxa_conversao_orcamento_pct': f"{taxa_orcamento:.2f}%",
            'taxa_conversao_agendamento_pct': f"{taxa_agendamento:.2f}%",
            'distribuicao_status': contagem_status
        }
        
        log_evento("Relatório analítico gerado com sucesso.", 'INFO')
        return relatorio

    except Exception as e:
        log_evento(f"Erro ao gerar relatórios analíticos: {e}", 'ERROR')
        return {'status': 'ERRO', 'detalhe': str(e), 'total_atendimentos': 0}

# --- Bloco de Testes ---
if __name__ == '__main__':
    log_evento(f"Iniciando testes do {os.path.basename(__file__)} (OssoBrain)", 'INFO')
    
    # OBS: O teste só funcionará se houver o osso_data.py e pandas instalados!
    try:
        relatorio = gerar_relatorio_analise_semanal()
    except Exception as e:
        print(f"ERRO DE TESTE (Pandas/BD): {e}")
        relatorio = {'status': 'ERRO', 'detalhe': 'Verifique as dependências (Pandas).'}

    print("\n" + "="*60)
    print("        RELATÓRIO SEMANAL DO GERENTE DE DADOS (OSSOBRAIN)")
    print("="*60)
    
    if relatorio.get('status') == 'BD Vazio':
        print("Aguardando dados no Banco de Dados para análise...")
    elif relatorio.get('status') == 'ERRO':
        print(f"Erro ao gerar relatório: {relatorio['detalhe']}")
    else:
        for key, value in relatorio.items():
            if key not in ['status', 'distribuicao_status']:
                print(f"{key.replace('_', ' ').title():<30}: {value}")
        print("\nDistribuição de Status:")
        for status, count in relatorio['distribuicao_status'].items():
            print(f"  - {status}: {count} registro(s)")

    log_evento("Testes do osso_brain.py concluídos.", 'INFO')