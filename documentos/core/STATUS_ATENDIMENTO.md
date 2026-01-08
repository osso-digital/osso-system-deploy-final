
# STATUS DE ATENDIMENTO — OSSO IA SYSTEM

Este documento define os **status oficiais** de atendimento utilizados pelo sistema OSSO IA SYSTEM.

⚠️ Estes status são **globais**, **imutáveis** e fazem parte das regras de negócio do sistema.
Nenhum agente (IA ou humano) pode criar status fora deste padrão.

---

## 🎯 Objetivo dos status

- Padronizar o fluxo de atendimento
- Permitir métricas confiáveis
- Evitar decisões automáticas incorretas
- Garantir que a IA **não feche vendas**
- Preparar o sistema para modelo SaaS multinicho

---

## 📌 Lista oficial de status

### 1️⃣ NOVO

**Descrição:**  
Lead recém-captado pelo sistema.

**Quem define:**  
Sistema automaticamente.

**Ações permitidas:**  
- Início do atendimento pelo BONE
- Coleta inicial de informações

**Ações proibidas:**  
- Envio de valores
- Encaminhamento humano imediato

---

### 2️⃣ EM_ATENDIMENTO

**Descrição:**  
O BONE está conduzindo a conversa ativa com o lead.

**Quem define:**  
IA (BONE).

**Ações permitidas:**  
- Fazer perguntas
- Esclarecer dúvidas
- Entender necessidade real

**Ações proibidas:**  
- Pressionar o lead
- Confirmar valores finais
- Agendar serviços

---

### 3️⃣ PRE_ORCAMENTO_ENVIADO

**Descrição:**  
O BONE apresentou um **pré-orçamento orientativo**.

**Quem define:**  
IA (BONE).

**Regra obrigatória:**  
Sempre deixar claro que:
> “Os valores são estimativas orientativas e dependem de validação humana.”

**Ações permitidas:**  
- Explicar critérios de valor
- Preparar o lead para contato humano

**Ações proibidas:**  
- Garantir preço
- Fechar venda
- Confirmar agenda

---

### 4️⃣ AGUARDANDO_HUMANO

**Descrição:**  
O lead está qualificado e pronto para atendimento humano.

**Quem define:**  
IA (BONE).

**Ações permitidas:**  
- Encerrar conversa educadamente
- Registrar informações no sistema

**Ações proibidas:**  
- Continuar negociação
- Alterar valores
- Reabrir conversa automaticamente

---

### 5️⃣ CONVERTIDO

**Descrição:**  
Atendimento concluído com sucesso por humano.

**Quem define:**  
Humano (admin ou operador).

**Ações permitidas:**  
- Registro final
- Métricas de conversão

---

### 6️⃣ NAO_CONVERTIDO

**Descrição:**  
Lead não avançou para fechamento.

**Quem define:**  
Humano ou sistema (timeout).

**Ações permitidas:**  
- Encerrar atendimento
- Usar para métricas

---

## 🚫 Regras absolutas

- Status **nunca pulam etapas**
- IA **não define CONVERTIDO**
- IA **não altera status após AGUARDANDO_HUMANO**
- Todos os atendimentos devem terminar em:
  - CONVERTIDO ou
  - NAO_CONVERTIDO

---

## 🧠 Observação final

Este fluxo é válido para **todos os nichos**  
(tattoo, piercing, clínicas, serviços, etc).

Regras específicas de cada nicho **não alteram** os status, apenas a lógica interna.
