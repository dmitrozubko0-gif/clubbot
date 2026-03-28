from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from config import GROUP_CHAT_ID, DAILY_POLL_HOUR, DAILY_POLL_MINUTE


# ──────────────────────────────────────────
#  Щоденне автоматичне опитування о 13:00
# ──────────────────────────────────────────

DAILY_POLL_QUESTION = "🎮 Як пройшов ваш Brawl Stars сьогодні?"
DAILY_POLL_OPTIONS = [
    "🔥 Відмінно, багато перемог!",
    "😎 Нормально, є прогрес",
    "😐 Так собі, важкувато",
    "💀 Жах, самі поразки",
    "😴 Ще не грав(а)",
]


async def send_daily_poll(bot: Bot):
    """Надіслати щоденне опитування у групу."""
    try:
        await bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text="⏰ <b>Щоденне опитування клубу!</b>",
            parse_mode="HTML"
        )
        await bot.send_poll(
            chat_id=GROUP_CHAT_ID,
            question=DAILY_POLL_QUESTION,
            options=DAILY_POLL_OPTIONS,
            is_anonymous=False,
            allows_multiple_answers=False,
        )
    except Exception as e:
        print(f"[ERROR] Помилка надсилання щоденного опитування: {e}")


def schedule_daily_poll(scheduler: AsyncIOScheduler, bot: Bot):
    """Зареєструвати щоденне опитування у планувальнику."""
    scheduler.add_job(
        send_daily_poll,
        trigger="cron",
        hour=DAILY_POLL_HOUR,
        minute=DAILY_POLL_MINUTE,
        args=[bot],
        id="daily_poll",
        replace_existing=True,
    )
    print(f"[SCHEDULER] Щоденне опитування о {DAILY_POLL_HOUR:02d}:{DAILY_POLL_MINUTE:02d} зареєстровано.")
