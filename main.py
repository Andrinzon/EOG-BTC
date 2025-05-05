import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import aiohttp
from datetime import datetime

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = '7215806088:AAHsLeDCOIhU89jJTemHQ8XgKLYOYmhXZgM'  # Reemplaza esto por tu token real

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy el bot de históricos de Bitcoin.\n\n"
        "Usa el comando /historico seguido de un año (desde 2010 en adelante) para ver el precio mensual promedio de BTC.\n"
        "Ejemplo: /historico 2020"
    )

# Función para obtener precios históricos por mes usando la fecha 15 de cada mes
async def get_monthly_prices(year: int):
    url_base = "https://api.coingecko.com/api/v3/coins/bitcoin/history"
    prices_by_month = {}

    async with aiohttp.ClientSession() as session:
        for month in range(1, 13):
            date_str = f"15-{month:02d}-{year}"  # formato dd-mm-yyyy
            params = {"date": date_str, "localization": "false"}
            async with session.get(url_base, params=params) as response:
                data = await response.json()
                try:
                    price = data["market_data"]["current_price"]["usd"]
                    prices_by_month[month] = round(price, 2)
                except KeyError:
                    prices_by_month[month] = None

    return prices_by_month

# Comando /historico <año>
async def historico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Por favor, usa el comando correctamente: /historico 2020")
        return

    year = int(context.args[0])
    if year < 2010 or year > datetime.now().year:
        await update.message.reply_text("Por favor ingresa un año válido entre 2010 y el año actual.")
        return

    await update.message.reply_text(f"📊 Consultando precios históricos de BTC en {year}...")

    prices = await get_monthly_prices(year)

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

# Main
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("historico", historico))

    print("Bot corriendo...")
    app.run_polling()
