from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import ADMIN_IDS, BOT_TOKEN
from sheets import get_sheet

router = Router()
bot = Bot(token=BOT_TOKEN)


class ApproveState(StatesGroup):
    approving = State()


def get_next_unapproved_row(sheet):
    all_rows = sheet.get_all_values()
    for index, row in enumerate(all_rows[1:], start=2):
        if len(row) < 6 or not row[5].strip():
            return index, row
    return None, None


def get_approval_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data="approve_order"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data="deny_order")
        ]
    ])


@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас нет доступа к этой функции.")
        return

    await start_approving(message, state)


async def start_approving(message_or_callback, state: FSMContext):
    sheet = get_sheet()
    index, row = get_next_unapproved_row(sheet)

    if not row:
        await message_or_callback.answer("✅ Нет необработанных заявок.")
        return

    user_info = (
        f"<b>📞 Телефон:</b> {row[0]}\n"
        f"<b>👤 Username:</b> @{row[1]}\n"
        f"<b>🆔 Telegram ID:</b> {row[2]}\n"
        f"<b>🪪 ID участника:</b> {row[3]}\n"
        f"<b>📦 Номер заказа:</b> {row[4]}\n"
        f"<b>🕓 Время:</b> {row[5]}"
    )

    await state.update_data(row_index=index)

    if isinstance(message_or_callback, Message):
        await message_or_callback.answer(user_info, reply_markup=get_approval_keyboard(), parse_mode="HTML")
    else:
        await message_or_callback.message.edit_text(user_info, reply_markup=get_approval_keyboard(), parse_mode="HTML")


@router.callback_query(F.data.in_(["approve_order", "deny_order"]))
async def handle_approval(callback: CallbackQuery, state: FSMContext):
    admin_id = callback.from_user.id

    if admin_id not in ADMIN_IDS:
        await callback.answer("❌ У вас нет доступа к этой функции.", show_alert=True)
        return

    data = await state.get_data()
    row_index = data.get("row_index")

    if not row_index:
        await callback.answer("⚠️ Нет активной заявки.")
        return

    sheet = get_sheet()
    row = sheet.row_values(row_index)

    if callback.data == "approve_order":
        sheet.update_cell(row_index, 6, "Одобрено ✅")
        await callback.answer("✅ Заявка одобрена")

    elif callback.data == "deny_order":
        sheet.update_cell(row_index, 6, "Отклонено ❌")
        await callback.answer("❌ Заявка отклонена")

        # ⛔ Уведомляем пользователя при отклонении
        if len(row) >= 3 and row[2].isdigit():
            try:
                await bot.send_message(
                    chat_id=int(row[2]),
                    text=(
                        "⚠️ Ваш заказ был отклонён.\n\n"
                        "Проверьте правильность ID и номера заказа.\n"
                        "Если у вас возникли вопросы, обратитесь к своему менеджеру."
                    )
                )
            except Exception as e:
                print(f"❗ Ошибка при отправке уведомления: {e}")

    # Показать следующую заявку
    await start_approving(callback, state)
