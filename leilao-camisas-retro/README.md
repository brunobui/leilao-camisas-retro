# 🏆 Leilão de Camisas Retrô - Simulação Serverless AWS

Projeto Python que simula uma arquitetura serverless da AWS para um sistema de leilão online de camisas de times retrô.

## 📋 Arquitetura Simulada

```
Usuário → API Gateway → Lambda (CriarLance) → SQS (Lances Pendentes) 
→ Lambda (ProcessarLance) → DynamoDB → SNS (Notificações)
```

## 🗂️ Estrutura do Projeto

```
leilao-camisas-retro/
 ├── criar_lance.py         # Lambda que cria lances e envia para SQS
 ├── processar_lance.py     # Lambda que processa lances e envia notificações
 ├── testar_sistema.py      # Script de teste completo do sistema
 ├── testes/                # Pasta com arquivos JSON de teste
 │   ├── evento_criar_lance_*.json      # Eventos de sucesso
 │   ├── evento_criar_lance_erro_*.json # Eventos de erro
 │   └── evento_processar_lance.json    # Evento de processamento
 └── README.md              # Este arquivo
```

## 🚀 Como Usar

### Executar criar_lance.py

Simula a criação de lances através do API Gateway:

```bash
python criar_lance.py
```

### Executar processar_lance.py

Simula o processamento dos lances da fila SQS:

```bash
python processar_lance.py
```

## 🔧 Serviços AWS Simulados

- **SQS (Lances Pendentes)**: Lista Python `fila_lances`
- **DynamoDB (Banco de Lances)**: Lista Python `banco_lances`
- **SNS (Notificações)**: Lista Python `notificacoes`

## 📝 Funcionalidades

### criar_lance.py
- Recebe requisições simulando API Gateway
- Valida dados do lance (camisa_id, nome_usuario, valor_do_lance)
- Cria lance com ID único (UUID)
- Envia para fila SQS simulada
- Retorna resposta JSON com statusCode 200

### processar_lance.py
- Lê lances da fila SQS simulada
- Salva no DynamoDB simulado
- Atualiza status para "processado"
- Verifica maior lance por camisa
- Envia notificações SNS simuladas

## 🎯 Exemplo de Uso Programático

```python
from criar_lance import lambda_handler as criar_lance
from processar_lance import lambda_handler as processar_lance

# Criar um lance
evento = {
    'body': {
        'camisa_id': 'CAMISA-VASCO-1997',
        'nome_usuario': 'João Silva',
        'valor_do_lance': 250.00
    }
}

resposta = criar_lance(evento)
print(resposta)

# Processar lances
resposta = processar_lance({})
print(resposta)
```

## 📦 Requisitos

- Python 3.6+
- Apenas bibliotecas padrão do Python (sem dependências externas)

## 🧪 Testes

### Teste Automatizado Completo

Execute o script de teste que valida todo o sistema:

```bash
python testar_sistema.py
```

Este script executa 4 tipos de testes:
1. **Criar Lances (Sucesso)** - Testa criação de lances válidos
2. **Criar Lances (Erros)** - Testa validação de erros
3. **Processar Lances** - Testa o fluxo SQS → DynamoDB → SNS
4. **Fluxo Completo** - Teste end-to-end completo

### Testes Individuais

Ambos os arquivos incluem blocos de teste local que podem ser executados diretamente:

```bash
python criar_lance.py
python processar_lance.py
```

### Arquivos JSON de Teste

A pasta `testes/` contém arquivos JSON com eventos de exemplo:

- **Sucesso**: `evento_criar_lance_01.json` até `05.json`
- **Erro**: `evento_criar_lance_erro_01.json` até `03.json`
- **Processamento**: `evento_processar_lance.json`

Você pode usar esses arquivos nos seus próprios testes ou modificar conforme necessário.

