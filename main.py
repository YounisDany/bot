import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from instabot import Bot

# تعريف مراحل المحادثة
USERNAME, PASSWORD, PHOTO = range(3)

# قواميس لتخزين بيانات المستخدمين
user_data = {}

# دالة البداية
def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحباً! أرسل اسم المستخدم الخاص بإنستقرام.")
    return USERNAME

# دالة استقبال اسم المستخدم
def receive_username(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    user_data[user_id] = {"username": update.message.text}
    update.message.reply_text("شكراً! الآن أرسل كلمة المرور الخاصة بإنستقرام.")
    return PASSWORD

# دالة استقبال كلمة المرور
def receive_password(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    user_data[user_id]["password"] = update.message.text
    update.message.reply_text("تم حفظ البيانات! الآن يمكنك إرسال الصور ليتم رفعها على إنستقرام.")
    return PHOTO

# دالة معالجة الصور
def photo_handler(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    if user_id not in user_data or "username" not in user_data[user_id] or "password" not in user_data[user_id]:
        update.message.reply_text("الرجاء إدخال اسم المستخدم وكلمة المرور أولاً باستخدام /start.")
        return

    username = user_data[user_id]["username"]
    password = user_data[user_id]["password"]

    # إعداد بوت إنستقرام وتسجيل الدخول
    insta_bot = Bot()
    insta_bot.login(username=username, password=password)

    photo_file = update.message.photo[-1].get_file()
    file_path = f"./{photo_file.file_id}.jpg"
    photo_file.download(file_path)

    # رفع الصورة إلى إنستقرام
    insta_bot.upload_photo(file_path, caption="الوصف")
    update.message.reply_text("تم تحميل الصورة إلى إنستقرام بنجاح!")

# دالة إلغاء المحادثة
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("تم إلغاء العملية. إذا أردت المحاولة مرة أخرى، اكتب /start.")
    return ConversationHandler.END

def main():
    # إعداد البوت باستخدام التوكن الخاص بك مباشرة
    TELEGRAM_BOT_TOKEN = "6497472662:AAFDHsqNQQYICkJ9xA14vLMdBHauGy6v3h8"

    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # إعداد ConversationHandler لإدارة المحادثة
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USERNAME: [MessageHandler(Filters.text & ~Filters.command, receive_username)],
            PASSWORD: [MessageHandler(Filters.text & ~Filters.command, receive_password)],
            PHOTO: [MessageHandler(Filters.photo, photo_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # تشغيل البوت
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
