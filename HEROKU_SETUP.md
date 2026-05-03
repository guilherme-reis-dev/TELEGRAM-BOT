# 🚀 Setup do Bot no Heroku

## 1️⃣ **Variáveis de Ambiente**

Configure no Heroku:
```bash
heroku config:set BOT_TOKEN="seu_token_aqui"
# DATABASE_URL já vem automaticamente com Heroku Postgres
```

Ou via Heroku Dashboard:
- Vá para Settings → Config Vars
- Adicione `BOT_TOKEN` com seu token

## 2️⃣ **Verificar Conexão com Banco**

```bash
heroku logs --tail
```

Procure por:
```
✅ Pool de conexões Postgres inicializado com sucesso
✅ Tabela 'usuarios' verificada/criada com sucesso
✅ Bot iniciado com sucesso!
```

## 3️⃣ **Estrutura de Melhorias Implementadas**

### ✅ Segurança
- ❌ Token removido do código
- ✅ Usando variáveis de ambiente
- ✅ Validação de variáveis obrigatórias

### ✅ Performance
- ✅ Pool de conexões (min=10, max=20)
- ✅ Reutilização de conexões
- ✅ Melhor para Heroku com múltiplas requisições

### ✅ Logging Profissional
- ✅ Logs estruturados
- ✅ Rastreável em `heroku logs`
- ✅ Níveis: INFO, ERROR, WARNING

### ✅ Banco de Dados
- ✅ Criação automática de tabelas
- ✅ Campos melhorados (telegram_id, created_at)
- ✅ Índices e constraints

## 4️⃣ **Arquivo requirements.txt**

Certifique-se que tem:
```
aiogram==3.x.x
asyncpg==0.27.x
python-dotenv==0.21.x
```

## 5️⃣ **Executar Localmente**

```bash
# Criar .env com BOT_TOKEN e DATABASE_URL
python main.py
```

## 6️⃣ **Deploy no Heroku**

```bash
git add .
git commit -m "Improve bot security and database handling"
git push heroku main
```

## 📊 **Monitorar**

```bash
# Logs em tempo real
heroku logs --tail

# Verificar variáveis
heroku config

# Conectar ao banco Heroku
heroku pg:psql
```

## ⚠️ **Problemas Comuns**

### Bot não inicia
```
Erro: BOT_TOKEN não foi definida
```
**Solução:** `heroku config:set BOT_TOKEN="token"`

### Erro de conexão ao banco
```
Erro ao criar pool de conexões
```
**Solução:** Verificar DATABASE_URL com `heroku config:get DATABASE_URL`

### Tabela não é criada
Rode manualmente:
```bash
heroku pg:psql < setup.sql
```

---

## 🎯 **Próximas Melhorias**

- [ ] Adicionar middlewares de validação
- [ ] Cache com Redis
- [ ] Tratamento de erros mais robusto
- [ ] Testes unitários
- [ ] CI/CD com GitHub Actions
