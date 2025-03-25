@echo off

:: Vai nella directory dello script
cd /d "%~dp0"

:: Disabilita controllo della versione pip
set PIP_DISABLE_PIP_VERSION_CHECK=1

set script_folder=Scripts\Migliora il Timing Dei Sub

set launcher_file=%script_folder%\Launcher.py

:: Controlla se esiste la cartella "main" (ambiente virtuale)
if not exist main (
    echo Creo la cartella "main"...
    python\python.exe -m venv main
    echo Installo il necessario...
    main\Scripts\python.exe -m pip install --upgrade pip
    main\Scripts\python.exe -m pip install -r "%script_folder%\requirements.txt"
    main\Scripts\python.exe -m pip install pysrt --use-pep517
)

if exist "%launcher_file%" (
    echo Avvio di Launcher.py...
    call main\Scripts\python.exe "%launcher_file%"
) else (
    echo ERRORE: Impossibile trovare Launcher.py in "%launcher_file%".
)

:: Metti in pausa per verificare il risultato
pause
