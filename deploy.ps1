# Script para deploy no Heroku
# Executar com: powershell -ExecutionPolicy Bypass -File deploy.ps1

Write-Host "`n=================================" -ForegroundColor Cyan
Write-Host "  DEPLOY DO BOT NO HEROKU" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# 1. Fazer login no Heroku
Write-Host "[1/5] Fazendo login no Heroku..." -ForegroundColor Yellow
heroku login

# 2. Configurar variáveis de ambiente
Write-Host ""
Write-Host "[2/5] Configurando variáveis de ambiente..." -ForegroundColor Yellow

$BOT_TOKEN = Read-Host "Digite seu BOT_TOKEN"
heroku config:set BOT_TOKEN=$BOT_TOKEN

Write-Host ""
$LINK_ANUAL = Read-Host "Digite o LINK_ANUAL (ou deixe em branco para usar o padrão)"
if ($LINK_ANUAL) {
    heroku config:set LINK_ANUAL=$LINK_ANUAL
}

# 3. Verificar variáveis
Write-Host ""
Write-Host "[3/5] Variáveis configuradas:" -ForegroundColor Yellow
heroku config

# 4. Deploy
Write-Host ""
Write-Host "[4/5] Fazendo push para Heroku..." -ForegroundColor Yellow
git push heroku fix-requirements:main

# 5. Ver logs
Write-Host ""
Write-Host "[5/5] Verificando logs..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
heroku logs --tail

Write-Host ""
Write-Host "=================================" -ForegroundColor Green
Write-Host "  DEPLOY CONCLUÍDO!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Cyan
Write-Host "- Teste o bot: /start"
Write-Host "- Monitorar logs: heroku logs --tail"
Write-Host "- Ver variáveis: heroku config"
Write-Host ""
