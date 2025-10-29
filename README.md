🛰️ Monitor Global Cloud Status Notifier

Monitor Global Cloud Status Notifier es una herramienta automatizada desarrollada en Python que supervisa el estado de los principales servicios en la nube (como AWS, Azure, Microsoft 365, Google Cloud y Google Workspace) y notifica en tiempo real cualquier cambio o interrupción a través de Telegram.

El sistema consulta periódicamente las páginas oficiales de estado, detecta incidentes, degradaciones o caídas, y envía alertas personalizadas con hora local (Colombia) al chat configurado.
Además, se encuentra desplegado en Render, lo que permite mantener el monitor activo 24/7 sin necesidad de servidores locales.

🚀 Características principales

✅ Monitoreo automático de los servicios cloud más utilizados.

🔔 Notificaciones instantáneas vía Telegram Bot.

🌎 Conversión automática de hora a zona horaria de Colombia (America/Bogota).

💾 Registro histórico de estados detectados.

☁️ Despliegue en Render con soporte Flask para mantener el servicio en línea.

🛠️ Tecnologías utilizadas

Python 3.13

Flask (para el servicio web)

Requests y HTTPAdapter (para las consultas seguras)

dotenv (manejo de variables de entorno)

pytz (ajuste de zona horaria)

Render (plataforma de despliegue)

📩 Notificación de ejemplo
🚨 Cambio detectado en AWS
Anterior: ✅ Operativo
Actual: ⚠️ Problemas detectados
🕒 2025-10-29 18:30:42 (Hora Colombia)
🔗 Ver más: https://status.aws.amazon.com/
