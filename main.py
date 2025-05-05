import logging
import yfinance as yf
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import datetime

# Configura el log
logging.basicConfig(level=logging.INFO)

# --- Comando /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("📡 Radar de Oportunidades", callback_data="radar")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Bienvenido. Usa /historico seguido de un año y moneda para ver precios históricos mensuales.\n\n"
        "Ejemplo: `/historico 2021 BTC`\n\n"
        "También puedes usar el botón abajo para ver oportunidades.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# --- Comando /historico ---
async def historico(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 2:
        await update.message.reply_text("Uso correcto: /historico [año] [moneda]. Ej: /historico 2021 BTC")
        return

    año = context.args[0]
    moneda = context.args[1].upper()

    try:
        año_int = int(año)
        if año_int < 2010 or año_int > datetime.datetime.now().year:
            raise ValueError("Año inválido.")
    except ValueError:
        await update.message.reply_text("Año inválido. Ej: /historico 2020 BTC")
        return

    ticker = f"{moneda}-USD"
    try:
        datos = yf.download(ticker, start=f"{año}-01-01", end=f"{int(año)+1}-01-01", interval="1mo", progress=False)
        if datos.empty:
            await update.message.reply_text("No se encontraron datos para ese año y moneda.")
            return

        mensaje = f"📊 *Histórico mensual de {moneda} en {año}*\n\n"
        for fecha, fila in datos.iterrows():
            mes = fecha.strftime("%B")
            precio = round(fila["High"], 2)
            mensaje += f"{mes}: ${precio}\n"

        await update.message.reply_text(mensaje, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error en /historico: {str(e)}")
        await update.message.reply_text("Ocurrió un error al obtener los datos.")

# --- Radar de Oportunidades ---
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
            datos = yf.download(ticker, period="3mo", interval="1d", progress=False)
            if datos is None or datos.empty:
                mensaje += f"{nombre}: ❌ No se encontraron datos.\n"
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
            logging.error(f"Error analizando {nombre}: {str(e)}")
            mensaje += f"{nombre}: ⚠️ Error al analizar.\n"

    return mensaje

# --- Callback del botón del radar ---
async def radar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    mensaje = await analizar_oportunidades()
    await query.message.reply_text(mensaje, parse_mode="Markdown")

# --- Main ---
if __name__ == "__main__":
    import os
    TOKEN = os.getenv("7215806088:AAHsLeDCOIhU89jJTemHQ8XgKLYOYmhXZgM")  # Reemplaza esto si deseas fijar el token directamente

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("historico", historico))
    app.add_handler(CallbackQueryHandler(radar_callback, pattern="^radar$"))

    print("🤖 Bot activo.")
    app.run_polling()
