from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS, GROUP_CHAT_ID

router = Router()


def confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📢 Відправити", callback_data=f"send_yes_{action}"),
        InlineKeyboardButton(text="❌ Скасувати", callback_data=f"send_no_{action}"),
    ]])


# ──────────────────────────────────────────
#  /say — надіслати повідомлення від бота
# ──────────────────────────────────────────

class SayStates(StatesGroup):
    waiting_for_text = State()


@router.message(Command("say"))
async def cmd_say(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("⛔ Тільки адміністратори.")
        return
    await message.reply(
        "✍️ <b>Повідомлення у групу</b>\n\n"
        "Введіть текст який бот відправить у групу:",
        parse_mode="HTML"
    )
    await state.set_state(SayStates.waiting_for_text)


@router.message(SayStates.waiting_for_text)
async def say_text_received(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.clear()

    await message.reply(
        f"📋 <b>Попередній перегляд:</b>\n\n{message.text}\n\n―――――――――\nВідправити у групу?",
        parse_mode="HTML",
        reply_markup=confirm_keyboard("say")
    )
    # Зберігаємо текст у наступному повідомленні через callback_data недостатньо —
    # тому кешуємо у простому dict
    _pending_say[message.from_user.id] = message.text


# Тимчасове сховище тексту між FSM і callback
_pending_say: dict = {}


@router.callback_query(F.data == "send_yes_say")
async def confirm_say(callback: CallbackQuery):
    text = _pending_say.pop(callback.from_user.id, None)
    if not text:
        await callback.answer("❌ Текст не знайдено, спробуй ще раз.", show_alert=True)
        return
    await callback.bot.send_message(chat_id=GROUP_CHAT_ID, text=text)
    await callback.message.edit_text("✅ Повідомлення відправлено у групу!")
    await callback.answer()


@router.callback_query(F.data == "send_no_say")
async def cancel_say(callback: CallbackQuery):
    _pending_say.pop(callback.from_user.id, None)
    await callback.message.edit_text("❌ Відправку скасовано.")
    await callback.answer()


# ──────────────────────────────────────────
#  /rickroll — Rick Roll для клубу 🎉
# ──────────────────────────────────────────

RICKROLL_TEXT = (
    "🎮 <b>УВАГА! ТЕРМІНОВЕ ПОВІДОМЛЕННЯ ДЛЯ КЛУБУ!</b>\n\n"
    "🏆 Розробники Brawl Stars щойно оголосили:\n\n"
    "✅ Безкоштовний Brawl Pass для всіх гравців\n"
    "✅ x10 до кубків на тиждень\n"
    "✅ Всі скіни безкоштовно\n\n"
    "👇 Деталі за посиланням — не пропусти!\n\n"
    "🔗 https://youtu.be/dQw4w9WgXcQ\n\n"
    "😂 <b>З 1 квітня, клуб! Попався!</b> 🎣"
)


@router.message(Command("rickroll"))
async def cmd_rickroll(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("⛔ Тільки адміністратори.")
        return
    await message.reply(
        "🎣 <b>Rick Roll для клубу</b>\n\n"
        "Бот відправить «офіційне» повідомлення про безкоштовний Brawl Pass 😈\n\n"
        "Відправити у групу?",
        parse_mode="HTML",
        reply_markup=confirm_keyboard("rickroll")
    )


@router.callback_query(F.data == "send_yes_rickroll")
async def confirm_rickroll(callback: CallbackQuery):
    await callback.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=RICKROLL_TEXT,
        parse_mode="HTML"
    )
    await callback.message.edit_text("😂 Rick Roll відправлено! З 1 квітня! 🎣")
    await callback.answer()


@router.callback_query(F.data == "send_no_rickroll")
async def cancel_rickroll(callback: CallbackQuery):
    await callback.message.edit_text("😅 Зберіг сюрприз на потім!")
    await callback.answer()
