import logging
import os # <-- این خط را اضافه کنید
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# توکن ربات از متغیرهای محیطی خوانده می‌شود
# دیگر توکن را مستقیم در کد نمی‌نویسیم
TELEGRAM_API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')

# بقیه کد بدون تغییر باقی می‌ماند...
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f'سلام {user.mention_html()}! 👋\n\n'
        f'من ربات جستجوی بلیط اتوبوس هستم. برای شروع یک جستجوی جدید، دستور /search را بفرست.'
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"پیام شما دریافت شد: {update.message.text}")

def main() -> None:
    # بررسی اینکه آیا توکن در محیط تعریف شده است یا نه
    if not TELEGRAM_API_TOKEN:
        print("خطا: توکن تلگرام در متغیرهای محیطی تعریف نشده است!")
        return
        
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("ربات در حال اجراست...")
    application.run_polling()

if __name__ == '__main__':
    main()