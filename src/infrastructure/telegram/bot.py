import logging
import asyncio
import os
import sys
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import re

from src.infrastructure.database.repository import FTTHRepository
from src.infrastructure.ai.ollama_client import OllamaClient
from src.core.services.network_service import NetworkService
from src.core.services.ai_service import AIService
from src.config.isp_config import get_config
from src.utils.plotting import generate_plot

# Cargar variables de entorno
load_dotenv()

# Configuración
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_CHAT_ID = int(os.getenv("TELEGRAM_AUTHORIZED_CHAT_ID", "0"))
DB_PATH = os.getenv("DB_PATH", "ftth_mantenimiento.db")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")

# Inicialización de servicios
repo = FTTHRepository(DB_PATH)
ai_client = OllamaClient(OLLAMA_URL, OLLAMA_MODEL)
network_service = NetworkService(repo)
ai_service = AIService(ai_client, repo)

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_CHAT_ID: return
    mensaje = (
        "🤖 *FiberMind Analytics - Bot Activo*\n\n"
        "Comandos disponibles:\n"
        "🔍 /auditar - Busca fallas críticas\n"
        "📊 /hilo [n] - Radiografía del hilo n\n"
    )
    await update.message.reply_text(mensaje, parse_mode='Markdown')

async def auditar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_CHAT_ID: return
    await update.message.reply_text("🔎 Ejecutando auditoría...")
    resultado = network_service.audit_critical_splices(0.2, id_cable=1)
    await update.message.reply_text(resultado[:4000])

async def hilo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_CHAT_ID: return
    if not context.args:
        await update.message.reply_text("Indica el número de hilo. Ej: /hilo 61")
        return

    try:
        id_hilo = int(context.args[0])
        await update.message.reply_text(f"📊 Buscando Hilo {id_hilo}...")
        
        resultado = network_service.get_hilo_radiography(1, id_hilo)
        
        # Generar gráfico
        img_path = generate_plot(1, id_hilo, f"trace_{id_hilo}.png", repo)
        
        if img_path and os.path.exists(img_path):
            with open(img_path, 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption=resultado)
            os.remove(img_path)
        else:
            await update.message.reply_text(resultado)
            
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_CHAT_ID: return
    
    text = update.message.text.lower()
    
    # Atajo para hilo
    match = re.search(r'hilo\s+(\d+)', text)
    if match:
        context.args = [match.group(1)]
        await hilo(update, context)
        return

    # IA Razonamiento
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    respuesta = await ai_service.process_question(update.message.text)
    await update.message.reply_text(respuesta, parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('auditar', auditar))
    app.add_handler(CommandHandler('hilo', hilo))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot de Telegram iniciado...")
    app.run_polling()
