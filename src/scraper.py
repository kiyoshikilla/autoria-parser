import asyncio
from playwright.async_api import async_playwright
import re

SEARCH_URL = "https://auto.ria.com/uk/car/used/"

async def scrape_search_page(page):
    await page.goto(SEARCH_URL)

    car_links = await page.eval_on_selector_all(
        "a.address",
        "elements => elements.map(el => el.href)"
    )
    return car_links

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
    # Телефон (може бути прихований, для прикладу — селектор)
    phone_number = await page.text_content("div.button-main span.action")
    # Фото
    image_url = await page.get_attribute("span.picture img", "src")
    # Номер авто (може бути відсутній)
    car_number = await page.text_content("div.car-number.ua span.body")
    # VIN (може бути відсутній)
    car_vin = await page.text_content("#badgesVin span.badge")
    
    return {
        "title": title.strip() if title else None,
        "price_usd": int(price.replace("\xa0", "").replace(" ", "").replace("$", "")) if price else None,
        "odometer": int(odometer.replace("тис. км", "").replace(" ", "")) if odometer else None,
        "ria_id": ria_id,
        "username": username.strip() if username else None,
        "phone_number": phone_number.strip() if phone_number else None,
        "image_url": image_url,
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