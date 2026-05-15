import replicate
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Photo ekak yawapan, passe Racing/Slowmo kiyala type karapan")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Photo lebuna ✅ Dan prompt eka type karapan: Racing, Slowmo, etc")
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    await file.download_to_drive("input.jpg")
    context.user_data["waiting_for_prompt"] = True

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_prompt"):
        return
    
    prompt = update.message.text
    await update.message.reply_text("Video hadanawa... 1-2 min yai ⏳")
    
    try:
        output = replicate.run(
            "stability-ai/stable-video-diffusion",
            input={
                "image": open("input.jpg", "rb"),
                "motion_bucket_id": 127,
                "fps": 6
            }
        )
        await update.message.reply_video(output)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
    
    context.user_data["waiting_for_prompt"] = False

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.COMMAND & filters.Regex("^/start$"), start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
