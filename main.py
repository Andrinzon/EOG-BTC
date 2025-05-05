import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import aiohttp

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = '7215806088:AAHsLeDCOIhU89jJTemHQ8XgKLYOYmhXZgM'  # Reemplaza esto con el token real de tu bot

# Función para /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy el bot de históricos de Bitcoin.\n\n"
        "Usa el comando /historico seguido de un año (desde 2010 en adelante) para ver el precio mensual promedio de BTC.\n"
        "Ejemplo: /historico 2020"
    )

# Función para obtener precios históricos por mes
async def get_historical_prices(year: int):
    url = f'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range'
    prices_by_month = {}

    async with aiohttp.ClientSession() as session:
        for month in range(1, 13):
            # Generar timestamps para inicio y fin del mes
            from datetime import datetime
            import calendar
            start_date = datetime(year, month, 1)
            end_day = calendar.monthrange(year, month)[1]
            end_date = datetime(year, month, end_day, 23, 59)

            from_ts = int(start_date.timestamp())
            to_ts = int(end_date.timestamp())

            params = {
                'vs_currency': 'usd',
                'from': from_ts,
                'to': to_ts
            }

            async with session.get(url, params=params) as response:
                data = await response.json()
                prices = [p[1] for p in data.get('prices', [])]
                if prices:
                    avg_price = sum(prices) / len(prices)
                    prices_by_month[month] = round(avg_price, 2)
                else:
                    prices_by_month[month] = None

    return prices_by_month

# Función para /historico <año>
async def historico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Por favor, usa el comando correctamente: /historico 2020")
        return

    year = int(context.args[0])
    if year < 2010 or year > 2025:
        await update.message.reply_text("Por favor ingresa un año válido entre 2010 y 2025.")
        return

    await update.message.reply_text(f"📊 Consultando precios históricos de BTC en {year}...")

    prices = await get_historical_prices(year)

    mensaje = f"📈 Precio promedio mensual de BTC en {year}:\n\n"
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
