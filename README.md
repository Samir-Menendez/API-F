# API-F (Finanzas)

Aplicación con:
- Backend FastAPI (guarda movimientos en SQLite)
- Dashboard Streamlit (login simple + gráficos + descarga CSV)
- Script `INICIAR SISTEMA.bat` para levantar todo en Windows

## Requisitos
- Windows con Python instalado (recomendado Python 3.x)
- Git
- Opcional: `ngrok.exe` en la carpeta del proyecto para abrir el túnel (si no existe, el script omite ngrok)

## Configuración (.env)
1. Copia el archivo:
   - `.env.example` -> `.env`
2. Completa:
   - `MY_API_TOKEN`: token para el endpoint del backend
   - `DASHBOARD_PASSWORD` (opcional): contraseña del login del dashboard

> `finanzas.db` se crea automáticamente en la carpeta del proyecto la primera vez que se inicia el backend.

## Ejecutar todo
Ejecuta:
- Doble clic en `INICIAR SISTEMA.bat`
o desde PowerShell/CMD, estando en la carpeta del proyecto:
```bat
INICIAR SISTEMA.bat
```

## Uso del Backend
### Registrar movimiento
- `POST /registrar`
- Header: `x-token` (igual a `MY_API_TOKEN`)
- Body JSON:
```json
{
  "monto": 100.5,
  "categoria": "Comida",
  "nota": "super",
  "tipo": "gasto"
}
```

### Ver movimientos (últimos 20)
- `GET /ver-movimientos`

## Dashboard
El dashboard usa login simple. Luego puedes filtrar por mes/tipo, ver KPIs, gráficos y descargar el reporte CSV del período filtrado.

