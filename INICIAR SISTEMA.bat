@echo off
TITLE Sistema de Finanzas
setlocal

:: Ir a la carpeta del proyecto
cd /d "%~dp0"
if errorlevel 1 goto :error

:: Crear venv si no existe
if not exist "venv\Scripts\python.exe" (
    echo [INFO] No se encontro venv. Creando entorno virtual...
    py -m venv venv || goto :error_py
)

:: Activar entorno
call venv\Scripts\activate || goto :error

:: Instalar dependencias solo si faltan paquetes clave
if not exist "venv\Scripts\streamlit.exe" (
    echo [INFO] Instalando dependencias: streamlit no encontrado...
    python -m pip install --upgrade pip || goto :error
    python -m pip install -r requirements.txt || goto :error
)
if not exist "venv\Scripts\uvicorn.exe" (
    echo [INFO] Instalando dependencias: uvicorn no encontrado...
    python -m pip install --upgrade pip || goto :error
    python -m pip install -r requirements.txt || goto :error
)

:: Iniciar API
start "Cerebro (Backend)" "venv\Scripts\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000

:: Esperar arranque
timeout /t 3 /nobreak >nul

:: Iniciar ngrok
if exist "ngrok.exe" (
    start "Tunel (Ngrok)" "ngrok.exe" http --domain=dawne-unpostulated-junko.ngrok-free.dev 8000
) else (
    echo [WARN] ngrok.exe no encontrado en esta carpeta. Se omite tunel.
)

:: Iniciar dashboard
start "Panel Visual" "venv\Scripts\python.exe" -m streamlit run dashboard.py

echo [OK] Servicios lanzados. Puedes cerrar esta ventana.
timeout /t 3 >nul
exit /b 0

:error_py
echo [ERROR] No se encontro el comando 'py'. Instala Python 3 y vuelve a ejecutar.
pause
exit /b 1

:error
echo [ERROR] Fallo durante el inicio. Revisa el mensaje anterior.
pause
exit /b 1