import logging
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler, # <-- جدید: برای مدیریت گفتگو
)

# توکن ربات از متغیرهای محیطی خوانده می‌شود
TELEGRAM_API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')


# فعال کردن لاگ‌گیری
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- بخش جدید: تعریف مراحل (States) گفتگو ---
# ما مراحل گفتگو را با اعداد نام‌گذاری می‌کنیم تا مدیریت آن‌ها ساده باشد
ORIGIN, DESTINATION, START_DATE, END_DATE = range(4)
# ------------------------------------------------

# این تابع زمانی اجرا می‌شود که کاربر دستور /start را بفرستد
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f'سلام {user.mention_html()}! 👋\n\n'
        f'من ربات جستجوی بلیط اتوبوس هستم. برای شروع یک جستجوی جدید، دستور /search را بفرست.'
    )

# --- توابع جدید برای مدیریت گفتگوی جستجو ---

# مرحله ۱: شروع گفتگو با دستور /search
async def search_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """گفتگو را شروع می‌کند و مبدا را می‌پرسد."""
    await update.message.reply_text(
        'جستجوی جدید شروع شد. لطفاً نام شهر مبدا را وارد کنید:'
    )
    # به ربات می‌گوییم که منتظر پاسخ برای مرحله بعدی (مبدا) باشد
    return ORIGIN

# مرحله ۲: دریافت مبدا و پرسیدن مقصد
async def origin_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مبدا را ذخیره می‌کند و مقصد را می‌پرسد."""
    # پاسخ کاربر را در یک حافظه موقت (context.user_data) ذخیره می‌کنیم
    context.user_data['origin'] = update.message.text
    logger.info(f"مبدا: {context.user_data['origin']}")
    
    await update.message.reply_text('عالی! حالا نام شهر مقصد را وارد کنید:')
    # به مرحله بعدی (مقصد) می‌رویم
    return DESTINATION

# مرحله ۳: دریافت مقصد و پرسیدن تاریخ شروع
async def destination_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مقصد را ذخیره می‌کند و تاریخ شروع را می‌پرسد."""
    context.user_data['destination'] = update.message.text
    logger.info(f"مقصد: {context.user_data['destination']}")
    
    await update.message.reply_text('متشکرم. حالا تاریخ شروع بازه را وارد کنید (مثال: ۲۸ شهریور):')
    return START_DATE

# مرحله ۴ (پایانی): دریافت تاریخ شروع و پایان
async def start_date_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تاریخ شروع را ذخیره می‌کند و گفتگو را تمام می‌کند."""
    context.user_data['start_date'] = update.message.text
    logger.info(f"تاریخ شروع: {context.user_data['start_date']}")
    
    origin = context.user_data['origin']
    destination = context.user_data['destination']
    start_date = context.user_data['start_date']
    
    # در اینجا باید منطق جستجوی واقعی را اضافه کنیم
    # فعلا فقط اطلاعات دریافتی را به کاربر نمایش می‌دهیم
    await update.message.reply_text(
        f'بسیار خب! درخواست شما ثبت شد:\n'
        f'🔍 **مبدا:** {origin}\n'
        f'🎯 **مقصد:** {destination}\n'
        f'📅 **از تاریخ:** {start_date}\n\n'
        'در حال حاضر قابلیت جستجوی واقعی فعال نیست، اما به زودی اضافه خواهد شد!'
    )
    
    # حافظه موقت را پاک می‌کنیم
    context.user_data.clear()
    # به ربات می‌گوییم که گفتگو تمام شده است
    return ConversationHandler.END

# تابعی برای لغو گفتگو در هر مرحله
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """گفتگوی فعلی را لغو می‌کند."""
    await update.message.reply_text('عملیات لغو شد. برای شروع مجدد /search را بزنید.')
    context.user_data.clear()
    return ConversationHandler.END

# ------------------------------------------------

def main() -> None:
    if not TELEGRAM_API_TOKEN:
        print("خطا: توکن تلگرام در متغیرهای محیطی تعریف نشده است!")
        return
        
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()
    
    # --- بخش جدید: تعریف ConversationHandler ---
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('search', search_start)],
        states={
            ORIGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, origin_received)],
            DESTINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, destination_received)],
            START_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_date_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    # ----------------------------------------------
    
    # اضافه کردن Handler ها به اپلیکیشن
    application.add_handler(conv_handler) # <-- اضافه کردن Handler گفتگو
    application.add_handler(CommandHandler("start", start))

    print("ربات در حال اجراست...")
    application.run_polling()

if __name__ == '__main__':
    main()