"""
Lambda Function: ProcessarLance
Simula o comportamento de uma Lambda que processa mensagens da SQS,
salva no DynamoDB e envia notificações via SNS.
"""

import json
from datetime import datetime

# Importa a fila compartilhada do criar_lance
# Em produção, isso seria uma fila SQS real
from functions.criar_lance import fila_lances

# Simulação do serviço DynamoDB (NoSQL Database)
# Na AWS real, isso seria uma tabela DynamoDB real
banco_lances = []

# Simulação do serviço SNS (Simple Notification Service)
# Na AWS real, isso seria um tópico SNS real
notificacoes = []


def lambda_handler(event, context=None):
    """
    Handler principal da Lambda no formato AWS.
    
    Args:
        event: Dicionário contendo as mensagens da SQS (simulando trigger SQS)
        context: Contexto da execução Lambda (opcional para simulação local)
    
    Returns:
        dict: Resposta no formato JSON com statusCode e quantidade processada
    """
    print("\n" + "="*60)
    print(">>> LAMBDA: ProcessarLance - Iniciando processamento")
    print("="*60)
    
    try:
        # Simula a leitura de mensagens da SQS
        # Na AWS real, o evento viria com Records contendo as mensagens
        # Para simulação local, vamos processar todos os lances pendentes da fila
        
        lances_processados = []
        
        # Processa todos os lances pendentes na fila
        while fila_lances:
            lance = fila_lances.pop(0)  # Remove o primeiro lance da fila (FIFO)
            
            print(f"\n[PROCESSANDO LANCE]")
            print(f"   ID: {lance['lance_id']}")
            print(f"   Camisa: {lance['camisa_id']}")
            print(f"   Usuario: {lance['nome_usuario']}")
            print(f"   Valor: R$ {lance['valor_do_lance']:.2f}")
            
            # Atualiza o status do lance
            lance['status'] = 'processado'
            lance['processado_em'] = datetime.now().isoformat()
            
            # Simula o salvamento no DynamoDB
            # Na AWS real, isso seria: dynamodb.put_item(TableName=..., Item=...)
            banco_lances.append(lance)
            lances_processados.append(lance)
            
            print(f"   [OK] Lance salvo no DynamoDB")
        
        # Verifica o maior lance para cada camisa e envia notificações
        if lances_processados:
            print(f"\n[ANALISANDO] Lances para determinar vencedores...")
            verificar_e_notificar_vencedores()
        
        quantidade_processada = len(lances_processados)
        
        print(f"\n[OK] Processamento concluido!")
        print(f"   Lances processados: {quantidade_processada}")
        print(f"   Total no banco: {len(banco_lances)}")
        print("="*60 + "\n")
        
        # Retorna resposta de sucesso
        return {
            'statusCode': 200,
            'body': json.dumps({
                'mensagem': 'Lances processados com sucesso',
                'quantidade_processada': quantidade_processada
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


def verificar_e_notificar_vencedores():
    """
    Verifica qual é o maior lance para cada camisa e envia notificações SNS.
    Simula a lógica de determinar quem está vencendo o leilão.
    """
    # Agrupa lances por camisa_id e encontra o maior lance de cada uma
    lances_por_camisa = {}
    
    for lance in banco_lances:
        camisa_id = lance['camisa_id']
        if camisa_id not in lances_por_camisa:
            lances_por_camisa[camisa_id] = []
        lances_por_camisa[camisa_id].append(lance)
    
    # Para cada camisa, encontra o maior lance
    for camisa_id, lances in lances_por_camisa.items():
        maior_lance = max(lances, key=lambda x: x['valor_do_lance'])
        
        # Cria a notificação
        notificacao = {
            'tipo': 'lance_vencedor',
            'camisa_id': camisa_id,
            'nome_usuario': maior_lance['nome_usuario'],
            'valor_do_lance': maior_lance['valor_do_lance'],
            'timestamp': datetime.now().isoformat(),
            'mensagem': f"[VENCEDOR] {maior_lance['nome_usuario']} esta vencendo o leilao da {camisa_id} com lance de R$ {maior_lance['valor_do_lance']:.2f}!"
        }
        
        # Simula o envio para o SNS
        # Na AWS real, isso seria: sns.publish(TopicArn=..., Message=...)
        notificacoes.append(notificacao)
        
        print(f"\n[NOTIFICACAO SNS ENVIADA]")
        print(f"   {notificacao['mensagem']}")


# Bloco de teste para execução local
if __name__ == "__main__":
    print("\n" + "[MODO DE TESTE LOCAL] - ProcessarLance")
    print("="*60)
    
    # Primeiro, vamos simular alguns lances sendo criados
    print("\n[SIMULANDO] Criacao de lances...")
    from functions.criar_lance import lambda_handler as criar_lance_handler
    
    lances_teste = [
        {
            'body': {
                'camisa_id': 'CAMISA-VASCO-1997',
                'nome_usuario': 'João Silva',
                'valor_do_lance': 250.00
            }
        },
        {
            'body': {
                'camisa_id': 'CAMISA-VASCO-1997',
                'nome_usuario': 'Maria Santos',
                'valor_do_lance': 350.00
            }
        },
        {
            'body': {
                'camisa_id': 'CAMISA-CORINTHIANS-1990',
                'nome_usuario': 'Pedro Costa',
                'valor_do_lance': 400.00
            }
        },
        {
            'body': {
                'camisa_id': 'CAMISA-VASCO-1997',
                'nome_usuario': 'Ana Oliveira',
                'valor_do_lance': 500.00
            }
        }
    ]
    
    # Cria os lances
    for lance_evento in lances_teste:
        criar_lance_handler(lance_evento)
    
    print(f"\n[ESTADO DA FILA] Antes do processamento:")
    print(f"   Lances pendentes: {len(fila_lances)}")
    
    # Agora processa os lances
    print("\n[INICIANDO] Processamento...")
    evento_sqs = {}  # Em produção, viria com Records da SQS
    resposta = lambda_handler(evento_sqs)
    
    print(f"\n[RESPOSTA DA LAMBDA]")
    print(json.dumps(resposta, indent=2, ensure_ascii=False))
    
    print(f"\n\n[ESTADO FINAL]")
    print(f"   Lances no banco DynamoDB: {len(banco_lances)}")
    print(f"   Notificacoes SNS enviadas: {len(notificacoes)}")
    
    print(f"\n[DETALHES DAS NOTIFICACOES]")
    for notif in notificacoes:
        print(f"   - {notif['mensagem']}")

