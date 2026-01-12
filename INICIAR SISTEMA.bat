@echo off
cd "C:\Users\Sam1R\Desktop\mi_finanzas"
call venv\Scripts\activate

:: Iniciar el servidor Python en una ventana minimizada
start /min cmd /k "uvicorn main:app --host 0.0.0.0 --port 8000"

:: Esperar 2 segundos y abrir Ngrok
timeout /t 2
start /min cmd /k "ngrok http 8000"

echo Sistema de Finanzas Iniciado 🚀