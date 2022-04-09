from telebot import types


# Клавиатура основная
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=False, selective=False)

    btn1 = types.KeyboardButton('📄Расписание')
    btn2 = types.KeyboardButton('📥Скачать файл')
    btn3 = types.KeyboardButton('📤Загрузить файл')
    btn4 = types.KeyboardButton('👤Профиль')
    markup.add(btn1)
    markup.row(btn2, btn3)
    markup.add(btn4)
    return markup


# Клавиатура диалогов
def schedule_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=False, selective=False)
    btn1 = types.KeyboardButton('Сегодня')
    btn2 = types.KeyboardButton('Завтра')
    btn3 = types.KeyboardButton('Неделя')
    btn4 = types.KeyboardButton('Месяц')
    btn5 = types.KeyboardButton('Ауд.')
    btn6 = types.KeyboardButton('Препод.')
    btn7 = types.KeyboardButton('Группа')
    btn8 = types.KeyboardButton('Студент')
    btn9 = types.KeyboardButton('Назад ↩️')
    markup.row(btn1, btn2, btn3, btn4)
    markup.row(btn5, btn6, btn7, btn8)
    markup.row(btn9)
    return markup

# Клавиатура ответа пользователю
def feedback_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    inline_1 = types.InlineKeyboardButton(text="Ответить чмоне", callback_data='reply_to_user')
    markup.add(inline_1)
    return markup

# Клавиатура обратной связи
def profile_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    inline_1 = types.InlineKeyboardButton(text="🔄Сменить ФИО", callback_data='fio_input')
    inline_2 = types.InlineKeyboardButton(text="📝Написать админу", callback_data='feedback')
    markup.row(inline_1, inline_2)
    return markup

# Клавиатура ФИО
def fio_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    inline_1 = types.InlineKeyboardButton(text="Ввести ФИО", callback_data='fio_input')
    markup.add(inline_1)
    return markup

# Клавиатура админа
def admin_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    inline_1 = types.InlineKeyboardButton(text="Рассылка", callback_data='send_newsletter')
    inline_2 = types.InlineKeyboardButton(text="Написать пользователю", callback_data='send_user')
    # inline_3 = types.InlineKeyboardButton(text="", callback_data='')
    markup.add(inline_1)
    markup.add(inline_2)
    return markup

# Клавиатура скрытия
def hide_schedule_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    inline_1 = types.InlineKeyboardButton(text="❌", callback_data='del_sch')
    # inline_3 = types.InlineKeyboardButton(text="", callback_data='')
    markup.add(inline_1)
    return markup

# Клавиатура обработки файлов
def file_moderation_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    inline_1 = types.InlineKeyboardButton(text="Принять", callback_data='acc_file')
    inline_2 = types.InlineKeyboardButton(text="Отклонить", callback_data='dec_file')
    markup.row(inline_1, inline_2)
    return markup
