import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pega tu link 📥")

async def link_directo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("ey wey eso no es un link, resume la conversación enviando solo para lo que fui hecho (link) okey 🫶🏻🖕")
        return
    context.user_data['url'] = url
    keyboard = [[InlineKeyboardButton("🎬 Video (MP4)", callback_data="video"),
                 InlineKeyboardButton("🎵 Audio (MP3)", callback_data="audio")]]
    await update.message.reply_text("¿Qué querés descargar?", reply_markup=InlineKeyboardMarkup(keyboard))

async def boton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tipo = query.data
    url = context.user_data.get('url')
    if not url:
        await query.edit_message_text("❌ Link perdido, pegalo de nuevo.")
        return
    await query.edit_message_text("⏳ Descargando... espera")
    try:
        if tipo == 'audio':
            ydl_opts = {
                'outtmpl': '/tmp/%(title)s.%(ext)s',
                'format': 'bestaudio/best',
                'noplaylist': True,
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
            }
        else:
            ydl_opts = {
                'outtmpl': '/tmp/%(title)s.%(ext)s',
                'format': 'best[filesize<50M]/best',
                'noplaylist': True,
            }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        if tipo == 'audio':
            filename = os.path.splitext(filename)[0] + '.mp3'
        await query.edit_message_text("⬆️ Subiendo al chat...")
        with open(filename, 'rb') as f:
            if tipo == 'audio':
                await query.message.reply_audio(f)
            else:
                await query.message.reply_video(f)
        os.remove(filename)
        await query.edit_message_text("✅ Listo!")
    except Exception as e:
        await query.edit_message_text(f"❌ Error: {str(e)[:250]}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, link_directo))
    app.add_handler(CallbackQueryHandler(boton))
    print("🤖 Bot público iniciado!")
    app.run_polling()

if __name__ == '__main__':
    main()
