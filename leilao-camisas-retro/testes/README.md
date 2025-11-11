# Arquivos de Teste JSON

Esta pasta contém arquivos JSON com eventos de teste para as funções Lambda.

## Arquivos de Sucesso

- `evento_criar_lance_01.json` - Lance para camisa Vasco 1997 (R$ 250,00) - João Silva
- `evento_criar_lance_02.json` - Lance para camisa Vasco 1997 (R$ 350,00) - Maria Santos
- `evento_criar_lance_03.json` - Lance para camisa Corinthians 1990 (R$ 400,00) - Pedro Costa
- `evento_criar_lance_04.json` - Lance para camisa Santos 1980 (R$ 500,00) - Ana Oliveira
- `evento_criar_lance_05.json` - Lance para camisa Vasco 1997 (R$ 600,00) - Bruno Bui

## Arquivos de Erro (Validação)

- `evento_criar_lance_erro_01.json` - Falta o campo `valor_do_lance`
- `evento_criar_lance_erro_02.json` - Valor do lance negativo
- `evento_criar_lance_erro_03.json` - Valor do lance inválido (string)

## Arquivo de Processamento

- `evento_processar_lance.json` - Evento vazio para processar lances da fila SQS

## Como Usar

Execute o script de teste principal:

```bash
python testar_sistema.py
```

Ou use os arquivos JSON diretamente nos seus testes:

```python
import json
from criar_lance import lambda_handler

with open('testes/evento_criar_lance_01.json', 'r') as f:
    evento = json.load(f)
    resposta = lambda_handler(evento)
    print(resposta)
```

