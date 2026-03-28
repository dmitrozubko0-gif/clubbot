import json
import os
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from config import ADMIN_IDS

router = Router()

TOP_FILE = "data/top.json"

MEDALS = ["🥇", "🥈", "🥉"]


# ──────────────────────────────────────────
#  Утиліти
# ──────────────────────────────────────────

def load_top() -> dict:
    if not os.path.exists(TOP_FILE):
        return {}
    with open(TOP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_top(data: dict):
    os.makedirs(os.path.dirname(TOP_FILE), exist_ok=True)
    with open(TOP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────
#  Команди
# ──────────────────────────────────────────

@router.message(Command("addpoints"))
async def cmd_add_points(message: Message):
    """Додати очки активності учаснику. /addpoints @username 10"""
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("⛔ Тільки адміністратори можуть нараховувати очки.")
        return

    args = message.text.split()
    if len(args) < 3:
        await message.reply(
            "❌ Формат: <code>/addpoints Ім'я 10</code>\n"
            "Приклад: <code>/addpoints Дмитро 5</code>",
            parse_mode="HTML"
        )
        return

    try:
        points = int(args[-1])
        name = " ".join(args[1:-1])
    except ValueError:
        await message.reply("❌ Кількість очок має бути числом.")
        return

    data = load_top()
    if name not in data:
        data[name] = 0
    data[name] += points
    save_top(data)

    await message.reply(
        f"✅ <b>{name}</b> отримав(ла) <b>+{points}</b> очок активності!\n"
        f"Всього: <b>{data[name]}</b> очок 🌟",
        parse_mode="HTML"
    )


@router.message(Command("removepoints"))
async def cmd_remove_points(message: Message):
    """Зняти очки. /removepoints Ім'я 5"""
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("⛔ Тільки адміністратори.")
        return

    args = message.text.split()
    if len(args) < 3:
        await message.reply(
            "❌ Формат: <code>/removepoints Ім'я 5</code>",
            parse_mode="HTML"
        )
        return

    try:
        points = int(args[-1])
        name = " ".join(args[1:-1])
    except ValueError:
        await message.reply("❌ Кількість очок має бути числом.")
        return

    data = load_top()
    if name not in data:
        await message.reply(f"❌ Учасника <b>{name}</b> не знайдено.", parse_mode="HTML")
        return

    data[name] = max(0, data[name] - points)
    save_top(data)

    await message.reply(
        f"✅ У <b>{name}</b> знято <b>{points}</b> очок.\n"
        f"Залишок: <b>{data[name]}</b> очок",
        parse_mode="HTML"
    )


@router.message(Command("top"))
async def cmd_top(message: Message):
    """Показати топ активних учасників клубу."""
    data = load_top()

    if not data:
        await message.reply(
            "📊 <b>Топ активності клубу</b>\n\nЩе немає даних.\n"
            "Адмін може додати очки командою <code>/addpoints Ім'я 10</code>",
            parse_mode="HTML"
        )
        return

    sorted_members = sorted(data.items(), key=lambda x: x[1], reverse=True)

    text = "📊 <b>Топ активних учасників клубу</b>\n\n"
    for i, (name, points) in enumerate(sorted_members[:10], 1):
        medal = MEDALS[i - 1] if i <= 3 else f"{i}."
        text += f"{medal} <b>{name}</b> — {points} очок\n"

    await message.reply(text, parse_mode="HTML")


@router.message(Command("resetpoints"))
async def cmd_reset_points(message: Message):
    """Скинути всі очки."""
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("⛔ Тільки адміністратори.")
        return

    save_top({})
    await message.reply("🗑️ Таблицю активності скинуто!")
