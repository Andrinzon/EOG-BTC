import logging
import yfinance as yf
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, CallbackQueryHandler
import datetime

# Configura logging
logging.basicConfig(level=logging.INFO)

# Función /start
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton("📡 Radar de Oportunidades", callback_data='radar')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👁 Bienvenido al bot de históricos.\n\nUsa /historico 2021 BTC o simplemente /historico 2021 para ver datos de BTC.\n\nHaz clic abajo para ver oportunidades:", reply_markup=reply_markup)

# Función /historico
async def historico(update: Update, context: CallbackContext) -> None:
    args = context.args
    if not args:
        await update.message.reply_text("❗ Usa el comando así: /historico 2021 BTC\nCriptos permitidas: BTC, BNB, ETH, SOL, ADA")
        return

    year = args[0]
    symbol = args[1].upper() if len(args) > 1 else "BTC"
    valid_symbols = {
        "BTC": "BTC-USD",
        "BNB": "BNB-USD",
        "ETH": "ETH-USD",
        "SOL": "SOL-USD",
        "ADA": "ADA-USD"
    }

    if symbol not in valid_symbols:
        await update.message.reply_text("❌ Cripto no válida. Usa: BTC, BNB, ETH, SOL o ADA.")
        return

    try:
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        data = yf.download(valid_symbols[symbol], start=start_date, end=end_date, interval="1mo")

        if data.empty:
            await update.message.reply_text(f"No se encontraron datos para {symbol} en {year}.")
            return

        mensaje = f"📊 Máximos mensuales de {symbol} en {year}:\n\n"
        for i, row in data.iterrows():
            mes = i.strftime('%B')
            precio = round(row['High'], 2)
            mensaje += f"{mes}: ${precio}\n"

        await update.message.reply_text(mensaje)
    except Exception as e:
        await update.message.reply_text("⚠️ Error al obtener datos. Intenta de nuevo.")
        logging.error(e)

# Función de radar de oportunidades
async def radar_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    mensaje = await analizar_oportunidades()
    await query.edit_message_text(mensaje)

async def analizar_oportunidades():
    monedas = {
        "BNB": "BNB-USD",
        "SOL": "SOL-USD",
        "ADA": "ADA-USD",
        "XRP": "XRP-USD"
    }

    mensaje = "📡 *Radar de Oportunidades*\n\n"
    for nombre, ticker in monedas.items():
        try:
            datos = yf.download(ticker, period="3mo", interval="1d")
            if datos.empty:
                mensaje += f"{nombre}: ❌ No hay datos.\n"
                continue

            precio_actual = round(datos["Close"][-1], 2)
            min_3m = round(datos["Close"].min(), 2)
            max_3m = round(datos["Close"].max(), 2)
            rango = max_3m - min_3m
            distancia_min = precio_actual - min_3m
            riesgo = round((distancia_min / rango) * 10, 1) if rango > 0 else 5

            if riesgo < 3:
                señal = "🟢 Cerca del mínimo"
            elif riesgo > 7:
                señal = "🔴 Cerca del máximo"
            else:
                señal = "🟡 Zona media"

            mensaje += f"{nombre}: ${precio_actual} | {señal} | Riesgo: {riesgo}/10\n"

        except Exception as e:
            mensaje += f"{nombre}: ⚠️ Error al analizar.\n"
            logging.error(e)

    return mensaje

# Main
if __name__ == "__main__":
    TOKEN = "7215806088:AAHsLeDCOIhU89jJTemHQ8XgKLYOYmhXZgM"  # Reemplaza con tu token
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("historico", historico))
    app.add_handler(CallbackQueryHandler(radar_callback, pattern="^radar$"))

    print("✅ Bot activo.")
    app.run_polling()
