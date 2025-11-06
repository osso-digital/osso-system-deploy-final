# osso_midia.py
# Módulo: OssoMídia (Agente de Marketing e Conteúdo)
# Gerencia a geração de legendas de alto impacto usando IA.

import os
from typing import List, Dict, Any

# NOTE: No produto final, você usaria o módulo 'openai' ou 'google-genai' aqui.
# from openai import OpenAI 
# client = OpenAI(api_key=SEU_TOKEN)

try:
    from osso_tools import log_evento
    from osso_data import exportar_para_dataframe # Para puxar dados de popularidade
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
        return {'status': 'BD Vazio', 'sugestao': 'Capture mais leads!'}

    try:
        # 1. Identifica o tipo de serviço mais orçado
        contagem_servicos = df['status_atendimento'].value_counts()
        
        # Simula a identificação de um estilo popular baseado no BD
        estilo_mais_popular = "FÊNIX" # Exemplo, no futuro viria de uma análise mais profunda do OssoBrain
        
        sugestao_marketing = (
            f"Seu estilo mais popular é **{estilo_mais_popular}**. "
            f"Foque o marketing de hoje em legendas sobre 'Renovação' e 'Força'. "
            f"Você tem {contagem_servicos.get('Orçamento Calculado', 0)} orçamentos prontos para fechar!"
        )
        
        return {'status': 'Pronto', 'sugestao': sugestao_marketing, 'estilo_foco': estilo_mais_popular}

    except Exception as e:
        log_evento(f"Erro ao gerar insights de marketing: {e}", 'ERROR')
        return {'status': 'ERRO', 'sugestao': 'Erro de processamento.'}

# --- Bloco de Testes ---
if __name__ == '__main__':
    log_evento(f"Iniciando testes do {os.path.basename(__file__)} (OssoMídia)", 'INFO')
    
    # 1. Sugestão de Pauta (OssoLead/OssoBrain)
    insights = obter_insights_de_marketing()
    print("\n--- Teste 1: Sugestão de Pauta ---")
    print(f"Sugestão: {insights['sugestao']}")
    
    # 2. Geração de Legenda (OssoMídia)
    print("\n--- Teste 2: Geração de Legendas com IA ---")
    
    # Legenda 1: Usando o foco sugerido
    legenda1 = gerar_legenda_inteligente(insights.get('estilo_foco', 'Leão'), "costas", cor=True)
    print(">> Legenda FÊNIX:", legenda1)
    
    # Legenda 2: Outro estilo
    legenda2 = gerar_legenda_inteligente("Leão", "coxa", cor=False)
    print(">> Legenda LEÃO:", legenda2)
    
    log_evento("Testes do osso_midia.py concluídos.", 'INFO')