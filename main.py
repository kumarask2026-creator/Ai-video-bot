import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import replicate

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey! Photo ekak yawapan, passe prompt ekak denna.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    await file.download_to_drive("input.jpg")
    
    await update.message.reply_text("Photo lebuna ✅ Dan prompt eka type karapan:\nRacing, Slowmo, etc")
    context.user_data["waiting_for_prompt"] = True

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_prompt"):
        return
    
    prompt = update.message.text
    await update.message.reply_text("Video hadanawa... 1-2 min yai ⏳")
    
    try:
        output = replicate.run(
                "stability-ai/stable-video-diffusion-img2vid:3f708dad6c394f359e5acfe3678d222d32b3e12c0fca4245cb87f23e3f6b8b",
    input={
                "image": open("input.jpg", "rb"),
                "prompt": prompt + ", smooth motion, cinematic",
                "num_frames": 25,
                "motion_bucket_id": 127
            }
        )
        await update.message.reply_video(output)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
    
    context.user_data["waiting_for_prompt"] = False

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("Started polling")
    app.run_polling()
