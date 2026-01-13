@echo off
TITLE Sistema de Finanzas y Trading 🚀

:: 1. Entrar a la carpeta del proyecto
cd /d "C:\Users\Sam1R\Desktop\mi_finanzas"

:: 2. Activar el entorno virtual (si usas venv)
call venv\Scripts\activate

:: 3. Iniciar el Servidor (API) en una ventana aparte
start "Cerebro (Backend)" uvicorn main:app --host 0.0.0.0 --port 8000

:: 4. Esperar 3 segundos para que el servidor arranque
timeout /t 3 /nobreak >nul

:: 5. Iniciar Ngrok (Tu túnel fijo)
:: OJO: Verifica que este sea tu dominio correcto
start "Tunel (Ngrok)" ngrok http --domain=burt-unbleeding-nondespotically.ngrok-free.dev 8000

:: 6. Iniciar el Dashboard (Usando Python para llamar a Streamlit)
:: Esta es la linea clave que fallaba antes. Ahora la forzamos con python.exe
start "Panel Visual" "venv\Scripts\python.exe" -m streamlit run dashboard.py

:: 7. Minimizar esta ventana (opcional)
exit