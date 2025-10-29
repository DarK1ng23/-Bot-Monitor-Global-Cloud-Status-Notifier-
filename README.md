# Bot de Monitoreo de Servicios Cloud

Este bot notifica por Telegram cada 12 horas si hay problemas con los principales servicios cloud (AWS, Azure, Google Cloud, Cloudflare).

## Configuración

1. Crea un archivo `.env` con:
```
TELEGRAM_TOKEN=tu_token_aqui
CHAT_ID=tu_chat_id_aqui
```
2. Instala las dependencias:
```
pip install -r requirements.txt
```
3. Ejecuta el bot:
```
python status_monitor.py
```

## Despliegue en Render
- Sube este proyecto a GitHub.
- En Render, configura las variables de entorno.
- Start Command: `bash start.sh`
