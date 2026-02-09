import asyncio
from .scraper import scrape_search_page, scrape_car_page
from .database import AsyncSessionLocal, upsert_car, create_db
from playwright.async_api import async_playwright

WORKERS = 2

async def worker(queue, browser, session, user_agent):
    page = await browser.new_page(user_agent=user_agent)
    try:
        while True:
            url = await queue.get()
            try:
                car_data = await scrape_car_page(page, url)
                await upsert_car(car_data, session)
            except Exception as e:
                print(f"Помилка при обробці URL {url}: {e}")
            finally:
                queue.task_done()
            await asyncio.sleep(1)  # Затримка між запитами
    finally:
        await page.close()



async def main():
    await create_db()
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Тепер headless
        # Для отримання списку car_urls використовуємо окремий page
        page = await browser.new_page(user_agent=user_agent)
        car_urls = await scrape_search_page(page)
        await page.close()
        queue = asyncio.Queue()
        for url in car_urls:
            await queue.put(url)
        async with AsyncSessionLocal() as session:
            workers = [asyncio.create_task(worker(queue, browser, session, user_agent)) for _ in range(WORKERS)]
            await queue.join()
            for _ in workers:
                queue.put_nowait(None)  # Сигнал завершення воркерам
            await asyncio.gather(*workers, return_exceptions=True)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

