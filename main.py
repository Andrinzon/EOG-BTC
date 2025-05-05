import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import aiohttp
from datetime import datetime
import time

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = '7215806088:AAHsLeDCOIhU89jJTemHQ8XgKLYOYmhXZgM'  # Reemplaza esto por tu token de Telegram
API_KEY = '6ca5dcd1-39a1-402a-b00e-97a7be25b217'  # Clave de LiveCoinWatch

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy el bot de históricos de Bitcoin.\n\n"
        "Usa el comando /historico seguido de un año (desde 2013 en adelante).\n"
        "Ejemplo: /historico 2020"
    )

async def get_monthly_prices_lcw(year: int):
    url = "https://api.livecoinwatch.com/coins/single/history"
    headers = {
        "content-type": "application/json",
        "x-api-key": API_KEY
    }

    prices_by_month = {}

    async with aiohttp.ClientSession() as session:
        for month in range(1, 13):
            # Día 15 del mes
            dt = datetime(year, month, 15)
            timestamp = int(time.mktime(dt.timetuple()) * 1000)

            payload = {
                "currency": "USD",
                "code": "BTC",
                "start": timestamp,
                "end": timestamp,
                "meta": False
            }

            async with session.post(url, headers=headers, json=payload) as response:
                try:
                    data = await response.json()
                    price = data["rate"]
                    prices_by_month[month] = round(price, 2)
                except Exception as e:
                    logging.warning(f"Error al obtener datos de {dt.strftime('%d-%m-%Y')}: {e}")
                    prices_by_month[month] = None

    return prices_by_month

async def historico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Por favor, usa el comando correctamente: /historico 2020")
        return

    year = int(context.args[0])
    if year < 2013 or year > datetime.now().year:
        await update.message.reply_text("Por favor ingresa un año válido entre 2013 y el año actual.")
        return

    await update.message.reply_text(f"📊 Consultando precios históricos de BTC en {year}...")

    prices = await get_monthly_prices_lcw(year)

    mensaje = f"📈 Precio de BTC (día 15 de cada mes) en {year}:\n\n"
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    for i in range(1, 13):
        precio = prices.get(i)
        if precio:
            mensaje += f"{meses[i-1]}: ${precio:,.2f}\n"
        else:
            mensaje += f"{meses[i-1]}: Sin datos\n"

    await update.message.reply_text(mensaje)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("historico", historico))

    print("Bot corriendo...")
    app.run_polling()
