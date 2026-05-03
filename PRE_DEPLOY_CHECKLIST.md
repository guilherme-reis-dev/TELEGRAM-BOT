# ✅ PRÉ-DEPLOY CHECKLIST

## Antes de fazer Deploy:

- [ ] **BOT_TOKEN obtido do BotFather**
  - Abra https://t.me/BotFather
  - Use `/newbot` para criar um novo bot
  - Copie o token

- [ ] **Heroku CLI instalado**
  ```bash
  # Baixar em: https://devcenter.heroku.com/articles/heroku-cli
  heroku --version
  ```

- [ ] **Heroku app criado**
  ```bash
  # Se ainda não tem, crie:
  heroku create seu-app-name
  
  # Ou veja apps existentes:
  heroku apps
  ```

- [ ] **Heroku Postgres add-on**
  ```bash
  # Verificar se já tem:
  heroku addons
  
  # Se não tem, adicione:
  heroku addons:create heroku-postgresql:hobby-dev
  ```

- [ ] **Git branch correto**
  ```bash
  git branch -v
  # Deve estar em: fix-requirements
  ```

- [ ] **Procfile criado (se necessário)**
  ```bash
  # Verificar se existe
  ls Procfile
  
  # Se não existe, criar com:
  # web: python main.py
  ```

## Execução do Deploy:

### Opção 1: Script Automático (Recomendado)
```powershell
powershell -ExecutionPolicy Bypass -File deploy.ps1
```

### Opção 2: Passos Manuais
```bash
# 1. Login
heroku login

# 2. Set environment variables
heroku config:set BOT_TOKEN="seu_token"
heroku config:set LINK_ANUAL="seu_link" # (opcional)

# 3. Deploy
git push heroku fix-requirements:main

# 4. Ver logs
heroku logs --tail

# 5. Testar
# Abra https://t.me/seu_bot_name
# Digite /start
```

## Após Deploy:

✅ Bot deve responder no Telegram
✅ Logs mostram: "✅ Bot iniciado com sucesso!"
✅ Tabela de usuários criada automaticamente
✅ Usuários registrados no banco de dados

## Troubleshooting:

| Erro | Solução |
|------|---------|
| `Erro: BOT_TOKEN não foi definida` | `heroku config:set BOT_TOKEN="token"` |
| `Connection refused` | Verificar DATABASE_URL: `heroku config:get DATABASE_URL` |
| `Tabla não criada` | Rodar: `heroku pg:psql` e copiar SQL de main.py |
| `Bot não responde` | Ver logs: `heroku logs --tail -n 100` |

---

💡 **Dica**: Sempre monitore os logs após deploy:
```bash
heroku logs --tail
```

Pressione `Ctrl+C` para sair.
