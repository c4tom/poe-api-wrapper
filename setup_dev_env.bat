@echo off
setlocal enabledelayedexpansion

REM Configurações de cores para mensagens
color 0A

REM Título do script
echo ========================================
echo   CONFIGURADOR DE AMBIENTE DE DESENVOLVIMENTO
echo ========================================

REM Verifica se o ambiente virtual existe
if not exist "venv\" (
    echo [CRIANDO] Ambiente virtual Python
    python -m venv venv
)

REM Ativa o ambiente virtual
call venv\Scripts\activate

REM Atualiza pip e ferramentas de instalação
echo [ATUALIZANDO] Pip e ferramentas de instalação
pip install --upgrade pip setuptools wheel

REM Limpa caches e distribuições inválidas
echo [LIMPANDO] Caches e distribuições inválidas
pip cache purge

REM Instala dependências principais
echo [INSTALANDO] Dependências do projeto
pip install -e .[llm,proxy,web_search]

REM Instala dependências específicas que costumam dar problema
pip install fastapi-poe ballyregan

REM Verifica instalação das dependências
echo [VERIFICANDO] Instalação das dependências
python -c "import fastapi_poe; print('[OK] fastapi_poe importado com sucesso')"
python -c "import ballyregan; print('[OK] ballyregan importado com sucesso')"

echo.
echo ========================================
echo   AMBIENTE DE DESENVOLVIMENTO CONFIGURADO
echo ========================================

REM Mantém a janela aberta para visualização
pause
