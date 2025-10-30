import requests
import time
from datetime import datetime
from telegram import Bot
import asyncio
from flask import Flask
import os

# --- Configuración ---
TELEGRAM_TOKEN = "TU_TOKEN_AQUI"
CHAT_ID = "TU_CHAT_ID_AQUI"

bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

# URLs de estado
status_urls = {
    "AWS": "https://status.aws.amazon.com/",
    "Azure": "https://status.azure.com/en-us/status",
    "Microsoft 365": "https://status.office.com/",
    "Google Cloud": "https://status.cloud.google.com/",
    "Google Workspace": "https://www.google.com/appsstatus/dashboard/",
}

# Estado previo
previous_status = {}

def verificar_servicio(nombre, url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return "✅ Operativo"
        else:
            return "⚠️ Problemas detectados"
    except requests.exceptions.SSLError:
        return "❌ Error SSL"
    except Exception:
        return "⚠️ Problemas detectados"

def generar_reporte():
    reporte = "📊 REPORTE GENERAL DE ESTADO DE SERVICIOS:\n\n"
    for nombre, url in status_urls.items():
        estado = verificar_servicio(nombre, url)
        reporte += f"• {nombre}: {estado}\n"
        if estado != "✅ Operativo":
            reporte += f"   🔗 {url}\n"
    reporte += f"\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Hora Colombia)"
    return reporte

def generar_alerta(nombre, estado, url):
    return f"🚨 Cambio detectado en *{nombre}*\n\nNuevo estado: {estado}\n🔗 {url}"

# --- Monitor asíncrono ---
async def monitorear():
    global previous_status
    while True:
        cambios = []
        reporte_general = "📊 REPORTE GENERAL DE ESTADO DE SERVICIOS:\n\n"

        for nombre, url in status_urls.items():
            estado_actual = verificar_servicio(nombre, url)
            estado_anterior = previous_status.get(nombre)

            reporte_general += f"• {nombre}: {estado_actual}\n"
            if estado_actual != "✅ Operativo":
                reporte_general += f"   🔗 {url}\n"

            if estado_anterior and estado_anterior != estado_actual:
                cambios.append(generar_alerta(nombre, estado_actual, url))

            previous_status[nombre] = estado_actual

        # Enviar alertas si hay cambios
        if cambios:
            for alerta in cambios:
                await bot.send_message(chat_id=CHAT_ID, text=alerta, parse_mode="Markdown")

        # Enviar reporte general cada 15 minutos
        await bot.send_message(chat_id=CHAT_ID, text=reporte_general)

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🕒 Próximo reporte en 15 minutos...")
        await asyncio.sleep(900)  # 15 minutos = 900 segundos

@app.route("/")
def home():
    return "✅ Bot Monitor Global Cloud Status corriendo correctamente."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    loop = asyncio.get_event_loop()
    loop.create_task(monitorear())
    app.run(host="0.0.0.0", port=port)
