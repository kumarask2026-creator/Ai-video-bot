import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import replicate

# Logging සකස් කිරීම
logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey! Photo ekak yawapan, passe prompt ekak deka denna.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    # එකම වෙලාවක කිහිපදෙනෙක් photo එවූ විට මිශ්‍ර නොවීමට user_id එක නමට එකතු කර ඇත
    file_path = f"input_{user_id}.jpg"
    await file.download_to_drive(file_path)
    
    # Prompt එකක් එවන තෙක් බලා සිටින බව දැක්වීමට State එක සකසයි
    context.user_data["waiting_for_prompt"] = True
    
    await update.message.reply_text("Photo lebuna ✅ Dan prompt eka type karapan:\nRacing, Slowmo, etc.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_prompt"):
        return

    user_id = update.message.from_user.id
    file_path = f"input_{user_id}.jpg"

    # පරිශීලකයා කලින් photo එකක් එවා ඇත්දැයි පරික්ෂා කිරීම
    if not os.path.exists(file_path):
        await update.message.reply_text("Kalindata photo ekak yawala inna ⚠️")
        context.user_data["waiting_for_prompt"] = False
        return

    prompt = update.message.text
    await update.message.reply_text("Video hadanawa... 1-2 min yai ⏳")
    
    try:
        # Replicate API එක ක්‍රියාත්මක කිරීම
        output = replicate.run(
            "stability-ai/stable-video-diffusion",
            input={
                "image": open(file_path, "rb"),
                "prompt": prompt + ", smooth motion, cinematic",
                "num_frames": 25,
                "motion_bucket_id": 127
            }
        )
        
        # Output එක List එකක් ලෙස පැමිණියහොත් මුල්ම සබැඳිය (URL) ලබා ගැනීම
        video_url = output[0] if isinstance(output, list) else output
        
        # වීඩියෝව ටෙලිග්‍රෑම් වෙත යැවීම
        await update.message.reply_video(video=video_url)
        
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        
    finally:
        # වැඩේ අවසන් වූ පසු State එක reset කිරීම සහ ඉඩ ඉතිරි කරගැනීමට photo එක delete කිරීම
        context.user_data["waiting_for_prompt"] = False
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("Started polling")
    app.run_polling()
