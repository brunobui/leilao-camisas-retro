"""
Lambda Function: CriarLance
Simula o comportamento de uma Lambda que recebe requisições do API Gateway
e envia lances para a fila SQS (simulada como lista Python).
"""

from uuid import uuid4
from datetime import datetime
import json

# Simulação do serviço SQS (Simple Queue Service)
# Na AWS real, isso seria uma fila SQS real
fila_lances = []


def lambda_handler(event, context=None):
    """
    Handler principal da Lambda no formato AWS.
    
    Args:
        event: Dicionário contendo os dados da requisição (simulando API Gateway)
        context: Contexto da execução Lambda (opcional para simulação local)
    
    Returns:
        dict: Resposta no formato JSON com statusCode e body
    """
    print("\n" + "="*60)
    print(">>> LAMBDA: CriarLance - Iniciando processamento")
    print("="*60)
    
    try:
        # Simula a extração do body da requisição do API Gateway
        # Em produção, o API Gateway passa o body como string JSON
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)
        
        # Extrai os dados do lance
        camisa_id = body.get('camisa_id')
        nome_usuario = body.get('nome_usuario')
        valor_do_lance = body.get('valor_do_lance')
        
        # Validação dos dados obrigatórios
        if not all([camisa_id, nome_usuario, valor_do_lance]):
            print("[ERRO] Dados incompletos na requisição")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'mensagem': 'Erro: camisa_id, nome_usuario e valor_do_lance são obrigatórios'
                })
            }
        
        # Validação do valor do lance
        try:
            valor_do_lance = float(valor_do_lance)
            if valor_do_lance <= 0:
                raise ValueError("Valor deve ser positivo")
        except (ValueError, TypeError):
            print("[ERRO] Valor do lance inválido")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'mensagem': 'Erro: valor_do_lance deve ser um número positivo'
                })
            }
        
        # Cria o objeto lance com ID único
        lance = {
            'lance_id': str(uuid4()),
            'camisa_id': camisa_id,
            'nome_usuario': nome_usuario,
            'valor_do_lance': valor_do_lance,
            'status': 'pendente',
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n[LANCE CRIADO]")
        print(f"   ID: {lance['lance_id']}")
        print(f"   Camisa: {lance['camisa_id']}")
        print(f"   Usuario: {lance['nome_usuario']}")
        print(f"   Valor: R$ {lance['valor_do_lance']:.2f}")
        print(f"   Status: {lance['status']}")
        
        # Simula o envio para a fila SQS
        # Na AWS real, isso seria: sqs.send_message(QueueUrl=..., MessageBody=...)
        fila_lances.append(lance)
        
        print(f"\n[OK] Lance enviado para a fila SQS (Lances Pendentes)")
        print(f"   Total de lances na fila: {len(fila_lances)}")
        print("="*60 + "\n")
        
        # Retorna resposta de sucesso no formato API Gateway
        return {
            'statusCode': 200,
            'body': json.dumps({
                'mensagem': 'Lance criado com sucesso',
                'lance_id': lance['lance_id'],
                'status': 'pendente'
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        print(f"\n[ERRO] Erro inesperado: {str(e)}")
        print("="*60 + "\n")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'mensagem': f'Erro interno: {str(e)}'
            })
        }


# Bloco de teste para execução local
if __name__ == "__main__":
    print("\n" + "[MODO DE TESTE LOCAL] - CriarLance")
    print("="*60)
    
    # Simula diferentes requisições do API Gateway
    testes = [
        {
            'body': {
                'camisa_id': 'CAMISA-001',
                'nome_usuario': 'João Silva',
                'valor_do_lance': 150.00
            }
        },
        {
            'body': {
                'camisa_id': 'CAMISA-001',
                'nome_usuario': 'Maria Santos',
                'valor_do_lance': 200.00
            }
        },
        {
            'body': {
                'camisa_id': 'CAMISA-002',
                'nome_usuario': 'Pedro Costa',
                'valor_do_lance': 300.00
            }
        }
    ]
    
    # Executa os testes
    for i, evento in enumerate(testes, 1):
        print(f"\n--- Teste {i} ---")
        resposta = lambda_handler(evento)
        print(f"\n[RESPOSTA DA LAMBDA]")
        print(json.dumps(resposta, indent=2, ensure_ascii=False))
    
    print(f"\n\n[ESTADO FINAL DA FILA SQS]")
    print(f"   Total de lances: {len(fila_lances)}")
    for lance in fila_lances:
        print(f"   - {lance['lance_id'][:8]}... | {lance['camisa_id']} | R$ {lance['valor_do_lance']:.2f}")

