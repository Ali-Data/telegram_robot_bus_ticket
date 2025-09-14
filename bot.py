import logging
import os
import json
import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from scraper import find_tickets

# خواندن توکن‌ها و کلید از متغیرهای محیطی
TELEGRAM_API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# --- بخش جدید: تنظیم Gemini API ---
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash') # استفاده از مدل سریع و بهینه
else:
    print("خطا: کلید API Gemini در متغیرهای محیطی تعریف نشده است!")
    model = None
# ------------------------------------

# تنظیمات لاگ‌گیری
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پاسخ به دستور /start"""
    user = update.effective_user
    await update.message.reply_html(
        f'سلام {user.mention_html()}! 👋\n\n'
        'لطفاً درخواست سفر خود را در یک جمله برای من بنویسید. مثال:\n'
        '«میخوام ۲۸ شهریور از تهران برم بابل»'
    )

# --- تابع اصلی و جدید: پردازش زبان طبیعی ---
async def handle_natural_language_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """جمله کاربر را دریافت، با Gemini تحلیل و سپس جستجو می‌کند."""
    if not model:
        await update.message.reply_text("متاسفانه سرویس هوش مصنوعی در حال حاضر در دسترس نیست.")
        return

    user_text = update.message.text
    logger.info(f"درخواست کاربر: {user_text}")
    await update.message.reply_text("در حال تحلیل درخواست شما با هوش مصنوعی... لطفاً صبر کنید 🤔")

    # ساخت یک پرامپت (دستور) دقیق برای Gemini
    prompt = f"""
        از متن زیر، مبدا، مقصد و تاریخ را استخراج کن و فقط یک JSON معتبر برگردان.
        - مبدا باید کلید 'origin' باشد.
        - مقصد باید کلید 'destination' باشد.
        - تاریخ باید کلید 'date' و در فرمت "روز ماه" باشد. مثال: "۲۸ شهریور".
        - اگر اطلاعات ناقص بود، مقادیر مربوطه را null قرار بده.

        مثال ۱:
        ورودی: "میخوام ۲۸ شهریور از تهران برم بابل"
        خروجی: {{"origin": "تهران", "destination": "بابل", "date": "۲۸ شهریور"}}

        مثال ۲:
        ورودی: "بلیط مشهد به شیراز برای پس فردا میخوام"
        خروجی: {{"origin": "مشهد", "destination": "شیراز", "date": null}}
        
        متن برای تحلیل: "{user_text}"
        خروجی:
    """

    try:
        # ارسال درخواست به Gemini
        response = model.generate_content(prompt)
        # استخراج متن JSON از پاسخ
        # گاهی اوقات Gemini توضیحات اضافی می‌دهد، ما فقط بخش JSON را می‌خواهیم
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        
        logger.info(f"پاسخ خام از Gemini: {response.text}")
        logger.info(f"پاسخ JSON استخراج شده: {json_text}")

        # تبدیل متن JSON به دیکشنری پایتون
        search_data = json.loads(json_text)
        
        origin = search_data.get("origin")
        destination = search_data.get("destination")
        date = search_data.get("date")

        if not all([origin, destination, date]):
            await update.message.reply_text("متاسفانه نتوانستم تمام اطلاعات لازم (مبدا، مقصد و تاریخ) را از جمله شما استخراج کنم. لطفاً واضح‌تر بنویسید.")
            return

        # فراخوانی خزنده وب با اطلاعات استخراج شده
        await update.message.reply_text(f"عالی! در حال جستجوی بلیط از {origin} به {destination} برای تاریخ {date}...")
        results = find_tickets(origin, destination, date)
        await update.message.reply_text(results)

    except Exception as e:
        logger.error(f"خطا در پردازش با Gemini یا جستجو: {e}")
        await update.message.reply_text("متاسفانه در پردازش درخواست شما خطایی رخ داد. لطفاً دوباره تلاش کنید.")

def main() -> None:
    if not TELEGRAM_API_TOKEN:
        print("خطا: توکن تلگرام تعریف نشده است!")
        return
        
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()
    
    # تعریف دستورها: فقط /start و یک Handler برای تمام پیام‌های متنی
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_natural_language_search))

    print("ربات هوشمند در حال اجراست...")
    application.run_polling()

if __name__ == '__main__':
    main()