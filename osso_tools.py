# osso_tools.py

import datetime
import json
import logging
import os
# Usamos Decimal para garantir precisão monetária
from decimal import Decimal, ROUND_HALF_UP 

# -----------------------------------------------------
# 1. CONFIGURAÇÃO DE LOGGING
# -----------------------------------------------------
# Configura o formato de saída do log
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

# -----------------------------------------------------
# 2. FUNÇÕES UTILITY
# -----------------------------------------------------

def log_evento(mensagem: str, nivel: str = 'INFO'):
    """Registra uma mensagem no log com o nível especificado."""
    nivel = nivel.upper()
    if nivel == 'DEBUG':
        logging.debug(mensagem)
    elif nivel == 'INFO':
        logging.info(mensagem)
    elif nivel == 'WARNING':
        logging.warning(mensagem)
    elif nivel == 'ERROR':
        logging.error(mensagem)
    elif nivel == 'CRITICAL':
        logging.critical(mensagem)
    else:
        logging.info(f"[NÍVEL INVÁLIDO] {mensagem}") 

def formatar_moeda(valor: float | Decimal, simbolo: str = 'R$', casas_decimais: int = 2) -> str:
    """
    Formata um valor numérico como uma string de moeda no formato brasileiro (BRL).
    Esta é a versão robusta que não depende da configuração de locale do seu SO.
    """
    try:
        # 1. Garante precisão e arredondamento (ex: 12345.678 -> 12345.68)
        precisao = Decimal(f'0.{"0" * casas_decimais}')
        valor_decimal = Decimal(valor).quantize(precisao, rounding=ROUND_HALF_UP)

        # 2. Converte para string e lida com o sinal (se houver)
        valor_str = str(valor_decimal)
        sinal = ''
        if valor_str.startswith('-'):
            sinal = '-'
            valor_str = valor_str[1:]

        # 3. Separa a parte inteira e a decimal
        if '.' in valor_str:
            inteira, decimal = valor_str.split('.')
        else:
            inteira, decimal = valor_str, '0' * casas_decimais

        # Garante a quantidade correta de casas decimais
        decimal = decimal.ljust(casas_decimais, '0')[:casas_decimais]

        # 4. Adiciona o separador de milhar '.' (logica brasileira)
        inteiro_formatado = ''
        for i, digito in enumerate(reversed(inteira)):
            if i > 0 and i % 3 == 0:
                inteiro_formatado += '.'
            inteiro_formatado += digito
            
        inteiro_formatado = sinal + inteiro_formatado[::-1]

        # 5. Monta o resultado final (ex: R$ 12.345,68)
        if casas_decimais > 0:
            return f"{simbolo} {inteiro_formatado},{decimal}"
        else:
            return f"{simbolo} {inteiro_formatado}"

    except Exception as e:
        log_evento(f"Erro ao formatar valor para moeda: {valor}. Erro: {e}", 'ERROR')
        return f"ERRO_FORMATO({valor})"


def obter_data_hora_atual(formato: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Retorna a data e hora atual formatada."""
    return datetime.datetime.now().strftime(formato)

def carregar_json(caminho_arquivo: str) -> dict | None:
    """Carrega dados de um arquivo JSON (usado para o service_account.json)."""
    if not os.path.exists(caminho_arquivo):
        log_evento(f"Arquivo JSON não encontrado: {caminho_arquivo}", 'ERROR')
        return None
    
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        return dados
    except json.JSONDecodeError as e:
        log_evento(f"Erro de decodificação JSON no arquivo {caminho_arquivo}: {e}", 'CRITICAL')
        return None
    except Exception as e:
        log_evento(f"Erro ao carregar o arquivo JSON {caminho_arquivo}: {e}", 'ERROR')
        return None


# -----------------------------------------------------
# 3. BLOCO DE TESTES 
# -----------------------------------------------------
# Este bloco SÓ é executado quando você roda: python osso_tools.py
# Ele testa todas as funções e deve funcionar 100% agora.

if __name__ == '__main__':
    log_evento("Iniciando testes do osso_tools.py (Versão Garantida)", 'INFO')

    # Teste de formatação de moeda
    valor1 = 12345.678
    valor2 = 99.99
    valor3 = 0.5
    valor4 = 1000
    valor5 = -234567.89
    valor6 = 123456789.9

    print("\n--- Teste formatar_moeda ---")
    print(f"Valor {valor1} formatado: {formatar_moeda(valor1)}")
    print(f"Valor {valor2} formatado: {formatar_moeda(valor2, simbolo='U$')}")
    print(f"Valor {valor3} com 3 casas: {formatar_moeda(valor3, casas_decimais=3)}")
    print(f"Valor {valor4} sem casas decimais: {formatar_moeda(valor4, casas_decimais=0)}")
    print(f"Valor {valor5} negativo: {formatar_moeda(valor5)}")
    print(f"Valor {valor6} valor alto: {formatar_moeda(valor6)}")
    
    # Teste de data/hora
    print("\n--- Teste obter_data_hora_atual ---")
    print(f"Data e Hora Atual (Padrão): {obter_data_hora_atual()}")
    print(f"Data e Hora Atual (Curto): {obter_data_hora_atual('%d/%m/%Y %H:%M')}")

    # Teste de log (Verifique a saída no console)
    print("\n--- Teste log_evento (Verifique o console) ---")
    log_evento("Esta é uma mensagem de informação.", 'INFO')
    
    # Teste carregar_json 
    print("\n--- Teste carregar_json ---")
    SA_FILE = 'service_account.json'
    if os.path.exists(SA_FILE):
        config = carregar_json(SA_FILE)
        if config:
            print(f"Chaves do arquivo '{SA_FILE}' carregadas: {list(config.keys())}")
        else:
            log_evento(f"Falha ao carregar o arquivo '{SA_FILE}'.", 'ERROR')
    else:
        log_evento(f"Arquivo '{SA_FILE}' não encontrado para o teste.", 'WARNING')

    log_evento("Testes do osso_tools.py concluídos.", 'INFO')