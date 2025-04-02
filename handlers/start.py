from aiogram import Router
from aiogram.types import Message
from handlers.repeat_order import phone_keyboard

router = Router()

@router.message(lambda message: message.text == "/start")
async def start_handler(message: Message):
    await message.answer(
        "🎉 Добро пожаловать в акцию <b>«Золотой билет»</b> от компании Phyto-Apipharm!\n\n"
        "Условия акции: Чтобы участвовать в промоушене, нужно сделать заказ на 10 единиц, используя личный Id-номер в период действия акции.\n\n"
        "Период действия акции: 21.03.2025 – 30.06.2025\n\n"
        "Чтобы принять участие в розыгрыше, вам необходимо подтвердить ваш номер телефона, ввести личный Id-номер и номер заказа.\n\n"
        "📱 <b>Нажмите кнопку ниже, чтобы отправить ваш номер телефона.</b>",
        reply_markup=phone_keyboard
    )
