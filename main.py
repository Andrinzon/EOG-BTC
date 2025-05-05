import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = '7215806088:AAHsLeDCOIhU89jJTemHQ8XgKLYOYmhXZgM'  # ← Reemplaza con tu token real de Telegram

# Scraper para obtener datos históricos
def obtener_datos_btc_por_anio(anio_deseado):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get('https://es.investing.com/crypto/bitcoin/historical-data')
    time.sleep(5)

    tabla = driver.find_element(By.CLASS_NAME, 'genTbl')
    filas = tabla.find_elements(By.TAG_NAME, 'tr')

    datos = []

    for fila in filas[1:]:
        columnas = fila.find_elements(By.TAG_NAME, 'td')
        if len(columnas) >= 2:
            fecha = columnas[0].text
            cierre = columnas[1].text.replace('.', '').replace(',', '.').replace('USD', '').strip()
            try:
                precio = float(cierre)
                fecha_formateada = datetime.strptime(fecha, '%d.%m.%Y')
                if fecha_formateada.year == anio_deseado:
                    mes = fecha_formateada.month
                    if mes not in datos:
                        datos.append((mes, precio))  # guardar un precio por mes
            except:
                continue

    driver.quit()

    datos_ordenados = {mes: precio for mes, precio in sorted(datos)}
    return datos_ordenados

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy el bot de históricos de Bitcoin.\n\n"
        "Usa el comando /historico seguido de un año (ej: /historico 2020) para ver los precios mensuales desde Investing.com."
    )

# Comando /historico <año>
async def historico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Usa el comando así: /historico 2020")
        return

    anio = int(context.args[0])
    if anio < 2013 or anio > datetime.now().year:
        await update.message.reply_text("Por favor elige un año entre 2013 y el actual.")
        return

    await update.message.reply_text(f"🔍 Buscando precios históricos de BTC en {anio} desde Investing.com...")

    precios = obtener_datos_btc_por_anio(anio)

    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    mensaje = f"📈 Precio de cierre de BTC (último disponible del mes) en {anio}:\n\n"
    for i in range(1, 13):
        if i in precios:
            mensaje += f"{meses[i-1]}: ${precios[i]:,.2f}\n"
        else:
            mensaje += f"{meses[i-1]}: Sin datos\n"

    await update.message.reply_text(mensaje)

# Main
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("historico", historico))
    print("Bot corriendo...")
    app.run_polling()
