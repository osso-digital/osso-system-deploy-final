# osso_templates.py
# Módulo: Gerenciamento de Templates e Nichos (Substitui parte do osso_config)

from typing import Dict, Any

# --- 1. CONFIGURAÇÃO DE NICHOS (O Valor de Venda) ---

# Define as regras únicas para cada tipo de cliente do seu SaaS
NICHOS = {
    "TATTOO_ESTUDIO": {
        "NOME_CLIENTE": "Estúdio Tattoo Até os Ossos",
        "MOEDA": "R$",
        "UNIDADE_TEMPO": "horas de sessão",
        "MENSAGENS": {
            "SAUDACAO": "Olá {nome}! Seu pedido de orçamento foi analisado.",
            "AGENDAMENTO_SUCESSO": "\n\nSeu horário foi reservado provisoriamente para {data} às {hora}h!"
        },
        "REGRAS_ORCAMENTO": {
            # Regras base para o Agente OssoPreço
            "TIPO_SERVICO": {
                'FÊNIX': {'base': 800.00, 'complexidade_min': 1.2, 'complexidade_max': 1.8},
                'FLORAL': {'base': 250.00, 'complexidade_min': 1.0, 'complexidade_max': 1.5},
                'OUTRO': {'base': 100.00, 'complexidade_min': 1.0, 'complexidade_max': 1.0},
            },
            "TAXAS": {
                "TAXA_COR_PADRAO": 0.35,  
                "TAXA_TAMANHO_GRANDE": 0.50,
            }
        }
    },
    
    "ESTETICA_AVANCADA": {
        "NOME_CLIENTE": "Clínica Saúde & Laser",
        "MOEDA": "R$",
        "UNIDADE_TEMPO": "sessões",
        "MENSAGENS": {
            "SAUDACAO": "Olá {nome}! Analisamos seu procedimento.",
            "AGENDAMENTO_SUCESSO": "\n\nSua consulta foi agendada para {data}."
        },
        "REGRAS_ORCAMENTO": {
            "TIPO_SERVICO": {
                'PREENCHIMENTO': {'base': 1500.00, 'complexidade_min': 1.0, 'complexidade_max': 1.5},
                'LASER': {'base': 400.00, 'complexidade_min': 1.1, 'complexidade_max': 1.6},
                'OUTRO': {'base': 200.00, 'complexidade_min': 1.0, 'complexidade_max': 1.0},
            },
            "TAXAS": {
                "TAXA_AREA_ESPECIAL": 0.40,  # Novo tipo de taxa
                "TAXA_REPETICAO": 0.10,      # Taxa por repetição
            }
        }
    }
    # Outros nichos (Mecânica, Design) viriam aqui...
}


def obter_template_nicho(nome_nicho: str) -> Dict[str, Any] | None:
    """
    Função principal que o osso_api.py chamará para carregar as configurações do nicho.
    """
    return NICHOS.get(nome_nicho.upper())


# --- Bloco de Testes ---
if __name__ == '__main__':
    from osso_tools import log_evento
    log_evento("Iniciando testes do Módulo de Templates.", 'INFO')
    
    # 1. Carrega o template de tatuagem
    template_tattoo = obter_template_nicho("TATTOO_ESTUDIO")
    print("\n--- TESTE TATUAGEM ---")
    print("Nome do Nicho:", template_tattoo['NOME_CLIENTE'])
    print("Preço Fênix:", template_tattoo['REGRAS_ORCAMENTO']['TIPO_SERVICO']['FÊNIX']['base'])
    
    # 2. Carrega o template de estética
    template_estetica = obter_template_nicho("ESTETICA_AVANCADA")
    print("\n--- TESTE ESTÉTICA ---")
    print("Mensagem:", template_estetica['MENSAGENS']['SAUDACAO'])
    print("Taxa:", template_estetica['REGRAS_ORCAMENTO']['TAXAS']['TAXA_AREA_ESPECIAL'])