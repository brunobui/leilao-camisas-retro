"""
Script de Teste Completo do Sistema de Leilão
Testa todo o fluxo: API Gateway -> Lambda CriarLance -> SQS -> Lambda ProcessarLance -> DynamoDB -> SNS
"""

import json
import os
import sys
from pathlib import Path

# Adiciona o diretório pai ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "functions"))

from functions.criar_lance import lambda_handler as criar_lance_handler, fila_lances
from functions.processar_lance import lambda_handler as processar_lance_handler, banco_lances, notificacoes


def carregar_json(caminho):
    """Carrega um arquivo JSON e retorna o conteúdo."""
    try:
        # Converte caminho relativo para absoluto baseado no diretório do script
        script_dir = Path(__file__).parent
        caminho_absoluto = script_dir / caminho
        
        if not caminho_absoluto.exists():
            print(f"[ERRO] Arquivo não encontrado: {caminho_absoluto}")
            return None
        
        with open(caminho_absoluto, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERRO] Arquivo não encontrado: {caminho}")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERRO] Erro ao decodificar JSON: {e}")
        print(f"[ERRO] Arquivo: {caminho}")
        return None
    except Exception as e:
        print(f"[ERRO] Erro inesperado ao carregar JSON: {e}")
        print(f"[ERRO] Arquivo: {caminho}")
        return None


def limpar_dados():
    """Limpa os dados simulados para começar testes limpos."""
    fila_lances.clear()
    banco_lances.clear()
    notificacoes.clear()


def testar_criar_lance_sucesso():
    """Testa a criação de lances com sucesso."""
    print("\n" + "="*70)
    print("TESTE 1: Criar Lances - Casos de Sucesso")
    print("="*70)
    
    limpar_dados()
    
    # Carrega os eventos de teste
    eventos_sucesso = [
        "testes/evento_criar_lance_01.json",
        "testes/evento_criar_lance_02.json",
        "testes/evento_criar_lance_03.json",
        "testes/evento_criar_lance_04.json",
        "testes/evento_criar_lance_05.json"
    ]
    
    resultados = []
    
    for i, arquivo in enumerate(eventos_sucesso, 1):
        print(f"\n--- Teste {i}: {arquivo} ---")
        evento = carregar_json(arquivo)
        
        if evento is None:
            print(f"[FALHA] Não foi possível carregar o arquivo JSON")
            resultados.append({
                'arquivo': arquivo,
                'status_code': None,
                'sucesso': False
            })
            continue
        
        try:
            resposta = criar_lance_handler(evento)
            resultados.append({
                'arquivo': arquivo,
                'status_code': resposta.get('statusCode'),
                'sucesso': resposta.get('statusCode') == 200
            })
            
            if resposta.get('statusCode') == 200:
                print(f"[OK] Lance criado com sucesso!")
            else:
                print(f"[FALHA] Status code: {resposta.get('statusCode')}")
                if 'body' in resposta:
                    try:
                        body = json.loads(resposta['body'])
                        print(f"[DETALHES] {body.get('mensagem', 'Sem mensagem')}")
                    except:
                        print(f"[DETALHES] {resposta.get('body', 'Sem detalhes')}")
        except Exception as e:
            print(f"[ERRO] Exceção ao processar lance: {e}")
            resultados.append({
                'arquivo': arquivo,
                'status_code': None,
                'sucesso': False
            })
    
    print(f"\n[RESUMO TESTE 1]")
    print(f"   Total de testes: {len(resultados)}")
    print(f"   Sucessos: {sum(1 for r in resultados if r['sucesso'])}")
    print(f"   Falhas: {sum(1 for r in resultados if not r['sucesso'])}")
    print(f"   Lances na fila SQS: {len(fila_lances)}")
    
    return len(fila_lances) == len(eventos_sucesso)


def testar_criar_lance_erros():
    """Testa a criação de lances com casos de erro."""
    print("\n" + "="*70)
    print("TESTE 2: Criar Lances - Casos de Erro (Validação)")
    print("="*70)
    
    limpar_dados()
    
    # Carrega os eventos de erro
    eventos_erro = [
        "testes/evento_criar_lance_erro_01.json",  # Falta valor_do_lance
        "testes/evento_criar_lance_erro_02.json",  # Valor negativo
        "testes/evento_criar_lance_erro_03.json"   # Valor inválido (string)
    ]
    
    resultados = []
    
    for i, arquivo in enumerate(eventos_erro, 1):
        print(f"\n--- Teste de Erro {i}: {arquivo} ---")
        evento = carregar_json(arquivo)
        
        if evento is None:
            print(f"[FALHA] Não foi possível carregar o arquivo JSON")
            resultados.append({
                'arquivo': arquivo,
                'status_code': None,
                'esperado_erro': False
            })
            continue
        
        try:
            resposta = criar_lance_handler(evento)
            resultados.append({
                'arquivo': arquivo,
                'status_code': resposta.get('statusCode'),
                'esperado_erro': resposta.get('statusCode') != 200
            })
            
            if resposta.get('statusCode') != 200:
                print(f"[OK] Erro capturado corretamente! Status: {resposta.get('statusCode')}")
            else:
                print(f"[FALHA] Erro deveria ter sido capturado!")
        except Exception as e:
            print(f"[ERRO] Exceção ao processar lance: {e}")
            resultados.append({
                'arquivo': arquivo,
                'status_code': None,
                'esperado_erro': False
            })
    
    print(f"\n[RESUMO TESTE 2]")
    print(f"   Total de testes: {len(resultados)}")
    print(f"   Erros capturados: {sum(1 for r in resultados if r['esperado_erro'])}")
    print(f"   Lances na fila SQS (deve ser 0): {len(fila_lances)}")
    
    return len(fila_lances) == 0 and all(r['esperado_erro'] for r in resultados)


def testar_processar_lance():
    """Testa o processamento de lances."""
    print("\n" + "="*70)
    print("TESTE 3: Processar Lances - SQS -> DynamoDB -> SNS")
    print("="*70)
    
    # Primeiro cria alguns lances válidos
    eventos = [
        "testes/evento_criar_lance_01.json",
        "testes/evento_criar_lance_02.json",
        "testes/evento_criar_lance_03.json",
        "testes/evento_criar_lance_04.json"
    ]
    
    print("\n[Criando lances para processar...]")
    for arquivo in eventos:
        evento = carregar_json(arquivo)
        if evento:
            criar_lance_handler(evento)
    
    lances_antes = len(fila_lances)
    print(f"\n[ESTADO ANTES DO PROCESSAMENTO]")
    print(f"   Lances na fila SQS: {lances_antes}")
    print(f"   Lances no DynamoDB: {len(banco_lances)}")
    
    # Processa os lances
    print(f"\n[PROCESSANDO LANCES...]")
    evento_processar = carregar_json("testes/evento_processar_lance.json")
    if not evento_processar:
        evento_processar = {}
    
    resposta = processar_lance_handler(evento_processar)
    
    print(f"\n[ESTADO APÓS O PROCESSAMENTO]")
    print(f"   Lances na fila SQS (deve ser 0): {len(fila_lances)}")
    print(f"   Lances no DynamoDB: {len(banco_lances)}")
    print(f"   Notificações SNS: {len(notificacoes)}")
    
    print(f"\n[RESPOSTA DA LAMBDA]")
    print(json.dumps(resposta, indent=2, ensure_ascii=False))
    
    print(f"\n[NOTIFICAÇÕES ENVIADAS]")
    for notif in notificacoes:
        print(f"   - {notif['mensagem']}")
    
    sucesso = (
        len(fila_lances) == 0 and
        len(banco_lances) == lances_antes and
        resposta['statusCode'] == 200
    )
    
    return sucesso


def testar_fluxo_completo():
    """Testa o fluxo completo do sistema."""
    print("\n" + "="*70)
    print("TESTE 4: Fluxo Completo End-to-End")
    print("="*70)
    
    limpar_dados()
    
    # Cria lances para diferentes camisas
    eventos = [
        {"body": {"camisa_id": "CAMISA-VASCO-1997", "nome_usuario": "João", "valor_do_lance": 200.00}},
        {"body": {"camisa_id": "CAMISA-VASCO-1997", "nome_usuario": "Maria", "valor_do_lance": 300.00}},
        {"body": {"camisa_id": "CAMISA-CORINTHIANS-1990", "nome_usuario": "Pedro", "valor_do_lance": 400.00}},
        {"body": {"camisa_id": "CAMISA-VASCO-1997", "nome_usuario": "Ana", "valor_do_lance": 500.00}}
    ]
    
    print("\n[ETAPA 1] Criando lances...")
    for evento in eventos:
        resposta = criar_lance_handler(evento)
        if resposta['statusCode'] != 200:
            print(f"[ERRO] Falha ao criar lance: {resposta}")
            return False
    
    print(f"   [OK] {len(fila_lances)} lances criados e enviados para SQS")
    
    print("\n[ETAPA 2] Processando lances...")
    resposta = processar_lance_handler({})
    
    if resposta['statusCode'] != 200:
        print(f"[ERRO] Falha ao processar lances: {resposta}")
        return False
    
    print(f"   [OK] {resposta['body']}")
    
    print("\n[ETAPA 3] Verificando resultados...")
    
    # Verifica se a fila está vazia
    if len(fila_lances) != 0:
        print(f"[ERRO] Fila SQS deveria estar vazia, mas tem {len(fila_lances)} lances")
        return False
    
    # Verifica se os lances foram salvos
    if len(banco_lances) != 4:
        print(f"[ERRO] Deveria ter 4 lances no banco, mas tem {len(banco_lances)}")
        return False
    
    # Verifica se as notificações foram enviadas (deve ter 2 - uma para cada camisa)
    if len(notificacoes) != 2:
        print(f"[ERRO] Deveria ter 2 notificações (uma por camisa), mas tem {len(notificacoes)}")
        return False
    
    # Verifica se os vencedores estão corretos
    notif_vasco = [n for n in notificacoes if 'VASCO' in n['camisa_id']][0]
    notif_corinthians = [n for n in notificacoes if 'CORINTHIANS' in n['camisa_id']][0]
    
    if 'Ana' not in notif_vasco['mensagem'] or '500.00' not in notif_vasco['mensagem']:
        print(f"[ERRO] Vencedor do Vasco incorreto")
        return False
    
    if 'Pedro' not in notif_corinthians['mensagem'] or '400.00' not in notif_corinthians['mensagem']:
        print(f"[ERRO] Vencedor do Corinthians incorreto")
        return False
    
    print("   [OK] Todos os resultados estão corretos!")
    print(f"   [OK] Fila SQS vazia: {len(fila_lances) == 0}")
    print(f"   [OK] Lances no DynamoDB: {len(banco_lances)}")
    print(f"   [OK] Notificações SNS: {len(notificacoes)}")
    
    return True


def main():
    """Executa todos os testes."""
    print("\n" + "="*70)
    print("SISTEMA DE TESTES - LEILÃO DE CAMISAS RETRÔ")
    print("="*70)
    
    resultados = []
    
    # Executa os testes
    resultados.append(("Teste 1: Criar Lances (Sucesso)", testar_criar_lance_sucesso()))
    resultados.append(("Teste 2: Criar Lances (Erros)", testar_criar_lance_erros()))
    resultados.append(("Teste 3: Processar Lances", testar_processar_lance()))
    resultados.append(("Teste 4: Fluxo Completo", testar_fluxo_completo()))
    
    # Exibe resumo final
    print("\n" + "="*70)
    print("RESUMO FINAL DOS TESTES")
    print("="*70)
    
    for nome, sucesso in resultados:
        status = "[OK]" if sucesso else "[FALHA]"
        print(f"{status} {nome}")
    
    total_ok = sum(1 for _, sucesso in resultados if sucesso)
    total_testes = len(resultados)
    
    print(f"\n[RESULTADO GERAL]")
    print(f"   Testes aprovados: {total_ok}/{total_testes}")
    print(f"   Taxa de sucesso: {(total_ok/total_testes)*100:.1f}%")
    
    if total_ok == total_testes:
        print("\n[SUCESSO] Todos os testes passaram! Sistema funcionando corretamente.")
        return 0
    else:
        print(f"\n[ATENÇÃO] {total_testes - total_ok} teste(s) falharam.")
        return 1


if __name__ == "__main__":
    exit(main())

