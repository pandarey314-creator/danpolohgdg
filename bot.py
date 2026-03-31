import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
FACEBOOK_PAGE_TOKEN = os.getenv("FACEBOOK_PAGE_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")

# ─────────────────────────────────────────────
# FACEBOOK
# ─────────────────────────────────────────────

def publicar_en_facebook(mensaje: str) -> str:
    if not FACEBOOK_PAGE_TOKEN or not FACEBOOK_PAGE_ID:
        return "❌ Faltan credenciales de Facebook. Configura FACEBOOK_PAGE_TOKEN y FACEBOOK_PAGE_ID en el archivo .env"

    url = f"https://graph.facebook.com/{FACEBOOK_PAGE_ID}/feed"
    data = {
        "message": mensaje,
        "access_token": FACEBOOK_PAGE_TOKEN
    }
    response = requests.post(url, data=data)
    result = response.json()

    if "id" in result:
        return f"✅ Publicado en Facebook correctamente.\nID del post: {result['id']}"
    else:
        error = result.get("error", {}).get("message", "Error desconocido")
        return f"❌ Error al publicar: {error}"

# ─────────────────────────────────────────────
# COMANDOS DEL BOT
# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hola! Soy tu asistente PandaRey Bot.\n\n"
        "📋 *Comandos disponibles:*\n"
        "/publicar [texto] - Publica en Facebook\n"
        "/estado - Ver estado del bot\n"
        "/ayuda - Ver todos los comandos\n\n"
        "También puedes escribirme directamente y te respondo.",
        parse_mode="Markdown"
    )

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 *Comandos disponibles:*\n\n"
        "*/publicar [texto]* - Publica un mensaje en tu página de Facebook\n"
        "Ejemplo: `/publicar Hola mundo desde mi bot!`\n\n"
        "*/estado* - Ver si el bot está funcionando\n\n"
        "*/ayuda* - Ver esta lista de comandos",
        parse_mode="Markdown"
    )

async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fb_estado = "✅ Configurado" if FACEBOOK_PAGE_TOKEN and FACEBOOK_PAGE_ID else "❌ Sin configurar"
    await update.message.reply_text(
        f"🤖 *Estado del bot:*\n\n"
        f"Telegram: ✅ Activo\n"
        f"Facebook: {fb_estado}",
        parse_mode="Markdown"
    )

async def publicar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "⚠️ Debes escribir el mensaje a publicar.\n"
            "Ejemplo: `/publicar Hola mundo!`",
            parse_mode="Markdown"
        )
        return

    mensaje = " ".join(context.args)
    await update.message.reply_text(f"📤 Publicando en Facebook...")
    resultado = publicar_en_facebook(mensaje)
    await update.message.reply_text(resultado)

async def mensaje_libre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()

    if "publicar" in texto or "facebook" in texto:
        await update.message.reply_text(
            "Para publicar en Facebook usa:\n`/publicar tu mensaje aqui`",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"Recibido: *{update.message.text}*\n\nUsa /ayuda para ver los comandos disponibles.",
            parse_mode="Markdown"
        )

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("🚀 Iniciando PandaRey Bot...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("estado", estado))
    app.add_handler(CommandHandler("publicar", publicar))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_libre))

    print("✅ Bot activo. Esperando mensajes en Telegram...")
    app.run_polling()

if __name__ == "__main__":
    main()
