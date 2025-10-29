import os
import time
import requests
from telegram import Bot
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Cargar variables del .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

def verificar_servicios():
    servicios = {
        "AWS": "https://status.aws.amazon.com",
        "Microsoft": "https://status.azure.com",
        "Google Cloud": "https://status.cloud.google.com",
        "Cloudflare": "https://www.cloudflarestatus.com"
    }

    problemas = []

    for nombre, url in servicios.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                problemas.append(f"⚠️ {nombre} devuelve código {response.status_code}.")
        except Exception as e:
            problemas.append(f"❌ Error en {nombre}: {e}")

    if problemas:
        mensaje = "🚨 Problemas detectados:\n" + "\n".join(problemas)
    else:
        mensaje = "✅ Todos los servicios están funcionando correctamente."

    bot.send_message(chat_id=CHAT_ID, text=mensaje)


def iniciar_bot():
    while True:
        verificar_servicios()
        time.sleep(43200)  # 12 horas (43200 segundos)


# --- SERVIDOR FLASK PARA RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot de monitoreo activo y escuchando."

def iniciar_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


# --- EJECUCIÓN ---
if __name__ == "__main__":
    Thread(target=iniciar_flask).start()
    iniciar_bot()
