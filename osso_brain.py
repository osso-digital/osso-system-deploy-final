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
    def log_evento(msg, nivel='INFO'):
        print(f"[{nivel}] osso_brain: {msg}")
    def formatar_moeda(valor):
        return f'R$ {valor:.2f}'
    def exportar_para_dataframe():
        log_evento("AVISO: Módulo osso_data não carregado.", 'WARNING')
        return None

def gerar_relatorio_analise_semanal() -> Dict[str, Any]:
    """
    Gera um relatório de análise de dados (Ponto 9).
    Calcula KPIs essenciais para o estúdio.
    """
    log_evento("Iniciando geração de relatório analítico.", 'INFO')
    df = exportar_para_dataframe()

    if df is None or df.empty:
        log_evento("Banco de dados vazio. Não é possível gerar relatórios.", 'WARNING')
        return {'status': 'BD Vazio'}

    try:
        total_atendimentos = len(df)
        
        # Converte a coluna de valores para garantir que os cálculos funcionem
        # Isso é necessário porque valor_calculado foi salvo como Float no BD
        df['valor_calculado'] = pd.to_numeric(df['valor_calculado'], errors='coerce').fillna(0)
        
        # KPIs de Atendimento e Vendas
        total_faturado = df['valor_calculado'].sum()
        orcamentos_calculados = len(df[df['status_atendimento'] == 'Orçamento Calculado'])
        
        # Se for um produto vendável, usamos o conceito de Funil de Vendas:
        # Leads (Todos os registros) -> Orçamentos (Calculado)
        taxa_conversao_orcamento = (orcamentos_calculados / total_atendimentos) * 100 if total_atendimentos > 0 else 0

        # Análise de Status (Ponto 8)
        contagem_status = df['status_atendimento'].value_counts().to_dict()
        
        relatorio = {
            'timestamp': df['timestamp'].max(), # Data do último registro
            'total_atendimentos': total_atendimentos,
            'clientes_unicos': df['nome_cliente'].nunique(),
            'total_faturado_bruto': formatar_moeda(total_faturado),
            'orcamentos_concluidos': orcamentos_calculados,
            'taxa_conversao_orcamento_pct': f"{taxa_conversao_orcamento:.2f}%",
            'distribuicao_status': contagem_status
        }
        
        log_evento("Relatório analítico gerado com sucesso.", 'INFO')
        return relatorio

    except Exception as e:
        log_evento(f"Erro ao gerar relatórios analíticos: {e}", 'ERROR')
        return {'status': 'ERRO', 'detalhe': str(e)}

# --- Bloco de Testes ---
if __name__ == '__main__':
    log_evento(f"Iniciando testes do {os.path.basename(__file__)} (OssoBrain)", 'INFO')
    
    # IMPORTANTE: Este teste exige que o BD já tenha sido inicializado e tenha dados (como os que você acabou de criar!)
    
    relatorio = gerar_relatorio_analise_semanal()

    print("\n" + "="*60)
    print("      RELATÓRIO SEMANAL DO GERENTE DE DADOS (OSSOBRAIN)")
    print("="*60)
    
    if relatorio.get('status') == 'BD Vazio':
        print("Aguardando dados no Banco de Dados para análise...")
    else:
        print(f"Última Atualização: {relatorio.get('timestamp', 'N/A')}")
        print(f"Total de Atendimentos no BD: {relatorio['total_atendimentos']}")
        print(f"Faturamento Bruto (Calculado): {relatorio['total_faturado_bruto']}")
        print("-" * 60)
        print(f"Taxa de Conversão para Orçamento: {relatorio['taxa_conversao_orcamento_pct']}")
        print("\nDistribuição de Status:")
        for status, count in relatorio['distribuicao_status'].items():
            print(f"  - {status}: {count} registro(s)")

    log_evento("Testes do osso_brain.py concluídos.", 'INFO')