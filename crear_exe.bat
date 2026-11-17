@echo off
setlocal
title Crear ejecutable - R&A Organizador

echo.
echo ==========================================
echo       R&A Organizador - Compilador
echo ==========================================
echo.

REM Detectar Python (primero el launcher de Windows).
where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON=py"
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set "PYTHON=python"
    ) else (
        echo ERROR: No se encontro Python.
        echo Instala Python 3.10 o superior y vuelve a intentarlo.
        pause
        exit /b 1
    )
)

echo Comprobando PyInstaller...
%PYTHON% -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo.
    echo ERROR: No se pudo instalar o actualizar PyInstaller.
    pause
    exit /b 1
)

echo.
echo Generando version Onefolder...
%PYTHON% -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onedir ^
    --windowed ^
    --name "RyA_Organizador" ^
    "organizador.py"

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller no pudo generar la aplicacion.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Compilacion finalizada.
echo.
echo La aplicacion esta en:
echo dist\RyA_Organizador\
echo.
echo IMPORTANTE: distribuye la carpeta completa,
echo no solamente el archivo EXE.
echo ==========================================
echo.
pause
endlocal
