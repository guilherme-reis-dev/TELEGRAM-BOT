"""
Script para testar o bot localmente
Antes de fazer deploy no Heroku
"""

import os
import sys
import asyncio
from pathlib import Path

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

async def test_imports():
    """Testa se todos os imports funcionam"""
    print("🧪 Testando imports...")
    try:
        import config
        import utils
        import bot
        print("✅ Todos os imports ok!\n")
        return True
    except ImportError as e:
        print(f"❌ Erro de import: {e}\n")
        return False

async def test_config():
    """Testa se as configurações estão corretas"""
    print("🧪 Testando configurações...")
    try:
        from config import validate_config, BOT_TOKEN, DATABASE_URL, PLANOS
        
        if not validate_config():
            print("❌ Configuração inválida\n")
            return False
        
        print(f"✅ BOT_TOKEN: {'***' + BOT_TOKEN[-5:] if BOT_TOKEN else 'NÃO CONFIGURADO'}")
        print(f"✅ DATABASE_URL: {'***' + DATABASE_URL.split('@')[-1] if DATABASE_URL else 'NÃO CONFIGURADO'}")
        print(f"✅ Planos disponíveis: {list(PLANOS.keys())}\n")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar config: {e}\n")
        return False

async def test_db_connection():
    """Testa conexão com o banco de dados"""
    print("🧪 Testando conexão com banco de dados...")
    try:
        from utils import init_db_pool, close_db_pool
        
        print("  ⏳ Conectando ao Postgres...")
        await init_db_pool()
        print("✅ Conexão com banco de dados ok!")
        
        await close_db_pool()
        print("✅ Pool fechado com sucesso\n")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}\n")
        return False

async def test_bot_handlers():
    """Testa se os handlers estão registrados"""
    print("🧪 Testando handlers do bot...")
    try:
        from bot import dp
        
        # Contar handlers
        handlers_count = len(dp.filters.update.handlers)
        print(f"✅ {handlers_count} handlers registrados")
        print("✅ Bot handlers ok!\n")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar handlers: {e}\n")
        return False

async def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "="*50)
    print("   TESTE LOCAL DO BOT DO TELEGRAM")
    print("="*50 + "\n")
    
    results = []
    
    # 1. Testar imports
    results.append(("Imports", await test_imports()))
    
    # 2. Testar configurações
    results.append(("Configurações", await test_config()))
    
    # 3. Testar banco (opcional)
    from config import DATABASE_URL
    if DATABASE_URL:
        results.append(("Banco de Dados", await test_db_connection()))
    else:
        print("⚠️ DATABASE_URL não configurado, pulando teste de conexão\n")
    
    # 4. Testar handlers
    results.append(("Handlers do Bot", await test_bot_handlers()))
    
    # Resumo
    print("="*50)
    print("   RESUMO DOS TESTES")
    print("="*50 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} testes passaram\n")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Bot pronto para deploy.\n")
        return True
    else:
        print("⚠️ Alguns testes falharam. Verifique as configurações.\n")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⌨️ Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro durante testes: {e}")
        sys.exit(1)
