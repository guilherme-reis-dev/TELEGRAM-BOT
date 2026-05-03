@echo off
REM Script para deploy no Heroku
REM Certifique-se de ter heroku-cli instalado: https://devcenter.heroku.com/articles/heroku-cli

echo.
echo =================================
echo   DEPLOY DO BOT NO HEROKU
echo =================================
echo.

REM 1. Fazer login no Heroku
echo [1/5] Fazendo login no Heroku...
heroku login

REM 2. Configurar variáveis de ambiente
echo.
echo [2/5] Configurando variáveis de ambiente...
echo Digite seu BOT_TOKEN:
set /p BOT_TOKEN=
heroku config:set BOT_TOKEN=%BOT_TOKEN%

echo.
echo Digite o LINK_ANUAL (ou deixe em branco para usar o padrão):
set /p LINK_ANUAL=
if not "%LINK_ANUAL%"=="" (
    heroku config:set LINK_ANUAL=%LINK_ANUAL%
)

REM 3. Verificar variáveis
echo.
echo [3/5] Variáveis configuradas:
heroku config

REM 4. Deploy
echo.
echo [4/5] Fazendo push para Heroku...
git push heroku fix-requirements:main

REM 5. Ver logs
echo.
echo [5/5] Verificando logs...
timeout /t 5
heroku logs --tail

echo.
echo =================================
echo   DEPLOY CONCLUÍDO!
echo =================================
echo.
echo Próximos passos:
echo - Teste o bot: /start
echo - Monitorar logs: heroku logs --tail
echo - Ver variáveis: heroku config
echo.
