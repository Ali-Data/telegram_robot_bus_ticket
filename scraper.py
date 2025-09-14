import requests

# --- بخش جدید: تابع تبدیل اعداد ---
def convert_persian_to_english_numerals(text: str) -> str:
    """یک رشته ورودی می‌گیرد و اعداد فارسی آن را به انگلیسی تبدیل می‌کند."""
    persian_numerals = '۰۱۲۳۴۵۶۷۸۹'
    english_numerals = '0123456789'
    translation_table = str.maketrans(persian_numerals, english_numerals)
    return text.translate(translation_table)
# ------------------------------------

PERSIAN_TO_ENGLISH_CITIES = {
    "تهران": "tehran", "اصفهان": "isfahan", "شیراز": "shiraz",
    "مشهد": "mashhad", "یزد": "yazd", "رشت": "rasht", "بابل": "babol",
    "ساری": "sari","آمل": "amol","قائمشهر": "qaemshahr",
    "همدان": "hamadan","بابلسر":"babolsar","کاشان":"kashan",
    "آران":"aranvabidgol","آران و بیدگل":"aranvabidgol","بیدگل":"aranvabidgol"
}

PERSIAN_MONTHS = {
    "فروردین": "01", "اردیبهشت": "02", "خرداد": "03", "تیر": "04", 
    "مرداد": "05", "شهریور": "06", "مهر": "07", "آبان": "08", 
    "آذر": "09", "دی": "10", "بهمن": "11", "اسفند": "12",
}

def find_tickets(origin_name: str, destination_name: str, date_str: str):
    origin_en = PERSIAN_TO_ENGLISH_CITIES.get(origin_name)
    destination_en = PERSIAN_TO_ENGLISH_CITIES.get(destination_name)

    if not origin_en or not destination_en:
        return f"متاسفانه شهر «{origin_name}» یا «{destination_name}» در لیست ما وجود ندارد."

    try:
        # --- تغییر اصلی اینجاست ---
        # ۱. ورودی کاربر را به تابع تبدیل اعداد می‌دهیم
        date_str_en = convert_persian_to_english_numerals(date_str)
        
        # ۲. بقیه کارها را با رشته تبدیل شده انجام می‌دهیم
        day, month_name = date_str_en.split()
        # ---------------------------
        
        month = PERSIAN_MONTHS[month_name]
        year = "1404"
        formatted_date = f"{year}-{month}-{day.zfill(2)}"
    except (ValueError, KeyError):
        return "فرمت تاریخ اشتباه است. لطفاً به صورت «روز ماه» وارد کنید (مثال: ۲۸ شهریور)."

    api_url = "https://service.safar724.com/buses/api/bus/route"
    params = {'Date': formatted_date, 'Destination': destination_en, 'Origin': origin_en}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        if "items" in data and data["items"]:
            available_tickets = data["items"]
            result_message = f"نتایج یافت شده برای {origin_name} به {destination_name} در تاریخ {formatted_date}:\n\n"
            for ticket in available_tickets[:5]:
                result_message += (
                    f"🚌 شرکت: {ticket['companyPersianName']}\n"
                    f"⏰ ساعت حرکت: {ticket['departureTime']}\n"
                    f"💰 قیمت: {int(ticket['price'] / 10):,} تومان\n"
                    f"📍 ترمینال: {ticket['originTerminalPersianName']}\n"
                    f"نوع وسیله: {ticket['busType']}\n"
                    "--------------------\n"
                )
            return result_message
        else:
            return f"متاسفانه در تاریخ {formatted_date} هیچ بلیطی از {origin_name} به {destination_name} یافت نشد."

    except requests.exceptions.RequestException as e:
        print(f"خطا در اتصال به API: {e}")
        return "خطا در اتصال به سرور جستجو. لطفاً لحظاتی دیگر دوباره تلاش کنید."
    except ValueError:
        return "پاسخ دریافت شده از سرور معتبر نبود."

if __name__ == '__main__':
    test_result = find_tickets("تهران", "بابل", "۲۸ شهریور")
    print(test_result)