import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yfinance as yf
from datetime import datetime

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = '7215806088:AAHsLeDCOIhU89jJTemHQ8XgKLYOYmhXZgM'  # ← Reemplaza con tu token real

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy el bot de históricos de Bitcoin.\n\n"
        "Usa el comando /historico seguido de un año (ej: /historico 2020) para ver el precio más alto de BTC cada mes según Yahoo Finance."
    )

# Comando /historico <año>
async def historico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Usa el comando así: /historico 2020")
        return

    anio = int(context.args[0])
    if anio < 2010 or anio > datetime.now().year:
        await update.message.reply_text("Por favor elige un año entre 2010 y el actual.")
        return

    await update.message.reply_text(f"🔍 Buscando precios máximos mensuales de BTC en {anio} desde Yahoo Finance...")

    try:
        btc = yf.Ticker("BTC-USD")
        hist = btc.history(start=f"{anio}-01-01", end=f"{anio}-12-31", interval="1mo")

        if hist.empty:
            await update.message.reply_text(f"No se encontraron datos para el año {anio}.")
            return

        mensaje = f"📈 Precio más alto de BTC en {anio} (por mes):\n\n"
        for index, row in hist.iterrows():
            mes = index.strftime('%B')
            precio_alto = row['High']
            mensaje += f"{mes}: ${precio_alto:,.2f}\n"

        await update.message.reply_text(mensaje)

    except Exception as e:
        await update.message.reply_text(f"Ocurrió un error al obtener los datos: {e}")

# Main
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("historico", historico))
    print("Bot corriendo...")
    app.run_polling()
