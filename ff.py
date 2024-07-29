import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Словарь для хранения состояния пользователей
user_state = {}
user_data = {}

# Ваш Telegram ID
ADMIN_ID = 1151245812  # Замените на ваш реальный Telegram ID

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Диспетчерское", callback_data='dispatcher')],
        [InlineKeyboardButton("Административное", callback_data='administrative')],
        [InlineKeyboardButton("Управленческое", callback_data='management')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите направление, которое вам более интересно', reply_markup=reply_markup)
    user_state[update.effective_user.id] = 'choose_direction'

# Обработчик callback-запросов
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == 'back':
        current_state = user_state.get(user_id, {}).get('state')
        
        if current_state == 'select_day':
            keyboard = [
                [InlineKeyboardButton("9:00", callback_data='9:00'), InlineKeyboardButton("9:15", callback_data='9:15')],
                [InlineKeyboardButton("9:30", callback_data='9:30'), InlineKeyboardButton("9:45", callback_data='9:45')],
                [InlineKeyboardButton("15:30", callback_data='15:30'), InlineKeyboardButton("15:45", callback_data='15:45')],
                [InlineKeyboardButton("16:00", callback_data='16:00'), InlineKeyboardButton("16:15", callback_data='16:15')],
                [InlineKeyboardButton("16:30", callback_data='16:30'), InlineKeyboardButton("17:00", callback_data='17:00')],
                [InlineKeyboardButton("16:45", callback_data='16:45'), InlineKeyboardButton("17:15", callback_data='17:15')],
                [InlineKeyboardButton("17:30", callback_data='17:30'), InlineKeyboardButton("17:45", callback_data='17:45')],
                [InlineKeyboardButton("Назад", callback_data='back')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text('Выберите время, в которое будет удобно подойти', reply_markup=reply_markup)
            user_state[user_id] = {'state': 'select_time'}
            return
        elif current_state == 'select_time':
            keyboard = [
                [InlineKeyboardButton("Диспетчерское", callback_data='dispatcher')],
                [InlineKeyboardButton("Административное", callback_data='administrative')],
                [InlineKeyboardButton("Управленческое", callback_data='management')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text('Выберите направление, которое вам более интересно', reply_markup=reply_markup)
            user_state.pop(user_id, None)
            return
        elif current_state in ['dispatcher', 'administrative', 'management']:
            text, keyboard = get_direction_text_and_keyboard(current_state)
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=text, reply_markup=reply_markup)
            return

    if query.data in ['9:00', '9:15', '9:30', '9:45', '16:30', '17:00', '16:45', '17:15']:
        keyboard = [
            [InlineKeyboardButton("ПН", callback_data='ПН')],
            [InlineKeyboardButton("ВТ", callback_data='ВТ')],
            [InlineKeyboardButton("СР", callback_data='СР')],
            [InlineKeyboardButton("ЧТ", callback_data='ЧТ')],
            [InlineKeyboardButton("ПТ", callback_data='ПТ')],
            [InlineKeyboardButton("Назад", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text('Выберите дни, в которые вам будет удобно подойти', reply_markup=reply_markup)
        user_state[user_id] = {'state': 'select_day', 'time': query.data}
        return

    if query.data in ['15:30', '15:45', '16:00', '16:15', '17:30', '17:45']:
        keyboard = [
            [InlineKeyboardButton("ПТ", callback_data='ПТ')],
            [InlineKeyboardButton("Назад", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text('Выберите день, в который вам будет удобно подойти', reply_markup=reply_markup)
        user_state[user_id] = {'state': 'select_day', 'time': query.data}
        return

    if query.data == 'next':
        current_state = user_state.get(user_id)
        if current_state and current_state['state'] in ['dispatcher', 'administrative', 'management']:
            keyboard = [
                [InlineKeyboardButton("9:00", callback_data='9:00'), InlineKeyboardButton("9:15", callback_data='9:15')],
                [InlineKeyboardButton("9:30", callback_data='9:30'), InlineKeyboardButton("9:45", callback_data='9:45')],
                [InlineKeyboardButton("15:30", callback_data='15:30'), InlineKeyboardButton("15:45", callback_data='15:45')],
                [InlineKeyboardButton("16:00", callback_data='16:00'), InlineKeyboardButton("16:15", callback_data='16:15')],
                [InlineKeyboardButton("16:30", callback_data='16:30'), InlineKeyboardButton("17:00", callback_data='17:00')],
                [InlineKeyboardButton("16:45", callback_data='16:45'), InlineKeyboardButton("17:15", callback_data='17:15')],
                [InlineKeyboardButton("17:30", callback_data='17:30'), InlineKeyboardButton("17:45", callback_data='17:45')],
                [InlineKeyboardButton("Назад", callback_data='back')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text('Выберите время, в которое будет удобно подойти', reply_markup=reply_markup)
            user_state[user_id] = {'state': 'select_time'}
            return

    if query.data in ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ']:
        user_state[user_id] = {'state': 'collect_data', 'day': query.data, 'time': user_state[user_id]['time']}
        await query.edit_message_text('Оставьте своё ФИО и номер телефона, по которому с вами свяжутся и подтвердят запись')
        return

    if query.data in ['dispatcher', 'administrative', 'management']:
        user_state[user_id] = {'state': query.data}

    text, keyboard = get_direction_text_and_keyboard(query.data)
    if text:
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup)

def get_direction_text_and_keyboard(direction):
    if direction == 'dispatcher':
        text = """📌 ДИСПЕТЧЕРСКОЕ НАПРАВЛЕНИЕ –
- Прием входящих телефонных звонков
- Прием заявок и заказов
- Консультация клиентов по телефону
- Внесение данных на платформы компании
- Сопровождение клиента по телефону
- Отчетность перед руководством
- График работы 2/2
- График работы 5/2
- Можно составить индивидуальный график
Оплата оговаривается исходя из графика на этапе собеседования."""
    elif direction == 'administrative':
        text = """📌 АДМИНИСТРАТИВНОЕ НАПРАВЛЕНИЕ (МЕНЕДЖЕР) –
- Контроль за порядком в офисе
- Прием и консультация клиентов
- Ведение переписки и переговоров
- Ведение первичной и отчетной документации, решение орг. вопросов по офису
- ГРАФИК (можно составить индивидуально, так же есть варианты 2/2, 5/2)
- Оплата ориентировочно в первый месяц порядка 45 000, со второго месяца порядка 55 000 + премиальная часть."""
    elif direction == 'management':
        text = """📌 УПРАВЛЕНЧЕСКОЕ НАПРАВЛЕНИЕ –
- Планирование, организация, взаимодействие с другими отделами и филиалами, управление
- Инструктирование, контроль, участие в расширении отдела
- ГРАФИК – 5/2, оплата на начальный месяц порядка 95 000, со второго месяца порядка 120 000 + Условия оговариваются на собеседовании"""
    else:
        text = ""
    
    keyboard = [[InlineKeyboardButton("Далее", callback_data='next')],
                [InlineKeyboardButton("Назад", callback_data='back')]]
    
    return text, keyboard

# Обработчик текстовых сообщений для сбора данных пользователя
async def collect_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    current_state = user_state.get(user_id)

    if current_state and current_state['state'] == 'collect_data':
        user_data[user_id] = update.message.text
        day = current_state['day']
        time = current_state['time']
        user_state.pop(user_id, None)
        
        confirmation_text = f"{user_data[user_id]}, ДЛЯ БОЛЕЕ ДЕТАЛЬНОГО РАЗГОВОРА ЖДЁМ ВАС в {day} в {time} по адресу:\nУл. Богдана Хмельницкого 59 4-й этаж 432 офис\nСпросите на входе Тимура Саяновича"
        await update.message.reply_text(confirmation_text)

        # Отправка информации администратору
        username = update.message.from_user.username
        admin_text = f"Пользователь @{username} записался на встречу.\n\nДанные: {user_data[user_id]}\nДата: {day}\nВремя: {time}"
        logger.info(f"Отправка сообщения админу: {admin_text}")
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)

def main():
    application = Application.builder().token("7417215075:AAFz39utBJGcVQT6DS4_eELk15E0GPjxc94").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_data))

    application.run_polling()

if __name__ == '__main__':
    main()
