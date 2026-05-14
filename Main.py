import fal_client
import asyncio
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
FAL_KEY = os.getenv("FAL_KEY")
os.environ["FAL_KEY"] = FAL_KEY

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Photo lebuna 🔥 dan style eka type karapan. Eg: VIP neon, Racing")
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    await file.download_to_drive("input.jpg")
    context.user_data["waiting_for_prompt"] = True

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_prompt"):
        return
    prompt = update.message.text
    await update.message.reply_text("Video generate wenawa... 30s-1min yai ⏳")
    try:
        result = await fal_client.run_async(
            "fal-ai/kling-video/v1.5/standard/image-to-video",
            arguments={"image_url": await fal_client.upload_file("input.jpg"), "prompt": prompt, "duration": "5"}
        )
        await update.message.reply_video(result["video"]["url"], caption="Haduwa bn! 🔥")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
    context.user_data["waiting_for_prompt"] = False

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
