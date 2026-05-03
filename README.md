# 🤖 Bot Telegram com Aiogram 3.x + PostgreSQL

Um bot de Telegram moderno, seguro e profissional desenvolvido com **aiogram 3.x**, **asyncpg** e **PostgreSQL**, hospedado no **Heroku** com **Railway PostgreSQL**.

## 🎯 Características

✅ **Segurança**
- Token protegido em variáveis de ambiente
- Validação de configuração no startup
- Sem dados sensíveis no código

✅ **Performance**
- Pool de conexões asyncpg (min=10, max=20)
- Reutilização eficiente de conexões
- Async/await para melhor concorrência

✅ **Profissionalismo**
- Logging estruturado
- Estrutura modular (config, utils, bot, main)
- Tratamento robusto de erros
- Rastreamento de eventos

✅ **Escalabilidade**
- Pronto para produção
- Suporta múltiplos usuários simultâneos
- Banco de dados persistente

## 📁 Estrutura do Projeto

```
telegram_bot/
├── config.py              # Configurações centralizadas
├── utils.py               # Funções auxiliares e banco de dados
├── bot.py                 # Definição do bot e handlers
├── main.py                # Ponto de entrada (execução)
├── test_local.py          # Testes locais
├── requirements.txt       # Dependências Python
├── .env.example           # Template de variáveis de ambiente
├── .gitignore             # Arquivos a ignorar no git
├── Procfile               # Configuração Heroku
├── deploy.ps1             # Script de deploy (PowerShell)
├── deploy.bat             # Script de deploy (Batch)
├── PRE_DEPLOY_CHECKLIST.md # Checklist pré-deploy
├── HEROKU_SETUP.md        # Guia de setup Heroku
└── README.md              # Este arquivo
```

## 🚀 Quick Start

### 1. Clonar o Repositório
```bash
git clone seu-repo
cd telegram_bot
```

### 2. Configurar Variáveis de Ambiente
```bash
# Copiar template
cp .env.example .env

# Editar .env com suas credenciais
# BOT_TOKEN=seu_token_aqui
# DATABASE_URL=sua_url_postgres
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Testar Localmente
```bash
# Teste automático (recomendado)
python test_local.py

# Ou executar direto
python main.py
```

## 🌍 Deploy no Heroku

### Opção 1: Script Automático (Recomendado)
```powershell
# PowerShell (Windows)
powershell -ExecutionPolicy Bypass -File deploy.ps1

# Linux/Mac
bash deploy.sh
```

### Opção 2: Manual
```bash
# 1. Login no Heroku
heroku login

# 2. Configurar variáveis
heroku config:set BOT_TOKEN="seu_token"

# 3. Deploy
git push heroku main

# 4. Monitorar
heroku logs --tail
```

## 📊 Estrutura do Banco de Dados

### Tabela: `usuarios`
```sql
CREATE TABLE usuarios (
    id BIGINT PRIMARY KEY,
    nome TEXT NOT NULL,
    telegram_id TEXT UNIQUE NOT NULL,
    role TEXT DEFAULT 'cliente',
    plano TEXT DEFAULT NULL,
    data_inscricao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_usuarios_telegram_id ON usuarios(telegram_id);
CREATE INDEX idx_usuarios_role ON usuarios(role);
```

## 🎮 Comandos Disponíveis

| Comando | Descrição |
|---------|-----------|
| `/start` | Inicia o bot e mostra os planos |
| `/help` | Mostra a ajuda |
| `/planos` | Lista todos os planos disponíveis |
| `/status` | Mostra seu status |

## 🔧 Variáveis de Ambiente

| Variável | Descrição | Obrigatória |
|----------|-----------|-------------|
| `BOT_TOKEN` | Token do bot no BotFather | ✅ |
| `DATABASE_URL` | URL de conexão PostgreSQL | ✅ |
| `LINK_SEMANAL` | Link de pagamento semanal | ❌ |
| `LINK_SEMESTRAL` | Link de pagamento semestral | ❌ |
| `LINK_ANUAL` | Link de pagamento anual | ❌ |
| `DB_POOL_MIN_SIZE` | Tamanho mínimo do pool | ❌ (padrão: 10) |
| `DB_POOL_MAX_SIZE` | Tamanho máximo do pool | ❌ (padrão: 20) |

## 📝 Logs

Verificar logs em tempo real:
```bash
# Heroku
heroku logs --tail

# Local
# Logs são exibidos no console
```

Formato de log:
```
2024-05-02 10:30:45,123 - config - INFO - ✅ Variáveis de ambiente validadas
2024-05-02 10:30:46,456 - utils - INFO - ✅ Pool de conexões inicializado
2024-05-02 10:30:47,789 - bot - INFO - 👤 Novo acesso: 123456789 (João)
```

## 🧪 Testes Locais

Executar suite de testes:
```bash
python test_local.py
```

Testes incluem:
- ✅ Validação de imports
- ✅ Validação de configuração
- ✅ Conexão com banco de dados
- ✅ Registro de handlers

## 🐛 Troubleshooting

### Erro: "BOT_TOKEN não foi definida"
```bash
heroku config:set BOT_TOKEN="seu_token"
```

### Erro: "DATABASE_URL não definida"
Heroku Postgres configura automaticamente. Se não tiver:
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

### Bot não responde
```bash
# Verificar logs
heroku logs --tail -n 100

# Verificar variáveis
heroku config

# Reiniciar dyno
heroku restart
```

### Erro de conexão ao banco
```bash
# Verificar conexão
heroku pg:psql

# Ver detalhes da url
heroku config:get DATABASE_URL
```

## 📈 Monitoramento

### Monitorar em Tempo Real
```bash
heroku logs --tail
```

### Verificar Status do Dyno
```bash
heroku ps
```

### Ver Uso de Recursos
```bash
heroku stats
```

## 🔐 Segurança

- ✅ Token nunca em código (variáveis de ambiente)
- ✅ DATABASE_URL protegida
- ✅ `.gitignore` configurado para não commitar `.env`
- ✅ Validação de entrada
- ✅ Tratamento de erros gracioso

## 📦 Dependências

- **aiogram 3.4.1** - Framework Telegram
- **asyncpg 0.29.0** - Async PostgreSQL
- **SQLAlchemy 2.0.29** - ORM (opcional)
- **python-dotenv 1.0.1** - Variáveis de ambiente

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 👨‍💻 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação no `HEROKU_SETUP.md`
2. Consulte a checklist em `PRE_DEPLOY_CHECKLIST.md`
3. Execute `python test_local.py` para diagnóstico

## 🎉 Próximas Melhorias

- [ ] Sistema de autenticação
- [ ] Webhooks em vez de polling
- [ ] Cache com Redis
- [ ] Testes automatizados (pytest)
- [ ] CI/CD com GitHub Actions
- [ ] Dashboard de administração
- [ ] Backup automático do banco

---

**Made with ❤️ by Reis**
