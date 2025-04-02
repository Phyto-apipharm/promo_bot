from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sheets import append_data_to_sheet
from handlers.repeat_order import phone_keyboard, new_order_button

router = Router()

class Registration(StatesGroup):
    waiting_for_id = State()
    waiting_for_order = State()

@router.message(F.contact)
async def process_contact(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await message.answer("📞 Телефон получен.\n\n🪪Введите ваш ID-номер 🪪:")
    await state.set_state(Registration.waiting_for_id)

@router.message(Registration.waiting_for_id)
async def process_id_number(message: Message, state: FSMContext):
    await state.update_data(user_id=message.text)
    await message.answer("📦 Введите номер заказа 📦:")
    await state.set_state(Registration.waiting_for_order)

@router.message(F.text == "📦 Зарегистрировать новый заказ")
async def repeat_order(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if "phone" in user_data and "user_id" in user_data:
        await message.answer("📦 Введите номер заказа 📦:")
        await state.set_state(Registration.waiting_for_order)
    else:
        await message.answer("❗ Не найдены данные. Начните регистрацию заново.")
        await state.clear()

@router.message(Registration.waiting_for_order)
async def order_received(message: Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        phone, user_iduser = user_data["phone"], user_data["user_id"]
        username, tg_id = message.from_user.username or "", str(message.from_user.id)

        await append_data_to_sheet(phone, username, tg_id, user_iduser, message.text)

        await message.answer(
            "✅ Заказ зарегистрирован!\n\nУдачи в розыгрыше!\n\nДобавьте ещё один заказ кнопкой ниже.",
            reply_markup=new_order_button
        )

        await state.set_data({"phone": phone, "tg_id": tg_id, "user_id": user_iduser})

    except Exception as e:
        print(f"Ошибка при записи: {e}")
        await message.answer("❌ Ошибка при сохранении данных, попробуйте позже.")
        await state.clear()
