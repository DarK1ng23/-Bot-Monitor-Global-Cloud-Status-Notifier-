import requests
import time
import asyncio
from telegram import Bot
from flask import Flask
import threading

# ==========================================
# 🔧 CONFIGURACIÓN DEL BOT
# ==========================================
TOKEN = "TU_TOKEN_TELEGRAM"  # reemplázalo por tu token real
CHAT_ID = "TU_CHAT_ID"       # reemplázalo por tu chat ID real
INTERVALO_HORAS = 12         # cada cuánto revisar (12h)
URLS_MONITOREO = {
    "AWS": "https://status.aws.amazon.com/",
    "Microsoft": "https://status.azure.com/",
    "Google Cloud": "https://status.cloud.google.com/",
    "Cloudflare": "https://www.cloudflarestatus.com/"
}

bot = Bot(token=TOKEN)
app = Flask(__name__)

# ==========================================
# 🧠 FUNCIÓN ASÍNCRONA PARA ENVIAR MENSAJES
# ==========================================
async def send_telegram_message(mensaje):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=mensaje)
        print(f"Mensaje enviado a Telegram: {mensaje}")
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")

# ==========================================
# 🚀 FUNCIÓN PRINCIPAL DE MONITOREO
# ==========================================
def monitorear_servicios():
    while True:
        print("Iniciando monitoreo de servicios...")
        problemas = []

        for nombre, url in URLS_MONITOREO.items():
            try:
                respuesta = requests.get(url, timeout=10)
                if respuesta.status_code != 200:
                    problemas.append(f"{nombre}: Código {respuesta.status_code}")
            except Exception as e:
                problemas.append(f"{nombre}: Error {str(e)}")

        if problemas:
            mensaje = "⚠️ Problemas detectados en los servicios:\n" + "\n".join(problemas)
            mensaje += "\n\n🔗 Verifica más en: https://status.aws.amazon.com o servicios similares."
        else:
            mensaje = "✅ Todos los servicios están funcionando correctamente."

        asyncio.run(send_telegram_message(mensaje))

        # Espera 12 horas antes del siguiente chequeo
        time.sleep(INTERVALO_HORAS * 3600)

# ==========================================
# ♻️ AUTO-PING CADA 10 MINUTOS (Mantener vivo Render)
# ==========================================
def keep_alive():
    while True:
        try:
            requests.get("https://monitor-bot-335u.onrender.com")
            print("Ping enviado para mantener activo el bot en Render.")
        except Exception as e:
            print(f"Error en ping: {e}")
        time.sleep(600)  # cada 10 min

# ==========================================
# 🌐 SERVIDOR FLASK (Render necesita un puerto activo)
# ==========================================
@app.route("/")
def home():
    return "✅ Monitor de servicios activo y en ejecución."

# ==========================================
# 🏁 INICIO DE THREADS
# ==========================================
if __name__ == "__main__":
    threading.Thread(target=monitorear_servicios, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
