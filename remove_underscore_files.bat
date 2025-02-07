@echo off
setlocal enabledelayedexpansion

echo Removendo arquivos com "_" no nome na pasta historico...

for /r "historico" %%F in (*_*) do (
    echo Removendo arquivo: %%F
    del "%%F"
)

echo Processo concluído.
pause
