import requests

# ۱. دیکشنری جدید برای ترجمه نام فارسی شهر به انگلیسی
PERSIAN_TO_ENGLISH_CITIES = {
    "تهران": "tehran",
    "اصفهان": "isfahan",
    "شیراز": "shiraz",
    "مشهد": "mashhad",
    "یزد": "yazd",
    "رشت": "rasht",
    "بابل": "babol",
}

# دیکشنری برای ترجمه نام ماه فارسی به عدد
PERSIAN_MONTHS = {
    "فروردین": "01", "اردیبهشت": "02", "خرداد": "03",
    "تیر": "04", "مرداد": "05", "شهریور": "06",
    "مهر": "07", "آبان": "08", "آذر": "09",
    "دی": "10", "بهمن": "11", "اسفند": "12",
}

def find_tickets(origin_name: str, destination_name: str, date_str: str):
    """
    با استفاده از API جدید و صحیح سفر۷۲۴، بلیط‌ها را جستجو می‌کند.
    """
    # ۲. ترجمه نام شهرها به انگلیسی
    origin_en = PERSIAN_TO_ENGLISH_CITIES.get(origin_name)
    destination_en = PERSIAN_TO_ENGLISH_CITIES.get(destination_name)

    if not origin_en or not destination_en:
        return f"متاسفانه شهر «{origin_name}» یا «{destination_name}» در لیست ما وجود ندارد."

    # ۳. تبدیل تاریخ ورودی (مثال: "۲۸ شهریور") به فرمت YYYY-MM-DD
    try:
        day, month_name = date_str.split()
        month = PERSIAN_MONTHS[month_name]
        # سال را به صورت موقت ۱۴۰۴ در نظر می‌گیریم
        # در یک ربات واقعی، این بخش باید هوشمندتر باشد
        year = "1404"
        formatted_date = f"{year}-{month}-{day.zfill(2)}"
    except (ValueError, KeyError):
        return "فرمت تاریخ اشتباه است. لطفاً به صورت «روز ماه» وارد کنید (مثال: ۲۸ شهریور)."

    # ۴. ساخت URL نهایی با پارامترهای صحیح
    api_url = "https://service.safar724.com/buses/api/bus/route"
    params = {
        'Date': formatted_date,
        'Destination': destination_en,
        'Origin': origin_en
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    
    try:
        # ۵. ارسال درخواست با پارامترها (params)
        response = requests.get(api_url, params=params, headers=headers, timeout=20)
        response.raise_for_status()
        
        data = response.json()
        
        # این بخش parsing بدون تغییر باقی می‌ماند چون ساختار پاسخ یکی است
        if "items" in data and data["items"]:
            available_tickets = data["items"]
            
            result_message = f"نتایج یافت شده برای {origin_name} به {destination_name} در تاریخ {formatted_date}:\n\n"
            
            for ticket in available_tickets[:5]:
                result_message += (
                    f"🚌 شرکت: {ticket['companyPersianName']}\n"
                    f"⏰ ساعت حرکت: {ticket['departureTime']}\n"
                    f"💰 قیمت: {int(ticket['price'] / 10):,} تومان\n"
                    f"📍 ترمینال: {ticket['originTerminalPersianName']}\n"
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

# بخش تست
if __name__ == '__main__':
    test_result = find_tickets("تهران", "بابل", "28 شهریور")
    print(test_result)