import json
import os
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from config import ADMIN_IDS

router = Router()

CUPS_FILE = "data/cups.json"


# ──────────────────────────────────────────
#  Утиліти
# ──────────────────────────────────────────

def load_cups() -> dict:
    if not os.path.exists(CUPS_FILE):
        return {"records": [], "personal": {}}
    with open(CUPS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("records", [])
    data.setdefault("personal", {})
    return data


def save_cups(data: dict):
    os.makedirs(os.path.dirname(CUPS_FILE), exist_ok=True)
    with open(CUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────
#  Команди
# ──────────────────────────────────────────

@router.message(Command("addrecord"))
async def cmd_add_record(message: Message):
    """/addrecord Дмитро 25000 — додати рекорд кубків для учасника"""
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("⛔ Тільки адміністратори можуть додавати рекорди.")
        return

    args = message.text.split()
    if len(args) < 3:
        await message.reply(
            "❌ Формат: <code>/addrecord Ім'я Кількість_кубків</code>\n"
            "Приклад: <code>/addrecord Дмитро 25000</code>",
            parse_mode="HTML"
        )
        return

    try:
        cups = int(args[-1])
        name = " ".join(args[1:-1])
    except ValueError:
        await message.reply("❌ Кількість кубків має бути числом.")
        return

    data = load_cups()
    personal = data["personal"]
    old_record = personal.get(name, 0)
    is_new_record = cups > old_record

    if is_new_record:
        personal[name] = cups
        record_text = "🏆 <b>НОВИЙ РЕКОРД!</b>"
    else:
        record_text = f"(рекорд: {old_record} 🏆)"

    save_cups(data)

    await message.reply(
        f"{record_text}\n\n"
        f"👤 <b>{name}</b>\n"
        f"🏆 Кубків: <b>{cups:,}</b>\n"
        f"{'📈 Покращено на ' + str(cups - old_record) + ' кубків!' if is_new_record and old_record > 0 else ''}",
        parse_mode="HTML"
    )


@router.message(Command("cups"))
async def cmd_cups(message: Message):
    """Показати рекорди кубків учасників клубу."""
    data = load_cups()
    personal = data.get("personal", {})

    if not personal:
        await message.reply(
            "🏆 <b>Рекорди кубків</b>\n\nЩе немає рекордів.\n"
            "Адмін може додати: <code>/addrecord Ім'я 25000</code>",
            parse_mode="HTML"
        )
        return

    sorted_members = sorted(personal.items(), key=lambda x: x[1], reverse=True)
    medals = ["🥇", "🥈", "🥉"]

    text = "🏆 <b>Рекорди кубків клубу</b>\n\n"
    for i, (name, cups) in enumerate(sorted_members, 1):
        medal = medals[i - 1] if i <= 3 else f"{i}."
        text += f"{medal} <b>{name}</b> — {cups:,} 🏆\n"

    await message.reply(text, parse_mode="HTML")


@router.message(Command("mycups"))
async def cmd_my_cups(message: Message):
    """/mycups Ім'я — переглянути рекорд конкретного учасника"""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "❌ Формат: <code>/mycups Ім'я</code>\n"
            "Приклад: <code>/mycups Дмитро</code>",
            parse_mode="HTML"
        )
        return

    name = args[1].strip()
    data = load_cups()
    cups = data["personal"].get(name)

    if cups is None:
        await message.reply(f"❌ Учасника <b>{name}</b> не знайдено в таблиці.", parse_mode="HTML")
        return

    await message.reply(
        f"👤 <b>{name}</b>\n🏆 Рекорд кубків: <b>{cups:,}</b>",
        parse_mode="HTML"
    )
