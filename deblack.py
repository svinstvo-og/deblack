import os
import io
import logging
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# coniggggg
# not a real loken btw
TOKEN = "8410894634:AAFKYM7xazlu8nwG44w0MLgC4SdKtjVJIr"

#ids
ALLOWED_USER_IDS = {603056985} 

DEFAULT_TOLERANCE = 25
DEFAULT_REPLACEMENT = 50

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def process_image_in_memory(image_bytes: bytes, tolerance: int, replacement: int) -> io.BytesIO:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    pixels = img.load()
    width, height = img.size
    
    replacement_color = (replacement, replacement, replacement)

    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            if r <= tolerance and g <= tolerance and b <= tolerance:
                pixels[x, y] = replacement_color

    output_buffer = io.BytesIO()
    img.save(output_buffer, format="JPEG", quality=95)
    output_buffer.seek(0)
    return output_buffer

def parse_caption_params(caption: str):
    tol = DEFAULT_TOLERANCE
    rep = DEFAULT_REPLACEMENT
    
    if not caption:
        return tol, rep

    tokens = caption.split()
    for i, token in enumerate(tokens):
        if token == "/tolerance" and i + 1 < len(tokens):
            try:
                tol = int(tokens[i+1])
            except ValueError:
                pass
        elif token == "/replacement" and i + 1 < len(tokens):
            try:
                rep = int(tokens[i+1])
            except ValueError:
                pass
                
    return tol, rep

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ALLOWED_USER_IDS:
        logging.warning(f"Unauthorized access attempt from ID: {user_id}")
        return 

    if update.message.document:
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_name = "image.jpg"
    else:
        return

    caption = update.message.caption or ""
    tolerance, replacement = parse_caption_params(caption)

    status_msg = await update.message.reply_text(
        f"⏳ Downloading & Processing...\n"
        f"⚙️ Tolerance: {tolerance} | Replacement: {replacement}"
    )

    try:
        new_file = await context.bot.get_file(file_id)
        file_byte_array = await new_file.download_as_bytearray()

        processed_io = process_image_in_memory(bytes(file_byte_array), tolerance, replacement)

        await update.message.reply_document(
            document=processed_io,
            filename=f"fixed_{file_name}",
            caption="✅ Here is your printer-friendly image."
        )
        
        await status_msg.delete()

    except Exception as e:
        logging.error(f"Error processing image: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    image_filter = filters.PHOTO | filters.Document.IMAGE
    
    handler = MessageHandler(image_filter, handle_photo)
    application.add_handler(handler)

    print("🤖 Bot is running...")
    application.run_polling()