from aiogram import Router

router = Router()
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# 📱 Кнопка для отправки номера телефона
phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📲 Отправить номер телефона", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# 📦 Кнопка для регистрации нового заказа
new_order_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Зарегистрировать новый заказ")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# 🛠 Панель администратора
admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Одобрение заказов")],
        [KeyboardButton(text="📤 Отправить рассылку")]
    ],
    resize_keyboard=True,
)

# ✅❌ Инлайн-кнопки для одобрения/отклонения заказа
approve_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data="approve_order"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data="deny_order")
        ]
    ]
)
