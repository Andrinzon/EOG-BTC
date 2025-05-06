import logging
import aiohttp
import yfinance as yf
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import asyncio

TOKEN = '7215806088:AAHsLeDCOIhU89jJTemHQ8XgKLYOYmhXZgM'


# Configuración del logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ===== FUNCIONES DEL BOT DE RIESGO Y RADAR (COINGECKO) =====

async def obtener_precio_btc():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return data["bitcoin"]["usd"]

async def calcular_riesgo_btc():
    precio_actual = await obtener_precio_btc()
    ATH = 105000
    distancia = precio_actual / ATH
    if distancia > 0.95:
        return 10
    elif distancia > 0.9:
        return 9
    elif distancia > 0.85:
        return 8
    elif distancia > 0.8:
        return 7
    elif distancia > 0.7:
        return 6
    elif distancia > 0.6:
        return 5
    elif distancia > 0.5:
        return 4
    elif distancia > 0.4:
        return 3
    elif distancia > 0.3:
        return 2
    else:
        return 1

async def riesgo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    precio = await obtener_precio_btc()
    riesgo = await calcular_riesgo_btc()
    await update.message.reply_text(f"💰 Precio BTC: ${precio:,.0f}\n⚠️ Nivel de riesgo: {riesgo}/10")

# ===== FUNCIONES HISTÓRICAS (YFINANCE) =====

async def historico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Uso: /historico <cripto> <año>\nEjemplo: /historico btc 2021")
            return

        simbolos = {
            "btc": "BTC-USD",
            "eth": "ETH-USD",
            "bnb": "BNB-USD",
            "sol": "SOL-USD",
            "ada": "ADA-USD"
        }

        cripto = args[0].lower()
        año = int(args[1])

        if cripto not in simbolos:
            await update.message.reply_text("Cripto no válida. Usa btc, eth, bnb, sol o ada.")
            return

        ticker = simbolos[cripto]
        inicio = f"{año}-01-01"
        fin = f"{año}-12-31"
        data = yf.download(ticker, start=inicio, end=fin, interval="1mo")

        if data.empty:
            await update.message.reply_text("No se encontraron datos.")
            return

        mensaje = f"📊 Histórico mensual de {cripto.upper()} - {año}\n\n"
        for fecha, fila in data.iterrows():
            mes = fecha.strftime("%B")
            maximo = fila['High']
            minimo = fila['Low']
            mensaje += f"{mes}: 📈 ${maximo:,.0f} / 📉 ${minimo:,.0f}\n"

        await update.message.reply_text(mensaje)

    except Exception as e:
        await update.message.reply_text("Error al obtener el histórico.")

# ===== MENÚ PRINCIPAL Y BOTONES =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚠️ Riesgo BTC", callback_data="riesgo")],
        [InlineKeyboardButton("📡 Radar de Oportunidades", callback_data="radar")],
        [InlineKeyboardButton("📊 Históricos", callback_data="historico_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Bienvenido al bot Ojo de Dios 👁‍🗨", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "riesgo":
        precio = await obtener_precio_btc()
        riesgo = await calcular_riesgo_btc()
        await query.edit_message_text(f"💰 Precio BTC: ${precio:,.0f}\n⚠️ Nivel de riesgo: {riesgo}/10")
    elif query.data == "radar":
        await query.edit_message_text("🔍 Analizando oportunidades...\n(Próximamente integrado con altcoins)")
    elif query.data == "historico_info":
        await query.edit_message_text("Usa el comando:\n/historico <cripto> <año>\nEjemplo:\n/historico btc 2021")

# ===== EJECUCIÓN DEL BOT =====

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("riesgo", riesgo))
    app.add_handler(CommandHandler("historico", historico))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot iniciado.")
    app.run_polling()
