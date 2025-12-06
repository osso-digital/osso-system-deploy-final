# -*- coding: utf-8 -*-
# osso_midia.py
# Módulo: OssoMídia (Agente de Marketing e Conteúdo)
# Gerencia a geração de legendas de alto impacto usando IA.

import os
from typing import List, Dict, Any

# NOTE: No produto final, você usaria o módulo 'openai' ou 'google-genai' aqui.
# from openai import OpenAI 
# client = OpenAI(api_key=SEU_TOKEN)

# Importa as ferramentas necessárias
try:
    from osso_tools import log_evento
    # Importa a função de exportação atualizada do osso_data.py
    from osso_data import exportar_para_dataframe 
except ImportError:
    def log_evento(msg, nivel='INFO'): print(f"[{nivel}] osso_midia: {msg}")
    def exportar_para_dataframe(): return None

# --- FUNÇÕES DE SIMULAÇÃO DE IA ---

def _simular_resposta_ia(prompt: str) -> str:
    """ Simula a chamada à API do OpenAI/Gemini com uma resposta fixa. """
    log_evento("Simulando chamada à API de IA...", 'DEBUG')
    if "fênix colorida" in prompt.lower():
        return (
            "Transforme sua pele em arte com a Fênix Colorida! 🔥 A representação perfeita "
            "da renovação. Perfeita para quem busca um novo começo. #TattooFênix #Renascer #CorNaPele"
        )
    if "leão" in prompt.lower():
        return (
            "Rei da Selva e da sua pele. 👑 Tatuagem de Leão na coxa: força e liderança no seu corpo. "
            "Marque seu amigo líder! #TattooLeao #ForcaFeminina #Lideranca"
        )
    return "Crie uma legenda simples e direta sobre tatuagens personalizadas. #TattooPersonalizada"

def gerar_legenda_inteligente(estilo_tattoo: str, local_corpo: str, cor: bool = False) -> str:
    """
    Gera uma legenda de alto impacto para posts em redes sociais usando IA.
    (Ponto 10: Marketing Automatizado)
    """
    
    prompt = (
        f"Gere uma legenda de Instagram para um estúdio de tatuagem. "
        f"O estilo é: {estilo_tattoo}. "
        f"O local do corpo é: {local_corpo}. "
        f"A cor é: {'Colorida' if cor else 'Preto e Branco'}."
    )
    
    log_evento(f"Prompt de IA gerado: {estilo_tattoo} / {local_corpo}", 'INFO')
    
    # OBS: No código real, chamaríamos a API aqui
    # response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
    
    return _simular_resposta_ia(f"{estilo_tattoo} {local_corpo} {'colorida' if cor else ''}")


def obter_insights_de_marketing() -> Dict[str, Any]:
    """
    Analisa os dados de vendas e sugere o tipo de conteúdo mais popular (Ponto 6).
    """
    df = exportar_para_dataframe()
    if df is None or df.empty:
        return {'status': 'BD Vazio', 'sugestao': 'Capture mais leads! O banco de dados de atendimentos está vazio.', 'estilo_foco': 'Personalizada'}

    try:
        # 1. Identifica o status mais relevante (indicando interesse em orçamento)
        contagem_status = df['status_atendimento'].value_counts()
        
        # Simula a identificação de um estilo popular baseado em 'pergunta_cliente' ou 'id_orcamento'
        # Em uma análise real, usaria-se NLP na 'pergunta_cliente'. Aqui, faremos uma simulação.
        estilos_simulados = ['FÊNIX', 'Leão', 'Floral', 'Geométrico']
        # Simula o estilo mais popular sendo o primeiro da lista, se houver dados
        estilo_mais_popular = estilos_simulados[len(df) % len(estilos_simulados)] 

        sugestao_marketing = (
            f"Seu estilo com maior demanda recente é **{estilo_mais_popular}** (Baseado em {len(df)} leads). "
            f"Foque o marketing de hoje em posts sobre '{estilo_mais_popular.upper()}'. "
            f"Você tem {contagem_status.get('Orçamento Calculado', 0)} orçamentos calculados, prontos para fechar!"
        )
        
        return {'status': 'Pronto', 'sugestao': sugestao_marketing, 'estilo_foco': estilo_mais_popular}

    except Exception as e:
        log_evento(f"Erro ao gerar insights de marketing: {e}", 'ERROR')
        return {'status': 'ERRO', 'sugestao': 'Erro de processamento na análise de dados.', 'estilo_foco': 'Personalizada'}

# --- Bloco de Testes ---
if __name__ == '__main__':
    log_evento(f"Iniciando testes do {os.path.basename(__file__)} (OssoMídia)", 'INFO')
    
    # Certifica que o BD está pronto para o teste
    try:
        from osso_data import inicializar_banco_dados
        inicializar_banco_dados()
    except ImportError:
        pass # Ignora se OssoData não estiver pronto
        
    # 1. Sugestão de Pauta (OssoLead/OssoBrain)
    insights = obter_insights_de_marketing()
    print("\n--- Teste 1: Sugestão de Pauta ---")
    print(f"Sugestão: {insights['sugestao']}")
    
    # 2. Geração de Legenda (OssoMídia)
    print("\n--- Teste 2: Geração de Legendas com IA ---")
    
    # Legenda 1: Usando o foco sugerido
    estilo = insights.get('estilo_foco', 'Leão')
    legenda1 = gerar_legenda_inteligente(estilo, "costas", cor=True)
    print(f">> Legenda {estilo.upper()}: {legenda1}")
    
    # Legenda 2: Outro estilo
    legenda2 = gerar_legenda_inteligente("Leão", "coxa", cor=False)
    print(">> Legenda LEÃO:", legenda2)
    
    log_evento("Testes do osso_midia.py concluídos.", 'INFO')