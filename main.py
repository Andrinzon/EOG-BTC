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

# Símbolos soportados
SYMBOLS = {
    'btc': 'BTC-USD',
    'eth': 'ETH-USD',
    'bnb': 'BNB-USD',
    'sol': 'SOL-USD',
    'ada': 'ADA-USD'
}

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy el bot de históricos de criptomonedas.\n\n"
        "Comandos disponibles:\n"
        "🔼 /historico <cripto> <año> → Precios máximos mensuales\n"
        "🔽 /minimos <cripto> <año> → Precios mínimos mensuales\n\n"
        "Ejemplos:\n"
        "/historico btc 2020\n"
        "/minimos eth 2021\n\n"
        "Criptos soportadas: BTC, ETH, BNB, SOL, ADA"
    )

# Función general para obtener históricos
async def obtener_historico(update: Update, context: ContextTypes.DEFAULT_TYPE, tipo='max'):
    if len(context.args) != 2:
        await update.message.reply_text(f"Usa el comando así: /{'historico' if tipo == 'max' else 'minimos'} btc 2020")
        return

    moneda = context.args[0].lower()
    anio = context.args[1]

    if moneda not in SYMBOLS:
        await update.message.reply_text("Cripto no soportada. Usa: btc, eth, bnb, sol, ada")
        return

    if not anio.isdigit() or int(anio) < 2010 or int(anio) > datetime.now().year:
        await update.message.reply_text("Por favor elige un año entre 2010 y el actual.")
        return

    await update.message.reply_text(
        f"🔍 Buscando precios {'máximos' if tipo == 'max' else 'mínimos'} mensuales de {moneda.upper()} en {anio} desde Yahoo Finance..."
    )

    try:
        ticker = SYMBOLS[moneda]
        hist = yf.Ticker(ticker).history(start=f"{anio}-01-01", end=f"{anio}-12-31", interval="1mo")

        if hist.empty:
            await update.message.reply_text(f"No se encontraron datos para {moneda.upper()} en {anio}.")
            return

        mensaje = f"📉 Precio {'más alto' if tipo == 'max' else 'más bajo'} de {moneda.upper()} en {anio} (por mes):\n\n"
        for index, row in hist.iterrows():
            mes = index.strftime('%B')
            precio = row['High'] if tipo == 'max' else row['Low']
            mensaje += f"{mes}: ${precio:,.2f}\n"

        await update.message.reply_text(mensaje)

    except Exception as e:
        await update.message.reply_text(f"Ocurrió un error al obtener los datos: {e}")

# Comandos
async def historico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await obtener_historico(update, context, tipo='max')

async def minimos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await obtener_historico(update, context, tipo='min')

# Main
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("historico", historico))
    app.add_handler(CommandHandler("minimos", minimos))
    print("Bot corriendo...")
    app.run_polling()
