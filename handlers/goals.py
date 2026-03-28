import json
import os
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS

router = Router()

GOALS_FILE = "data/goals.json"


# ──────────────────────────────────────────
#  Утиліти для роботи з файлом цілей
# ──────────────────────────────────────────

def load_goals() -> list:
    if not os.path.exists(GOALS_FILE):
        return []
    with open(GOALS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_goals(goals: list):
    os.makedirs(os.path.dirname(GOALS_FILE), exist_ok=True)
    with open(GOALS_FILE, "w", encoding="utf-8") as f:
        json.dump(goals, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────
#  FSM стани
# ──────────────────────────────────────────

class GoalStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()


# ──────────────────────────────────────────
#  Команди
# ──────────────────────────────────────────

@router.message(Command("goals"))
async def cmd_goals(message: Message):
    """Показати всі цілі клубу."""
    goals = load_goals()

    if not goals:
        await message.reply(
            "🎯 <b>Цілі клубу</b>\n\nЦілей ще немає. Адміністратор може додати ціль командою /addgoal",
            parse_mode="HTML"
        )
        return

    text = "🎯 <b>Цілі клубу Brawl Stars</b>\n\n"
    for i, goal in enumerate(goals, 1):
        status = "✅" if goal.get("completed") else "🔄"
        text += f"{status} <b>{i}. {goal['title']}</b>\n"
        if goal.get("description"):
            text += f"   └ {goal['description']}\n"
        text += "\n"

    await message.reply(text, parse_mode="HTML")


@router.message(Command("addgoal"))
async def cmd_add_goal(message: Message, state: FSMContext):
    """Додати нову ціль."""
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("⛔ Тільки адміністратори можуть додавати цілі.")
        return

    await message.reply(
        "🎯 <b>Нова ціль клубу</b>\n\nВведіть назву цілі:",
        parse_mode="HTML"
    )
    await state.set_state(GoalStates.waiting_for_title)


@router.message(GoalStates.waiting_for_title)
async def goal_title_received(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.reply(
        "📝 Введіть опис цілі (або надішліть <code>-</code> щоб пропустити):",
        parse_mode="HTML"
    )
    await state.set_state(GoalStates.waiting_for_description)


@router.message(GoalStates.waiting_for_description)
async def goal_description_received(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    description = "" if message.text == "-" else message.text
    goals = load_goals()
    new_goal = {
        "id": len(goals) + 1,
        "title": data["title"],
        "description": description,
        "completed": False
    }
    goals.append(new_goal)
    save_goals(goals)

    await message.reply(
        f"✅ Ціль <b>«{data['title']}»</b> додана до списку клубу!",
        parse_mode="HTML"
    )


@router.message(Command("completegoal"))
async def cmd_complete_goal(message: Message):
    """Позначити ціль як виконану."""
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("⛔ Тільки адміністратори можуть змінювати цілі.")
        return

    goals = load_goals()
    if not goals:
        await message.reply("❌ Немає цілей для виконання.")
        return

    # Inline кнопки для вибору цілі
    buttons = []
    for goal in goals:
        if not goal.get("completed"):
            buttons.append([
                InlineKeyboardButton(
                    text=f"🎯 {goal['title']}",
                    callback_data=f"complete_goal_{goal['id']}"
                )
            ])

    if not buttons:
        await message.reply("✅ Всі цілі вже виконані!")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.reply("Оберіть ціль, яку позначити як виконану:", reply_markup=kb)


@router.callback_query(F.data.startswith("complete_goal_"))
async def complete_goal_callback(callback: CallbackQuery):
    goal_id = int(callback.data.split("_")[-1])
    goals = load_goals()

    for goal in goals:
        if goal["id"] == goal_id:
            goal["completed"] = True
            break

    save_goals(goals)
    await callback.message.edit_text(
        f"🏆 Ціль <b>«{goal['title']}»</b> виконана! Вітаємо клуб!",
        parse_mode="HTML"
    )
    await callback.answer("✅ Ціль виконана!")


@router.message(Command("cleargoals"))
async def cmd_clear_goals(message: Message):
    """Очистити всі виконані цілі."""
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("⛔ Тільки адміністратори.")
        return

    goals = [g for g in load_goals() if not g.get("completed")]
    save_goals(goals)
    await message.reply("🗑️ Виконані цілі видалено!")
