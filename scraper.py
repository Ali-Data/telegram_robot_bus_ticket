import requests
import datetime

# این بخش بدون تغییر باقی می‌ماند
CITY_CODES = {
    "تهران": 1,
    "اصفهان": 10,
    "شیراز": 6,
    "مشهد": 4,
    "یزد": 13,
    "رشت": 21,
    "بابل": 20, # بابل را به لیست اضافه می‌کنیم
}

def find_tickets(origin_name: str, destination_name: str, date_str: str):
    """
    با استفاده از API سفر۷۲۴، بلیط‌ها را جستجو می‌کند.
    این نسخه برای کار با ساختار JSON جدید آپدیت شده است.
    """
    origin_code = CITY_CODES.get(origin_name)
    destination_code = CITY_CODES.get(destination_name)

    if not origin_code or not destination_code:
        return "متاسفانه کد یکی از شهرهای مبدا یا مقصد یافت نشد."

    # این بخش برای سادگی بدون تغییر باقی می‌ماند
    parts = date_str.split()
    day = parts[0]
    month_map = {"شهریور": "06"}
    month = month_map.get(parts[1], "00")
    year = "1404"
    formatted_date = f"{year}/{month}/{day}"

    api_url = (f"https://api.safar724.com/api/v1/bus/getservices?"
               f"origin={origin_code}&destination={destination_code}&date={formatted_date}")
    
    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        # --- بخش اصلی تغییرات اینجاست ---
        
        # ۱. بررسی می‌کنیم که کلید 'items' در پاسخ وجود داشته باشد و خالی نباشد
        if "items" in data and data["items"]:
            available_tickets = data["items"]
            
            result_message = f"نتایج یافت شده برای {origin_name} به {destination_name} در تاریخ {formatted_date}:\n\n"
            
            # ۲. در لیست 'items' حلقه می‌زنیم و از کلیدهای جدید استفاده می‌کنیم
            for ticket in available_tickets[:5]: # فقط ۵ نتیجه اول
                result_message += (
                    f"🚌 شرکت: {ticket['companyPersianName']}\n"
                    f"⏰ ساعت حرکت: {ticket['departureTime']}\n"
                    # ۳. قیمت همچنان تقسیم بر ۱۰ می‌شود تا به تومان تبدیل شود
                    f"💰 قیمت: {int(ticket['price'] / 10):,} تومان\n"
                    f"📍 ترمینال مبدا: {ticket['originTerminalPersianName']}\n"
                    "--------------------\n"
                )
            return result_message
        else:
            # اگر کلید 'items' وجود نداشت یا خالی بود
            return f"متاسفانه در تاریخ {formatted_date} هیچ بلیطی از {origin_name} به {destination_name} یافت نشد."

    except requests.exceptions.RequestException as e:
        print(f"خطا در اتصال به API: {e}")
        return "خطا در اتصال به سرور جستجو. لطفاً لحظاتی دیگر دوباره تلاش کنید."
    except ValueError: # اگر پاسخ JSON معتبر نباشد
        return "پاسخ دریافت شده از سرور معتبر نبود. ممکن است سایت در حال بروزرسانی باشد."


# این بخش برای تست مستقیم خود اسکریپت است
if __name__ == '__main__':
    # تست عملکرد تابع با شهرهای جدید
    test_result = find_tickets("تهران", "بابل", "28 شهریور")
    print(test_result)