from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from config import ADMIN_IDS

router = Router()


@router.message(Command("start", "help"))
async def cmd_help(message: Message):
    is_admin = message.from_user.id in ADMIN_IDS
    base_text = (
        "🎮 <b>Помічник клубу Brawl Stars</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📊 <b>ОПИТУВАННЯ</b>\n"
        "/newpoll — створити нове опитування 🔒\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🎯 <b>ЦІЛІ КЛУБУ</b>\n"
        "/goals — переглянути цілі клубу\n"
        "/addgoal — додати нову ціль 🔒\n"
        "/completegoal — позначити ціль виконаною 🔒\n"
        "/cleargoals — видалити виконані цілі 🔒\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>МЕГАКОПІЛКА</b>\n"
        "/megastart [назва] — почати мегакопілку 🔒\n"
        "/megaend — завершити мегакопілку 🔒\n"
        "/megastatus — статус мегакопілки\n"
        "/megahistory — історія мегакопілок\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔒 — тільки для адміністраторів\n\n"
        "⏰ Щоденне опитування надсилається автоматично о 13:00!"
    )

    if is_admin:
        base_text += "\n\n👑 <i>Ви маєте права адміністратора.</i>"

    await message.reply(base_text, parse_mode="HTML")


@router.message(Command("adminlist"))
async def cmd_admin_list(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("⛔ Тільки для адміністраторів.")
        return
    ids_str = "\n".join(f"• <code>{aid}</code>" for aid in ADMIN_IDS)
    await message.reply(
        f"👑 <b>Адміністратори бота:</b>\n{ids_str}",
        parse_mode="HTML"
    )
