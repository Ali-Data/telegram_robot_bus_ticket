import logging
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# --- بخش جدید: وارد کردن تابع خزنده ---
from scraper import find_tickets
# ------------------------------------

TELEGRAM_API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ORIGIN, DESTINATION, START_DATE = range(3) # <-- یک مرحله کمتر شده

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f'سلام {user.mention_html()}! 👋\n\n'
        f'برای جستجوی بلیط، دستور /search را بفرست.'
    )

async def search_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('جستجوی جدید شروع شد. لطفاً نام شهر مبدا را وارد کنید:')
    return ORIGIN

async def origin_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['origin'] = update.message.text
    await update.message.reply_text('عالی! حالا نام شهر مقصد را وارد کنید:')
    return DESTINATION

async def destination_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['destination'] = update.message.text
    await update.message.reply_text('متشکرم. حالا تاریخ مورد نظر را وارد کنید (مثال: ۲۸ شهریور):')
    return START_DATE

# --- بخش آپدیت شده: فراخوانی خزنده ---
async def start_date_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """اطلاعات نهایی را دریافت، خزنده را اجرا و نتیجه را ارسال می‌کند."""
    context.user_data['start_date'] = update.message.text
    
    origin = context.user_data['origin']
    destination = context.user_data['destination']
    start_date = context.user_data['start_date']
    
    # ۱. پیام "لطفا صبر کنید"
    await update.message.reply_text('در حال جستجو... لطفاً چند لحظه صبر کنید 🔎')
    
    # ۲. فراخوانی تابع خزنده
    results = find_tickets(origin, destination, start_date)
    
    # ۳. ارسال نتیجه به کاربر
    await update.message.reply_text(results)
    
    context.user_data.clear()
    return ConversationHandler.END
# --------------------------------------

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('عملیات لغو شد. برای شروع مجدد /search را بزنید.')
    context.user_data.clear()
    return ConversationHandler.END

def main() -> None:
    if not TELEGRAM_API_TOKEN:
        print("خطا: توکن تلگرام در متغیرهای محیطی تعریف نشده است!")
        return
        
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('search', search_start)],
        states={
            ORIGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, origin_received)],
            DESTINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, destination_received)],
            START_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_date_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))

    print("ربات در حال اجراست...")
    application.run_polling()

if __name__ == '__main__':
    main()