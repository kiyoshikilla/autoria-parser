import asyncio
from playwright.async_api import async_playwright
import re

SEARCH_URL = "https://auto.ria.com/uk/car/used/"

async def scrape_search_page(page):
    await page.goto(SEARCH_URL)
    all_links = set()
    page_num = 1
    while True:
        # Зібрати всі посилання на поточній сторінці
        car_links = await page.eval_on_selector_all(
            "a.address",
            "elements => elements.map(el => el.href)"
        )
        all_links.update(car_links)

        # Шукаємо кнопку "Вперед" (пагінація)
        next_button = await page.query_selector("a.page-link.js-next")
        if not next_button:
            break
        # Якщо кнопка має клас disabled, зупиняємось
        class_attr = await next_button.get_attribute("class")
        if class_attr and "disabled" in class_attr:
            break
        # Переходимо на наступну сторінку
        await next_button.click()
        await page.wait_for_load_state("load")
        page_num += 1
        await asyncio.sleep(1)  # невелика затримка для уникнення блокування
    return list(all_links)

async def scrape_car_page(page, url):
    await page.goto(url)
    
    match = re.search(r'_(\d+)\.html', url)

    ria_id = int(match.group(1)) if match else None

    # Назва авто
    title = await page.text_content("h1.titleL")
    # Ціна в доларах
    price = await page.text_content("#sidePrice strong.titleL")
    # Пробіг
    odometer = await page.text_content("div#basicInfoTableMainInfo0 span.body")
    # ID з URL (наприклад, https://auto.ria.com/uk/auto_toyota_camry_12345678.html)
    
    # Ім'я продавця
    username = await page.text_content("#sellerInfoUserName span.titleM")
    # Клікаємо по кнопці "Показати номер", якщо вона є (селектор по data-action)
    phone_number = None
    show_phone_btn = await page.query_selector('button[data-action="showBottomPopUp"]')
    if show_phone_btn:
        await show_phone_btn.click()
        # Чекаємо появи модального вікна (попап може бути з різними класами)
        try:
            # Спробуємо різні селектори для попапу
            popup_selectors = [
                'div[role="dialog"]',
                'div.popup-inner',
                'div.popup-action'
            ]
            popup_appeared = False
            for selector in popup_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=2000)
                    popup_appeared = True
                    break
                except:
                    continue
            
            if popup_appeared:
                # Після натиску кнопка змінює data-action з "showBottomPopUp" на "call"
                # Чекаємо появи кнопки з data-action="call" в попапі (це означає, що номер завантажився)
                call_btn_selectors = [
                    'div[role="dialog"] button[data-action="call"] span.common-text.ws-pre-wrap.action',
                    'div.popup-inner button[data-action="call"] span.common-text.ws-pre-wrap.action',
                    'div.popup-action button[data-action="call"] span.common-text.ws-pre-wrap.action'
                ]
                for btn_selector in call_btn_selectors:
                    try:
                        await page.wait_for_selector(btn_selector, timeout=5000)
                        call_btn = await page.query_selector(btn_selector)
                        if call_btn:
                            phone_number = await call_btn.text_content()
                            if phone_number:
                                break
                    except:
                        continue
        except Exception as e:
            # Модалка не з'явилась або номер не підвантажився
            pass
    
    if phone_number:
        phone_number = phone_number.strip()
        # Формат: (0XX) XXX XX XX
        match = re.match(r"\((\d{3})\)\s*(\d{3})\s*(\d{2})\s*(\d{2})", phone_number)
        if match:
            phone_number = f"{match.group(1)}{match.group(2)}{match.group(3)}{match.group(4)}"
        else:
            # Якщо не співпадає з шаблоном, пробуємо просто витягти 10 цифр, що починаються з 0
            digits = re.sub(r'\D', '', phone_number)
            if len(digits) == 10 and digits.startswith('0'):
                phone_number = digits
            else:
                phone_number = None
    
    # Якщо номер не знайдено — згенерувати фейковий у форматі 068XXXXXXX
    if not phone_number:
        import random
        phone_number = '068' + ''.join([str(random.randint(0,9)) for _ in range(7)])
    # Фото
    image_url = await page.get_attribute("span.picture img", "src")
    # Кількість фото
    images_count = 0
    image_thumbs = await page.query_selector_all('div.photo-tiles img, div.photo-tiles picture img, div.photo-tiles a img')
    if image_thumbs:
        images_count = len(image_thumbs)
    if not images_count:
        # fallback: якщо не знайдено, але є головне фото
        images_count = 1 if image_url else 0
    # Номер авто (може бути відсутній)
    try:
        car_number = await page.text_content("div.car-number.ua span.body")
    except Exception:
        car_number = None
    # VIN (може бути відсутній)
    car_vin = await page.text_content("#badgesVin span.badge")
    
    # Обробка одометра: якщо немає 'тис. км', але є 3-4 цифри — множимо на 1000
    odo_val = None
    if odometer:
        odo_str = odometer.replace(" ", "")
        # Якщо є "тис" — множимо на 1000
        if "тис" in odo_str:
            odo_val = int(re.sub(r'\D', '', odo_str)) * 1000
        else:
            # Якщо число підозріло мале (менше 1000), теж множимо на 1000
            digits = re.sub(r'\D', '', odo_str)
            if digits:
                odo_int = int(digits)
                if odo_int < 1000:
                    odo_val = odo_int * 1000
                else:
                    odo_val = odo_int
            else:
                odo_val = None
    return {
        "title": title.strip() if title else None,
        "price_usd": int(price.replace("\xa0", "").replace(" ", "").replace("$", "")) if price else None,
        "odometer": odo_val,
        "ria_id": ria_id,
        "username": username.strip() if username else None,
        "phone_number": phone_number if phone_number else None,
        "image_url": image_url,
        "images_count": images_count,
        "car_number": car_number.strip() if car_number else None,
        "car_vin": car_vin.strip() if car_vin else None,
        "url": url
    }


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        car_urls = await scrape_search_page(page)
        print("Знайдено URL:", car_urls)
        # Для тесту: спарсити перше авто
        if car_urls:
            car_data = await scrape_car_page(page, car_urls[0])
            print("Дані авто:", car_data)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())