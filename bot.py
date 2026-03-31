import os
import subprocess
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
FACEBOOK_PAGE_TOKEN = os.getenv("FACEBOOK_PAGE_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
OWNER_ID = os.getenv("OWNER_ID")  # Tu ID de Telegram - solo tu puedes dar ordenes

directorio_actual = os.path.expanduser("~")  # Empieza en tu carpeta de usuario

# ─────────────────────────────────────────────
# SEGURIDAD: solo el dueño puede usar el bot
# ─────────────────────────────────────────────

def es_dueño(update: Update) -> bool:
    if not OWNER_ID:
        return True  # Si no hay OWNER_ID configurado, permite todo temporalmente
    return str(update.effective_user.id) == str(OWNER_ID)

# ─────────────────────────────────────────────
# EJECUTAR COMANDOS EN LA PC
# ─────────────────────────────────────────────

def ejecutar_comando(comando: str, directorio: str) -> str:
    try:
        result = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            cwd=directorio,
            timeout=30
        )
        salida = result.stdout or result.stderr or "✅ Comando ejecutado sin salida."
        if len(salida) > 3000:
            salida = salida[:3000] + "\n...(texto recortado)"
        return salida
    except subprocess.TimeoutExpired:
        return "⏱ Tiempo agotado (30 segundos)"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ─────────────────────────────────────────────
# FACEBOOK
# ─────────────────────────────────────────────

def publicar_en_facebook(mensaje: str) -> str:
    if not FACEBOOK_PAGE_TOKEN or not FACEBOOK_PAGE_ID:
        return "❌ Faltan credenciales de Facebook en el archivo .env"
    url = f"https://graph.facebook.com/{FACEBOOK_PAGE_ID}/feed"
    data = {"message": mensaje, "access_token": FACEBOOK_PAGE_TOKEN}
    response = requests.post(url, data=data)
    result = response.json()
    if "id" in result:
        return f"✅ Publicado en Facebook.\nID: {result['id']}"
    error = result.get("error", {}).get("message", "Error desconocido")
    return f"❌ Error: {error}"

# ─────────────────────────────────────────────
# COMANDOS
# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Hola! Soy tu asistente PandaRey Bot.\n"
        f"Tu ID de Telegram es: `{update.effective_user.id}`\n\n"
        f"📋 Comandos:\n"
        f"/cmd [comando] - Ejecutar comando en tu PC\n"
        f"/carpeta [nombre] - Crear carpeta\n"
        f"/archivos - Ver archivos del directorio actual\n"
        f"/donde - Ver directorio actual\n"
        f"/ir [ruta] - Cambiar directorio\n"
        f"/publicar [texto] - Publicar en Facebook\n"
        f"/estado - Ver estado\n"
        f"/miid - Ver tu ID de Telegram",
        parse_mode="Markdown"
    )

async def miid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Tu ID de Telegram es:\n`{update.effective_user.id}`\n\n"
        f"Copia este numero y ponlo en el archivo `.env` como:\n"
        f"`OWNER_ID={update.effective_user.id}`",
        parse_mode="Markdown"
    )

async def cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global directorio_actual
    if not es_dueño(update):
        await update.message.reply_text("⛔ No tienes permiso para usar este bot.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /cmd [comando]\nEjemplo: `/cmd dir`", parse_mode="Markdown")
        return
    comando = " ".join(context.args)
    await update.message.reply_text(f"⚙️ Ejecutando: `{comando}`", parse_mode="Markdown")
    resultado = ejecutar_comando(comando, directorio_actual)
    await update.message.reply_text(f"```\n{resultado}\n```", parse_mode="Markdown")

async def carpeta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global directorio_actual
    if not es_dueño(update):
        await update.message.reply_text("⛔ No tienes permiso.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /carpeta [nombre]\nEjemplo: `/carpeta MiProyecto`", parse_mode="Markdown")
        return
    nombre = " ".join(context.args)
    resultado = ejecutar_comando(f"mkdir \"{nombre}\"", directorio_actual)
    await update.message.reply_text(f"📁 Carpeta `{nombre}` creada en `{directorio_actual}`", parse_mode="Markdown")

async def archivos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global directorio_actual
    if not es_dueño(update):
        await update.message.reply_text("⛔ No tienes permiso.")
        return
    resultado = ejecutar_comando("dir", directorio_actual)
    await update.message.reply_text(f"📂 Contenido de `{directorio_actual}`:\n```\n{resultado}\n```", parse_mode="Markdown")

async def donde(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_dueño(update):
        await update.message.reply_text("⛔ No tienes permiso.")
        return
    await update.message.reply_text(f"📍 Directorio actual:\n`{directorio_actual}`", parse_mode="Markdown")

async def ir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global directorio_actual
    if not es_dueño(update):
        await update.message.reply_text("⛔ No tienes permiso.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /ir [ruta]\nEjemplo: `/ir C:\\Users\\TuUsuario\\Desktop`", parse_mode="Markdown")
        return
    nueva_ruta = " ".join(context.args)
    if os.path.isdir(nueva_ruta):
        directorio_actual = nueva_ruta
        await update.message.reply_text(f"✅ Ahora estas en:\n`{directorio_actual}`", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ La ruta `{nueva_ruta}` no existe.", parse_mode="Markdown")

async def publicar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_dueño(update):
        await update.message.reply_text("⛔ No tienes permiso.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /publicar [texto]\nEjemplo: `/publicar Hola mundo!`", parse_mode="Markdown")
        return
    mensaje = " ".join(context.args)
    await update.message.reply_text("📤 Publicando en Facebook...")
    resultado = publicar_en_facebook(mensaje)
    await update.message.reply_text(resultado)

async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fb = "✅ Configurado" if FACEBOOK_PAGE_TOKEN and FACEBOOK_PAGE_ID else "❌ Sin configurar"
    owner = "✅ Configurado" if OWNER_ID else "⚠️ Sin configurar (cualquiera puede usar el bot)"
    await update.message.reply_text(
        f"🤖 *Estado del bot:*\n\n"
        f"Telegram: ✅ Activo\n"
        f"Facebook: {fb}\n"
        f"Seguridad: {owner}\n"
        f"Directorio: `{directorio_actual}`",
        parse_mode="Markdown"
    )

async def mensaje_libre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_dueño(update):
        await update.message.reply_text("⛔ No tienes permiso.")
        return
    await update.message.reply_text(
        f"Usa /cmd para ejecutar comandos.\nEjemplo: `/cmd dir`\n\nEscribe /start para ver todos los comandos.",
        parse_mode="Markdown"
    )

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("🚀 Iniciando PandaRey Bot...")
    print(f"📂 Directorio inicial: {directorio_actual}")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("miid", miid))
    app.add_handler(CommandHandler("cmd", cmd))
    app.add_handler(CommandHandler("carpeta", carpeta))
    app.add_handler(CommandHandler("archivos", archivos))
    app.add_handler(CommandHandler("donde", donde))
    app.add_handler(CommandHandler("ir", ir))
    app.add_handler(CommandHandler("publicar", publicar))
    app.add_handler(CommandHandler("estado", estado))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_libre))

    print("✅ Bot activo. Esperando ordenes desde Telegram...")
    app.run_polling()

if __name__ == "__main__":
    main()
