import os
import subprocess
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

DUMPS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dumps')
DB_NAME = os.environ.get('DB_NAME', 'autoria-scraper')
DB_USER = os.environ.get('HOST_USERNAME', 'postgres')
DB_PASSWORD = os.environ.get('HOST_PASSWORD', '123')
DB_HOST = os.environ.get('HOST_NAME', 'localhost')
DB_PORT = os.environ.get('HOST_PORT', '5432')

os.makedirs(DUMPS_DIR, exist_ok=True)

def make_dump():
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    dump_path = os.path.join(DUMPS_DIR, f"dump_{now}.sql")
    env = os.environ.copy()
    env['PGPASSWORD'] = DB_PASSWORD
    cmd = [
        'pg_dump',
        '-h', DB_HOST,
        '-p', DB_PORT,
        '-U', DB_USER,
        '-F', 'c',
        '-b',
        '-v',
        '-f', dump_path,
        DB_NAME
    ]
    try:
        subprocess.run(cmd, check=True, env=env)
        print(f"Дамп БД збережено: {dump_path}")
    except Exception as e:
        print(f"Помилка дампу БД: {e}")

async def schedule_db_dump():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(make_dump, 'cron', hour=12, minute=0)
    scheduler.start()
    print("Планувальник дампу БД запущено (щодня о 12:00)")

if __name__ == "__main__":
    import asyncio
    asyncio.run(schedule_db_dump())
    # Тримати процес живим
    import time
    while True:
        time.sleep(3600)
