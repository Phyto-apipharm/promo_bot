import asyncio
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import ADMIN_IDS
from handlers.repeat_order import admin_keyboard, approve_keyboard
from sheets import get_sheet

router = Router()

class BroadcastState(StatesGroup):
    waiting_for_text = State()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("👨‍💼 Добро пожаловать в админ-панель", reply_markup=admin_keyboard)
    else:
        await message.answer("❌ У вас нет доступа к этой команде.")

# 👉 Универсальный показ заявок (Message или CallbackQuery)
async def start_approving(event, state: FSMContext):
    user_id = event.from_user.id

    if user_id not in ADMIN_IDS:
        if isinstance(event, CallbackQuery):
            await event.answer("❌ У вас нет доступа к этой функции.")
        else:
            await event.answer("❌ У вас нет доступа к этой функции.")
        return

    sheet = get_sheet()
    data = sheet.get_all_values()

    for idx, row in enumerate(data[1:], start=2):  # Пропускаем заголовки
        if len(row) < 6 or row[6]:  # Статус уже есть
            continue

        text = (
            f"<b>📦 Заявка</b>\n\n"
            f"📞 Телефон: {row[0]}\n"
            f"🆔 ID: {row[3]}\n"
            f"📦 Заказ: {row[4]}\n"
            f"📅 Дата: {row[5]}"
        )

        await state.set_data({"row_index": idx, "tg_id": row[2]})  # сохраняем также tg_id

        if isinstance(event, CallbackQuery):
            await event.message.answer(
                text,
                reply_markup=approve_keyboard,
                parse_mode="HTML"
            )
        else:
            await event.answer(
                text,
                reply_markup=approve_keyboard,
                parse_mode="HTML"
            )
        return

    # Если заявок нет
    if isinstance(event, CallbackQuery):
        await event.message.answer("✅ Все заказы были проверены.")
    else:
        await event.answer("✅ Все заказы были проверены.")

# 👉 Обработка кнопки "📋 Одобрение заказов"
@router.message(F.text == "📋 Одобрение заказов")
async def admin_start_approval(message: Message, state: FSMContext):
    await start_approving(message, state)

# 👉 Обработка кнопок ✅ / ❌
@router.callback_query(F.data.in_(["approve_order", "deny_order"]))
async def handle_approval(callback: CallbackQuery, state: FSMContext):
    admin_id = callback.from_user.id

    if admin_id not in ADMIN_IDS:
        await callback.answer("❌ У вас нет доступа к этой функции.", show_alert=True)
        return

    data = await state.get_data()
    row_index = data.get("row_index")
    tg_id = data.get("tg_id")

    if not row_index:
        await callback.answer("⚠️ Нет активной заявки.")
        return

    sheet = get_sheet()

    if callback.data == "approve_order":
        sheet.update_cell(row_index, 7, "Одобрено")
        await callback.answer("✅ Заявка одобрена")
    elif callback.data == "deny_order":
        sheet.delete_rows(row_index)
        await callback.answer("❌ Заявка отклонена")

        # Рассылка пользователю
        try:
            if tg_id and str(tg_id).isdigit():
                await callback.bot.send_message(
                    int(tg_id),
                    "⚠️ Ваша заявка не прошла проверку и была отклонена.\nПроверьте правильность ваших данных и попробуйте снова.\nЕсли у вас есть вопросы, обратитесь к менеджеру @Phyto_apipharm_uz",
                )
        except Exception:
            pass  # не удалось отправить — продолжаем

    # Показать следующую
    await start_approving(callback, state)

# 📤 Обработка кнопки "Отправить рассылку"
@router.message(F.text == "📤 Отправить рассылку")
async def ask_broadcast_text(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас нет доступа к этой функции.")
        return
    await state.set_state(BroadcastState.waiting_for_text)
    await message.answer("✏️ Введите текст рассылки, и я отправлю его всем пользователям.")

# ✅ Отправка рассылки по уникальным Telegram ID
@router.message(BroadcastState.waiting_for_text)
async def send_broadcast(message: Message, state: FSMContext):
    sheet = get_sheet()
    data = sheet.get_all_values()[1:]  # Пропускаем заголовки

    tg_ids = set()
    sent = 0
    failed = 0

    for row in data:
        if len(row) >= 3:
            tg_id = row[2]
            if tg_id.isdigit():
                tg_ids.add(int(tg_id))

    for tg_id in tg_ids:
        try:
            await message.bot.send_message(tg_id, message.text)
            sent += 1
            await asyncio.sleep(0.2)
        except Exception:
            failed += 1

    await message.answer(f"📤 Рассылка завершена.\n✅ Успешно: {sent}\n❌ Ошибок: {failed}")
    await state.clear()
