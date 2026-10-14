@echo off
rem MKWiita PSD09: un clic para convertir tu ISO/WBFS propio en Windows.
rem Se abre un selector de archivo. Nunca sube el juego a GitHub.
setlocal EnableExtensions
cd /d "%~dp0"
title MKWiita PSD09 - Convertidor automatico
set "PYTHONUTF8=1"
set "PYTHONUNBUFFERED=1"
echo.
echo ====================================================
echo  MKWiita PSD09 - Conversion automatica para PS Vita
echo ====================================================
echo.
where py >nul 2>nul
if errorlevel 1 goto :try_python
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
if errorlevel 1 goto :try_python
py -3 "tools\vita\psd09_wizard.py" "%~1"
set "result=%errorlevel%"
goto :finished

:try_python
where python >nul 2>nul
if errorlevel 1 goto :no_python
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
if errorlevel 1 goto :no_python
python "tools\vita\psd09_wizard.py" "%~1"
set "result=%errorlevel%"
goto :finished

:no_python
echo ERROR: No se encontro Python 3.11 o superior.
echo Descarga Python: https://www.python.org/downloads/
echo Durante la instalacion marca "Add python.exe to PATH".
echo Despues cierra esta ventana y vuelve a ejecutar el conversor.
set "result=1"

:finished
echo.
if "%result%"=="0" (
    echo Listo. Comprueba la carpeta build\vita\data\mkw
) else (
    echo El proceso no se completo. Si se genero build-assets-log.txt,
    echo envia ese registro para diagnosticar el problema.
)
echo.
echo Esta ventana permanecera abierta hasta que presiones una tecla.
pause >nul
exit /b %result%
