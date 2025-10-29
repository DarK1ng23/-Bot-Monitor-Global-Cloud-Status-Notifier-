import requests
import time
import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot
from flask import Flask
import threading

# ==========================================
# ⚙️ CARGA DE VARIABLES DE ENTORNO
# ==========================================
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
INTERVALO_HORAS = 12  # cada cuánto revisar (12h)

# ==========================================
# 🌐 URLS A MONITOREAR
# ==========================================
URLS_MONITOREO = {
    "AWS": "https://status.aws.amazon.com/",
    "Microsoft Azure": "https://status.azure.com/",
    "Google Cloud": "https://status.cloud.google.com/",
    "Cloudflare": "https://www.cloudflarestatus.com/"
}

bot = Bot(token=TOKEN)
app = Flask(__name__)

# ==========================================
# 📤 FUNCIÓN PARA ENVIAR MENSAJE A TELEGRAM
# ==========================================
async def send_telegram_message(mensaje):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=mensaje)
        print(f"📨 Mensaje enviado: {mensaje}")
    except Exception as e:
        print(f"⚠️ Error al enviar mensaje: {e}")

# ==========================================
# 🔎 MONITOREO DE SERVICIOS
# ==========================================
def monitorear_servicios():
    while True:
        print("🛰️ Iniciando monitoreo de servicios...")
        problemas = []

        for nombre, url in URLS_MONITOREO.items():
            try:
                r = requests.get(url, timeout=10)
                if r.status_code != 200:
                    problemas.append(f"{nombre}: Código {r.status_code}")
            except Exception as e:
                problemas.append(f"{nombre}: Error {str(e)}")

        if problemas:
            mensaje = "⚠️ Problemas detectados:\n" + "\n".join(problemas)
            mensaje += "\n\n🔗 Verifica detalles en las páginas oficiales."
        else:
            mensaje = "✅ Todos los servicios están funcionando correctamente."

        asyncio.run(send_telegram_message(mensaje))
        time.sleep(INTERVALO_HORAS * 3600)

# ==========================================
# ♻️ AUTO-PING PARA MANTENER ACTIVO EL BOT
# ==========================================
def keep_alive():
    while True:
        try:
            requests.get("https://monitor-bot-335u.onrender.com")
            print("💓 Ping enviado a Render para mantener el bot activo.")
        except Exception as e:
            print(f"Error en ping: {e}")
        time.sleep(600)  # cada 10 minutos

# ==========================================
# 🌍 SERVIDOR WEB REQUERIDO POR RENDER
# ==========================================
@app.route("/")
def home():
    return "✅ Bot de monitoreo activo y en ejecución."

# ==========================================
# 🚀 EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    threading.Thread(target=monitorear_servicios, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
