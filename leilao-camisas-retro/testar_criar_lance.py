"""
Script simples para testar apenas a criação de lances
"""

import json
import sys
from pathlib import Path

# Adiciona o diretório ao path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "functions"))

from functions.criar_lance import lambda_handler, fila_lances


def testar_com_json(arquivo_json):
    """Testa criar lance usando um arquivo JSON."""
    print(f"\n{'='*60}")
    print(f"Testando com: {arquivo_json}")
    print('='*60)
    
    try:
        # Carrega o JSON
        caminho = Path(__file__).parent / arquivo_json
        if not caminho.exists():
            print(f"[ERRO] Arquivo não encontrado: {caminho}")
            return False
        
        with open(caminho, 'r', encoding='utf-8') as f:
            evento = json.load(f)
        
        print(f"[OK] Arquivo JSON carregado com sucesso")
        
        # Executa a lambda
        resposta = lambda_handler(evento)
        
        # Verifica resultado
        if resposta.get('statusCode') == 200:
            print(f"[OK] Lance criado com sucesso!")
            print(f"[OK] Status Code: {resposta['statusCode']}")
            
            # Mostra detalhes do body
            try:
                body = json.loads(resposta['body'])
                print(f"[OK] Mensagem: {body.get('mensagem')}")
                print(f"[OK] Lance ID: {body.get('lance_id')}")
            except:
                print(f"[INFO] Body: {resposta.get('body')}")
            
            return True
        else:
            print(f"[FALHA] Status Code: {resposta.get('statusCode')}")
            try:
                body = json.loads(resposta.get('body', '{}'))
                print(f"[ERRO] Mensagem: {body.get('mensagem', 'Sem mensagem')}")
            except:
                print(f"[ERRO] Body: {resposta.get('body', 'Sem detalhes')}")
            return False
            
    except json.JSONDecodeError as e:
        print(f"[ERRO] Erro ao decodificar JSON: {e}")
        return False
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa testes de criação de lances."""
    print("\n" + "="*60)
    print("TESTE DE CRIAÇÃO DE LANCES")
    print("="*60)
    
    # Limpa a fila antes de começar
    fila_lances.clear()
    
    # Lista de arquivos para testar
    arquivos_teste = [
        "testes/evento_criar_lance_01.json",
        "testes/evento_criar_lance_02.json",
        "testes/evento_criar_lance_03.json",
        "testes/evento_criar_lance_04.json",
        "testes/evento_criar_lance_05.json"
    ]
    
    resultados = []
    
    for arquivo in arquivos_teste:
        sucesso = testar_com_json(arquivo)
        resultados.append((arquivo, sucesso))
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    sucessos = sum(1 for _, s in resultados if s)
    total = len(resultados)
    
    for arquivo, sucesso in resultados:
        status = "[OK]" if sucesso else "[FALHA]"
        print(f"{status} {arquivo}")
    
    print(f"\n[RESULTADO]")
    print(f"   Sucessos: {sucessos}/{total}")
    print(f"   Falhas: {total - sucessos}/{total}")
    print(f"   Lances na fila: {len(fila_lances)}")
    
    if sucessos == total:
        print("\n[SUCESSO] Todos os testes passaram!")
        return 0
    else:
        print(f"\n[ATENÇÃO] {total - sucessos} teste(s) falharam.")
        return 1


if __name__ == "__main__":
    exit(main())

