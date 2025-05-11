import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
ADMIN_ID = 8060554095
BOT_CHANNEL = "@eco_bonus_channel"

users = {}
referrals = {}

menu_buttons = ReplyKeyboardMarkup([
    ["📸 Rasm yuborish", "💰 Mening hisobim"],
    ["🏆 Top 10", "🎁 Referal havola"],
    ["ℹ️ Loyiha haqida", "📞 Admin bilan aloqa"],
    ["📱 Botning kanali", "💸 Pulni yechish"]
], resize_keyboard=True)

async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    args = context.args
    if user_id not in users:
        users[user_id] = 0
    if args and args[0].isdigit():
        inviter_id = int(args[0])
        if inviter_id in users and user_id != inviter_id and user_id not in referrals:
            users[inviter_id] += 5
            referrals[user_id] = inviter_id
    await update.message.reply_text(
        "♻️ Salom! Bizning Eco jamoamizga hush kelibsiz! "
        "Chiqindi tasdiqlash orqali sizga mukofotlar beriladi. Iltimos, chiqindini to‘g‘ri tashlagan rasmni yuboring!",
        reply_markup=menu_buttons
    )

async def button_handler(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = update.message.from_user.id
    if text == "📸 Rasm yuborish":
        await update.message.reply_text("Iltimos, chiqindini to‘g‘ri tashlagan rasmni yuboring.")
    elif text == "💰 Mening hisobim":
        await update.message.reply_text(f"💰 Sizda {users.get(user_id, 0)} Eco Ball mavjud.")
    elif text == "🏆 Top 10":
        sorted_users = sorted(users.items(), key=lambda x: x[1], reverse=True)[:10]
        msg = "🏆 Top 10 foydalanuvchilar:"
        for i, (uid, bal) in enumerate(sorted_users, 1):
            msg += f"{i}. 👤 {uid} - {bal} Eco Ball\n"
        await update.message.reply_text(msg)
    elif text == "🎁 Referal havola":
        ref_link = f"https://t.me/{context.bot.username}?start={user_id}"
        await update.message.reply_text(f"🎁 Sizning referal havolangiz: {ref_link}")
    elif text == "ℹ️ Loyiha haqida":
        await update.message.reply_text("♻️ Eco Bonus - chiqindi yig'ib, rasm yuborganlarga mukofot beriladi.")
    elif text == "📞 Admin bilan aloqa":
        await update.message.reply_text("📞 Admin: @farxod_biznes")
    elif text == "📱 Botning kanali":
        await update.message.reply_text(f"📱 Kanal: {BOT_CHANNEL}")
    elif text == "💸 Pulni yechish":
        balance = users.get(user_id, 0)
        if balance < 100000:
            await update.message.reply_text("❌ Kamida 100,000 Eco Ball kerak.")
        else:
            await update.message.reply_text("✅ Pulni yechish uchun admin bilan bog‘laning.")

async def verify_image(update: Update, context: CallbackContext):
    await update.message.reply_text("⚙️ Rasm tekshirilmoqda...")
    image = update.message.photo[-1].file_id
    file = await context.bot.get_file(image)
    file_url = file.file_path
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    data = {"inputs": file_url}
    response = requests.post("https://api-inference.huggingface.co/models/google/vit-base-patch16-224", headers=headers, json=data)
    result = response.json()
    if "trash" in str(result).lower():
        user_id = update.message.from_user.id
        users[user_id] = users.get(user_id, 0) + 2
        await update.message.reply_text("✅ Rasm tasdiqlandi! 2 Eco Ball qo‘shildi.")
    else:
        await update.message.reply_text("❌ Bu rasm chiqindi emas. Qayta urinib ko‘ring.")

if __name__ == "__main__":
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, verify_image))
    application.run_polling()
