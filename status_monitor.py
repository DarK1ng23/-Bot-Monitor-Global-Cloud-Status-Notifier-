import requests
import time
from datetime import datetime
from telegram import Bot

# --- Configuración ---
TELEGRAM_TOKEN = "TU_TOKEN_AQUI"
CHAT_ID = "TU_CHAT_ID_AQUI"

bot = Bot(token=TELEGRAM_TOKEN)

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
            # Consideramos que está operativo si responde bien
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

def monitorear():
    global previous_status
    while True:
        cambios = []
        reporte_general = "📊 REPORTE GENERAL DE ESTADO DE SERVICIOS:\n\n"
        
        for nombre, url in status_urls.items():
            estado_actual = verificar_servicio(nombre, url)
            estado_anterior = previous_status.get(nombre)
            
            # Reporte general siempre
            reporte_general += f"• {nombre}: {estado_actual}\n"
            if estado_actual != "✅ Operativo":
                reporte_general += f"   🔗 {url}\n"
            
            # Si el estado cambió, generamos alerta
            if estado_anterior and estado_anterior != estado_actual:
                cambios.append(generar_alerta(nombre, estado_actual, url))
            
            previous_status[nombre] = estado_actual
        
        # Enviamos alerta solo si hubo cambios
        if cambios:
            for alerta in cambios:
                bot.send_message(chat_id=CHAT_ID, text=alerta, parse_mode="Markdown")
        
        # Siempre enviamos el reporte general simple cada 15 minutos
        bot.send_message(chat_id=CHAT_ID, text=reporte_general)
        
        time.sleep(900)  # Esperar 15 minutos (900 segundos)

if __name__ == "__main__":
    monitorear()
