# 🚀 OSSO IA SYSTEM - Sistema de Gestão de Leads e Orçamentos

Este é o core da automação para estúdios de tatuagem, responsável pela captação de leads via WhatsApp/Site, cálculo de orçamentos e persistência de dados em um Banco de Dados (BD) central.

---

## 1. ⚙️ ARQUITETURA E TECNOLOGIA

O sistema é construído em módulos com arquitetura **orientada a objetos (POO)** e utiliza as seguintes tecnologias:

* **Linguagem Principal:** Python 3.10+
* **Servidor Web (API):** Flask
* **Banco de Dados (BD):** SQLite (Utilizando SQLAlchemy como ORM)
* **Dependências:** Todas listadas no `requirements.txt`.

### 🗂️ Estrutura do Projeto

| Arquivo | Função |
| :--- | :--- |
| `osso_api.py` | Ponto de entrada (Endpoint) para o Webhook do WhatsApp/Site. |
| `osso_orcamento.py` | Contém a lógica de negócio para calcular o orçamento da tatuagem. |
| `osso_data.py` | O "Arquivista". Responsável por salvar e ler dados no BD. |
| `osso_models.py` | Define as tabelas do BD (Clientes, Atendimentos, etc.). |
| `requirements.txt`| Lista todas as bibliotecas Python que precisam ser instaladas. |
| `osso_database.db`| O arquivo do Banco de Dados SQLite. |

---

## 2. 🛠️ INSTRUÇÕES DE INSTALAÇÃO E EXECUÇÃO

O projeto deve ser configurado em um ambiente virtual isolado.

### 2.1. Configuração Inicial

1.  **Crie e Ative o Ambiente Virtual:**
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate
    ```
    *(O terminal deve mostrar `(venv)`)*

2.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

### 2.2. Inicialização do Servidor

1.  **Garantir a Inicialização do BD:**
    Execute o `main.py` uma vez para confirmar que as tabelas do BD estão criadas.
    ```bash
    python main.py
    ```

2.  **Iniciar a API de Webhook (Servidor Flask):**
    Mantenha este terminal rodando 24/7.
    ```bash
    python osso_api.py
    ```

---

## 3. 🧪 TESTE DE VALIDAÇÃO

Para testar se a API e o BD estão funcionando localmente, utilize o `teste_api.py` em um **segundo terminal** (Terminal 2).

* Terminal 2: `python teste_api.py`

Se o Terminal 1 (Flask) mostrar `Novo atendimento registrado...`, o sistema está validado.

---