# -*- coding: utf-8 -*-
# osso_orcamento.py
# Versão atualizada com regras do estúdio Bone

from typing import Dict, Any, List
import math

try:
    from osso_tools import log_evento
except Exception:
    def log_evento(msg, nivel='INFO', modulo='osso_orcamento'):
        print(f"[{nivel}] {modulo}: {msg}")

# --- Configurações de preço ---
PRECOS_BASE_CM2 = {
    'Pequena': 10.00,
    'Média': 8.00,
    'Grande': 6.00,
}

ADICIONAIS_COMPLEXIDADE = {
    'Simples': 0.00,
    'Média': 0.20,
    'Alta': 0.50,
}

ADICIONAIS_COR = {
    'Preto e Cinza': 0.00,
    'Colorida': 0.30,
}

ADICIONAIS_LOCAL = {
    'Braço': 0.00,
    'Perna': 0.00,
    'Costas': 0.10,
    'Tórax': 0.15,
    'Mão': 0.20,
    'Pé': 0.20,
    'Pescoço': 0.25,
    'Rosto': 0.25,
    'Barriga': 0.20
}

# Regras do estúdio (suas confirmações)
VALOR_MINIMO_TATTOO_ATE_5CM2 = 150.00
VALOR_MINIMO_SESSAO_3H = 650.00
VALOR_SESSAO_6H = 1200.00

PIERCING_PRECOS = {
    "aco": 50.0,
    "titanio": 90.0
}

VALOR_MINIMO_GERAL = 300.00  # fallback caso queira

def calcular_area(tamanho_cm: float, fator_largura: float = 0.4) -> float:
    area_cm2 = tamanho_cm * (tamanho_cm * fator_largura)
    log_evento(f"Cálculo de Área: {tamanho_cm}cm x {tamanho_cm * fator_largura:.1f}cm = {area_cm2:.2f} cm²", 'DEBUG', 'osso_orcamento')
    return area_cm2

def calcular_novo_orcamento(pergunta_cliente: str, parametros_calculo: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retorna:
      {
        'valor_final': 'R$ x.xxx,xx',
        'servico_base': 'Tatuagem ...' or 'Piercing ...',
        'valor_bruto': float,
        'adicionais_aplicados': [...]
      }
    """
    try:
        tipo_servico = parametros_calculo.get('servico', 'Tatuagem')  # 'Tatuagem' ou 'Piercing'
        tamanho_cm = float(parametros_calculo.get('tamanho_cm', parametros_calculo.get('tamanho', 12)))
        cor_ou_preto = parametros_calculo.get('cor_ou_preto', parametros_calculo.get('cor', 'Preto e Cinza'))
        complexidade = parametros_calculo.get('complexidade', 'Média')
        local_corpo = parametros_calculo.get('local_corpo', parametros_calculo.get('local', 'Braço'))
        sessao_opcao = parametros_calculo.get('sessao', parametros_calculo.get('opcao_sessao', 'Sessão única'))  # 'Sessão única', '3h', '6h', etc.
        adicionais_aplicados: List[str] = []

        # === Piercing branch ===
        if tipo_servico.lower().startswith('pierc'):
            metal = parametros_calculo.get('metal', 'aco').lower()
            preco_base = PIERCING_PRECOS.get(metal, PIERCING_PRECOS['aco'])
            adicionais_aplicados.append(f"Material: {metal.capitalize()}")
            valor_final = preco_base
            valor_final_formatado = f"R$ {valor_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            log_evento(f"Orçamento Piercing: {valor_final_formatado}", 'INFO', 'osso_orcamento')
            return {
                'valor_final': valor_final_formatado,
                'servico_base': f"Piercing ({metal})",
                'valor_bruto': valor_final,
                'adicionais_aplicados': adicionais_aplicados
            }

        # === Tattoo branch ===
        # determina faixa de tamanho
        if tamanho_cm > 20:
            faixa_tamanho = 'Grande'
        elif tamanho_cm > 10:
            faixa_tamanho = 'Média'
        else:
            faixa_tamanho = 'Pequena'

        preco_base_cm2 = PRECOS_BASE_CM2.get(faixa_tamanho, PRECOS_BASE_CM2['Média'])
        area_cm2 = calcular_area(tamanho_cm)
        preco_base_bruto = area_cm2 * preco_base_cm2
        log_evento(f"Base: R$ {preco_base_bruto:.2f} (Área {area_cm2:.2f} x Preço/cm² {preco_base_cm2:.2f})", 'DEBUG', 'osso_orcamento')

        # adicionais porcentuais
        adicional_comp_pct = ADICIONAIS_COMPLEXIDADE.get(complexidade, 0.00)
        adicional_cor_pct = ADICIONAIS_COR.get(cor_ou_preto, 0.00)

        local_key = local_corpo.split('/')[0].strip().split(' ')[0]
        adicional_local_pct = ADICIONAIS_LOCAL.get(local_key, 0.00)

        if adicional_comp_pct > 0:
            adicionais_aplicados.append(f"Complexidade {complexidade} (+{int(adicional_comp_pct*100)}%)")
        if adicional_cor_pct > 0:
            adicionais_aplicados.append(f"Tinta {cor_ou_preto} (+{int(adicional_cor_pct*100)}%)")
        if adicional_local_pct > 0:
            adicionais_aplicados.append(f"Local: {local_corpo} (+{int(adicional_local_pct*100)}%)")

        adicional_total_percentual = adicional_comp_pct + adicional_cor_pct + adicional_local_pct
        valor_com_adicionais = preco_base_bruto * (1 + adicional_total_percentual)

        # aplica regras de sessão
        if str(sessao_opcao).lower().startswith('6'):
            # sessão 6h fixa
            valor_final = VALOR_SESSAO_6H
            adicionais_aplicados.append("Sessão 6h (valor fixo)")
        elif str(sessao_opcao).lower().startswith('3'):
            # ao menos o mínimo de 3h
            valor_final = max(valor_com_adicionais, VALOR_MINIMO_SESSAO_3H)
            adicionais_aplicados.append("Sessão 3h (mínimo aplicado se necessário)")
        else:
            # sessão única: aplica mínimo por área
            if area_cm2 <= 5.0:
                # especial: se área pequena, preço mínimo R$150
                valor_final = max(valor_com_adicionais, VALOR_MINIMO_TATTOO_ATE_5CM2)
                if valor_final == VALOR_MINIMO_TATTOO_ATE_5CM2:
                    adicionais_aplicados.append(f"Valor mínimo aplicado para <=5cm² (R$ {VALOR_MINIMO_TATTOO_ATE_5CM2:.2f})")
            else:
                valor_final = max(valor_com_adicionais, VALOR_MINIMO_GERAL)

        # Caso valor_final ainda muito baixo, aplica fallback
        if valor_final < 1.0:
            valor_final = VALOR_MINIMO_GERAL

        # formatar
        valor_final_formatado = f"R$ {valor_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        log_evento(f"Estimativa final: {valor_final_formatado}", 'INFO', 'osso_orcamento')
        return {
            'valor_final': valor_final_formatado,
            'servico_base': f"Tatuagem {faixa_tamanho} ({tamanho_cm:.1f}cm)",
            'valor_bruto': float(valor_final),
            'adicionais_aplicados': adicionais_aplicados
        }

    except Exception as e:
        log_evento(f"Erro no cálculo do orçamento: {e}", 'ERROR', 'osso_orcamento')
        return {
            'valor_final': 'R$ 0,00',
            'servico_base': 'ERRO DE CÁLCULO',
            'valor_bruto': 0.0,
            'adicionais_aplicados': ["Erro ao processar dados de entrada."]
        }
