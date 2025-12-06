# -*- coding: utf-8 -*-
# osso_tools.py
# Módulo: Funções de Apoio e Log

import datetime
import os

def log_evento(mensagem: str, nivel: str = 'INFO', modulo: str = 'Geral'):
    """
    Função simples de logging para rastrear o fluxo do agente.
    """
    # Define cores para melhor visualização no terminal (se compatível)
    CORES = {
        'DEBUG': '\033[94m',    # Azul
        'INFO': '\033[92m',     # Verde
        'WARNING': '\033[93m',  # Amarelo
        'ERROR': '\033[91m',    # Vermelho
        'CRITICAL': '\033[95m', # Magenta
        'ENDC': '\033[0m'       # Reset de cor
    }
    
    cor = CORES.get(nivel, CORES['INFO'])
    reset = CORES['ENDC']
    
    # Formato: [NIVEL] modulo: Mensagem
    print(f"{cor}[{nivel}] {modulo}: {mensagem}{reset}")

def calcular_proximo_dia_util() -> datetime.date:
    """
    Calcula o próximo dia útil (excluindo sábados e domingos) a partir da data de hoje.
    """
    hoje = datetime.date.today()
    proximo_dia = hoje + datetime.timedelta(days=1)
    
    # Enquanto o dia não for útil (segunda=0 a sexta=4)
    while proximo_dia.weekday() > 4: # 5 é Sábado, 6 é Domingo
        proximo_dia += datetime.timedelta(days=1)
        
    return proximo_dia

if __name__ == '__main__':
    log_evento("Teste de log INFO")
    log_evento("Teste de log DEBUG", 'DEBUG')
    log_evento("Teste de log ERRO", 'ERROR')
    
    proximo_dia = calcular_proximo_dia_util()
    print(f"Próximo dia útil é: {proximo_dia.strftime('%d/%m/%Y')}")