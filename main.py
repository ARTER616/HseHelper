import telebot
from telebot import types, util
import requests, sqlite3, traceback as trcb, configparser, time, os, logging, shutil
from datetime import datetime, timedelta
from config import list_full_path, list_dir, list_full_files, list_full_dir
from keyboard import main_keyboard, schedule_keyboard, feedback_keyboard, profile_keyboard, fio_keyboard, admin_keyboard
from keyboard import hide_schedule_keyboard, file_moderation_keyboard
from database import get_ruz_database, get_user_info, get_count_database, get_count_status, get_all_users, create_db
from database import up_user_files, up_ruz_id, up_all_files, get_file_count

config = configparser.ConfigParser()
config.read("misc/settings.ini")
tg_token = config['Telegram']['tg_token']
admin_id = int(config['Telegram']['admin_id'])
chat_link = config['Telegram']['chat_link']

bot = telebot.AsyncTeleBot(tg_token)

logger = telebot.logging
logger.basicConfig(filename='misc/logs.log', level=logging.ERROR,
                   format=' %(asctime)s - %(levelname)s - %(message)s')


@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    try:
        sql = create_db(chat_id)
        if sql is None:
            bot.send_photo(chat_id, open('source_imgs/main_logo.png', 'rb'), caption="Приветствую в боте-помощнике "
                                                                                     "студентам ВШЭ!\nДанный бот "
                                                                                     "работает по принципу "
                                                                                     "файлообменника - вы загружаете "
                                                                                     "полезные для студентов файлы и "
                                                                                     "можете найти и скачать что-то "
                                                                                     "для себя. Все файлы проходят "
                                                                                     "модерацию для избежания "
                                                                                     "засорения мусором.\nДля "
                                                                                     "использования расписания вам "
                                                                                     "необходимо ввести свое ФИО, "
                                                                                     "но оно не будет храниться в "
                                                                                     "базе в целях "
                                                                                     "конфиденциальности.\nДля "
                                                                                     "навигации по боту "
                                                                                     "воспользуйтесь кнопками "
                                                                                     "управления. Приятного "
                                                                                     "пользования!",
                           reply_markup=fio_keyboard())
        else:
            bot.send_photo(chat_id, open('source_imgs/main_logo.png', 'rb'), caption="Добро пожаловать!",
                           reply_markup=main_keyboard())
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


@bot.message_handler(commands=['admin'])
def admin_panel(message):
    try:
        chat_id = message.chat.id
        if chat_id == admin_id:
            users_count = get_count_database()
            files = get_file_count()
            status = get_count_status()
            bot.send_message(admin_id,
                             f"Админка💻\n\nПользоваталей в боте: {users_count}\n\nЗагружено файлов: {files}\n\n"
                             f"Пользователей со вторым статусом: {status}", reply_markup=admin_keyboard())
        else:
            message = bot.send_message(message.chat.id, "Вам сюда нельзя🧸")
            message.wait()
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


@bot.message_handler(commands=['help'])
def help_notes(message):
    try:
        chat_id = message.chat.id
        bot.send_message(chat_id,
                         f"⚠️Данный бот - неофициальный.⚠️\nБот, как и его разработчик, не имеет никакого отношения к "
                         f"НИУ ВШЭ. При составлении расписания используется открытая информация из апи РУЗа. "
                         f"Администрация не пишет первой ни с каких аккаунтов телеграма, за исключением рассылки и "
                         f"сообщений внутри бота.\n\nИнформация содержащаяся в расписании:\n\n🌐 - онлайн пара(если "
                         f"пара офлайн, на этом месте "
                         f"располагается номер кабинета)\n\n🔗 - кликабельная ссылка на онлайн пару\n\n\nУпрощение "
                         f"пользования ботом:\n\nПример запроса в расписании аудитории/преподавателя/группы/студента "
                         f"копируется при нажатии(в мобильной версии), аналогично с папками при поиске "
                         f"файла.\n\nСвязаться с администрацией можно по кнопке, которая находится в профиле.\n\nВаше "
                         f"ФИО нужно только для вывода личного расписания и больше никак не используется, "
                         f"в базе хранится числовой идентификатор РУЗа. По такому же принципу работает авторизация в "
                         f"приложении HSE app, но оно хранит ваше ФИО в том числе.(Не путать с HSE app X, "
                         f"в нем авторизация через почту)\n\nНадеюсь данный бот окажется вам полезен.",
                         reply_markup=hide_schedule_keyboard())
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    chat_id = call.message.chat.id
    # print(call.message)
    try:
        if call.data == "fio_input":
            # message = bot.send_message(chat_id, "Введите ваше ФИО через пробел:")
            if call.message.caption is not None:
                message = bot.edit_message_caption('Введите ваше ФИО через пробел:', chat_id=chat_id,
                                                   message_id=call.message.id)
                message = message.wait()
            else:
                message = bot.edit_message_text('Введите ваше ФИО через пробел:', chat_id=chat_id,
                                                message_id=call.message.id)
                message = message.wait()
            bot.register_next_step_handler(message, get_ruz_id)
        if call.data == "feedback":
            message = bot.edit_message_text("Напишите ваше сообщение(можно прикрепить 1 картинку):", chat_id=chat_id,
                                            message_id=call.message.id)
            message = message.wait()
            msg = message.id
            bot.register_next_step_handler(message, get_feedback, msg)
        if call.data == "reply_to_user":
            message = bot.send_message(chat_id, "Telegram ID пользователя:")
            message = message.wait()
            bot.register_next_step_handler(message, id_reply)
        if call.data == "send_newsletter":
            if call.message.chat.id == admin_id:
                message = bot.send_message(chat_id, "Текст рассылки с картинкой:")
                message = message.wait()
                bot.register_next_step_handler(message, get_newsletter)
        if call.data == "send_user":
            if call.message.chat.id == admin_id:
                message = bot.send_message(chat_id, "Telegram ID пользователя:")
                message = message.wait()
                bot.register_next_step_handler(message, user_send)
        if call.data == "del_sch":
            bot.delete_message(chat_id, call.message.id)
        if call.data == "acc_file":
            if call.message.chat.id == admin_id:
                filename = call.message.document.file_name
                cmsid = call.message.id
                message = bot.send_message(admin_id, "Введите директорию:")
                message = message.wait()
                bot.register_next_step_handler(message, sort_files, filename, message.id, cmsid)
        if call.data == "dec_file":
            os.remove(f"unsorted/{call.message.document.file_name}")
            bot.delete_message(admin_id, call.message.id)
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    try:
        chat_id = message.chat.id
        # print(chat_id)
        # print(get_ruz_database(chat_id))
        # print(sql.fetchone() is not None)
        # print(get_ruz_database(chat_id) != 0)
        # print((sql.fetchone() is not None) and (get_ruz_database(chat_id) != 0))
        if get_ruz_database(chat_id) != 0:
            # if message.text == '🔄Сменить ФИО':
            if message.text == '👤Профиль':
                user_str = '👤Профиль\n\nВы зарегистрированы: '
                info = get_user_info(chat_id)
                # print(info[1])
                user_str = user_str + info[0] + '.\n\nВами загружено ' + info[1] + ' файлов.'
                bot.send_message(chat_id, user_str, reply_markup=profile_keyboard())
            if message.text == 'Назад ↩️':
                bot.send_message(chat_id, "Главное меню", reply_markup=main_keyboard())
            if message.text == '📄Расписание':
                bot.send_message(chat_id, "Выберите период расписания кнопкой:", reply_markup=schedule_keyboard())
            if message.text == 'Завтра':
                ruz_id = get_ruz_database(chat_id)
                # print(ruz_id)
                if datetime.isoweekday(datetime.today()) != 6:
                    today = datetime.today()
                    tomorrow = today + timedelta(days=1)  # 1 день (завтра)
                    # print(tomorrow)
                    date1 = datetime.date(tomorrow)
                    # print(date1)
                    get_schedule(date1, date1, chat_id, ruz_id)
                else:
                    today = datetime.today()
                    tomorrow = today + timedelta(days=2)  # 2 дня (послезавтра т.к. сегодня суббота)
                    # print(tomorrow)
                    date1 = datetime.date(tomorrow)
                    bot.send_message(chat_id, "Завтра воскресенье, расписание на понедельник:")
                    get_schedule(date1, date1, chat_id, ruz_id)
            if message.text == 'Сегодня':
                ruz_id = get_ruz_database(chat_id)
                # print(ruz_id)
                if datetime.isoweekday(datetime.today()) != 7:
                    today = datetime.today()
                    today = today
                    date1 = datetime.date(today)
                    get_schedule(date1, date1, chat_id, ruz_id)
                else:
                    bot.send_message(chat_id, "Сегодня воскресенье, выберите другой период.")
            if message.text == 'Неделя':
                ruz_id = get_ruz_database(chat_id)
                # bot.send_message(chat_id, "Расписание на неделю")
                date1 = datetime.today()
                if datetime.isoweekday(date1) != 1 and datetime.isoweekday(date1) != 7:
                    date1 = date1 + timedelta(days=-(datetime.isoweekday(date1) - 1))
                if datetime.isoweekday(date1) == 7:
                    date1 = date1 + timedelta(days=1)
                if datetime.isoweekday(date1) == 1:
                    date1 = date1
                date2 = date1 + timedelta(days=6)
                # print(datetime.date(date1), ' ', datetime.date(date2))
                get_schedule(datetime.date(date1), datetime.date(date2), chat_id, ruz_id)
            if message.text == 'Месяц':
                # bot.send_message(chat_id, "Расписание на месяц")
                ruz_id = get_ruz_database(chat_id)
                date1 = datetime.today()
                # print(int(str(datetime.date(date1))[8:]))
                if int(str(datetime.date(date1))[8:]) != 1 and int(str(datetime.date(date1))[8:]) != 30 and int(
                        str(datetime.date(date1))[8:]) != 31:
                    date1 = date1 + timedelta(days=-(int(str(datetime.date(date1))[8:]) - 1))

                if int(str(datetime.date(date1))[8:]) == 30:
                    date1 = date1 + timedelta(days=2)
                if int(str(datetime.date(date1))[8:]) == 31:
                    date1 = date1 + timedelta(days=1)
                if int(str(datetime.date(date1))[8:]) == 1:
                    date1 = date1
                date2 = date1 + timedelta(days=30)
                # print(datetime.date(date1), ' ', datetime.date(date2))
                get_schedule(datetime.date(date1), datetime.date(date2), chat_id, ruz_id)
            if message.text == "Препод.":
                message = bot.send_message(chat_id,
                                           f"Введите ФИО преподавателя и дату через пробел, пример:\n(`Иванов Иван "
                                           f"Иванович "
                                           f"{datetime.strptime(str(datetime.date(datetime.today())), '%Y-%m-%d').strftime('%Y.%m.%d')}-{datetime.strptime(str(datetime.date(datetime.today())), '%Y-%m-%d').strftime('%Y.%m.%d')}`)",
                                           parse_mode="Markdown")
                message = message.wait()
                bot.register_next_step_handler(message, prepod_input)
            if message.text == "Ауд.":
                message = bot.send_message(chat_id,
                                           f"Введите номер аудитории и дату через пробел, пример:\n(`300 {datetime.strptime(str(datetime.date(datetime.today())), '%Y-%m-%d').strftime('%Y.%m.%d')}-{datetime.strptime(str(datetime.date(datetime.today())), '%Y-%m-%d').strftime('%Y.%m.%d')}`)",
                                           parse_mode="Markdown")
                message = message.wait()
                bot.register_next_step_handler(message, room_input)
            if message.text == "Группа":
                message = bot.send_message(chat_id, f"Введите точный номер группы и дату через пробел, пример:\n("
                                                    f"`ГРП192 {datetime.strptime(str(datetime.date(datetime.today())), '%Y-%m-%d').strftime('%Y.%m.%d')}-{datetime.strptime(str(datetime.date(datetime.today())), '%Y-%m-%d').strftime('%Y.%m.%d')}`)",
                                           parse_mode="Markdown")
                message = message.wait()
                bot.register_next_step_handler(message, group_input)
            if message.text == "Студент":
                message = bot.send_message(chat_id,
                                           f"Введите ФИО студента и дату через пробел, пример:\n(`Иванов Иван Иванович {datetime.strptime(str(datetime.date(datetime.today())), '%Y-%m-%d').strftime('%Y.%m.%d')}-{datetime.strptime(str(datetime.date(datetime.today())), '%Y-%m-%d').strftime('%Y.%m.%d')}`)",
                                           parse_mode="Markdown")
                message = message.wait()
                bot.register_next_step_handler(message, student_input)
            if message.text == "📥Скачать файл":
                message = bot.send_message(chat_id, f"🗂/\n\nВыберите папку:\n{list_full_dir('stud_files')}",
                                           parse_mode="Markdown")
                message = message.wait()
                msg_id = message.id
                bot.register_next_step_handler(message, dir_input, msg_id)
            if message.text == "📤Загрузить файл":
                message = bot.send_message(chat_id, "Отправьте в одном сообщении файл и текст вида `Направление/Курс`\n\n_Вес файла не должен превышать 20мб (ограничение телеграма для ботов), большие файлы можно скинуть ссылкой на dropmefiles.com в сообщении админу(в профиле)._",
                                           parse_mode="Markdown")
                message = message.wait()
                msg_id = message.id
                bot.register_next_step_handler(message, file_info_input, msg_id)
        else:
            bot.send_message(chat_id, "Пожалуйста, пройдите авторизацию.", reply_markup=fio_keyboard())
        # time.sleep(3)
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def sort_files(message, filename, msid, cmsid):
    try:
        dir1 = message.text
        dir2 = dir1
        dir1 = dir1.split('/')[-2:][0]
        dir2 = dir2.split('/')[-1:][0]
        #print(dir1, dir2)
        if os.path.exists(f"stud_files/{dir1}") == False:
            os.mkdir(f"stud_files/{dir1}")
            os.mkdir(f"stud_files/{dir1}/{dir2}")
            path = shutil.move(f"unsorted/{filename}", f"stud_files/{message.text}")
            up_all_files()
            bot.send_message(admin_id, "Файл успешно добавлен.")
            bot.delete_message(admin_id, msid)
            bot.delete_message(admin_id, cmsid)
        elif os.path.exists(f"stud_files/{dir1}") == True and os.path.exists(f"stud_files/{dir1}/{dir2}") == True:
            path = shutil.move(f"unsorted/{filename}", f"stud_files/{message.text}")
            up_all_files()
            bot.send_message(admin_id, "Файл успешно добавлен.")
            bot.delete_message(admin_id, msid)
            bot.delete_message(admin_id, cmsid)
        elif os.path.exists(f"stud_files/{dir1}") == True and os.path.exists(f"stud_files/{dir1}/{dir2}") == False:
            #print(os.path.exists(f"stud_files/{dir2}"))
            os.mkdir(f"stud_files/{dir1}/{dir2}")
            path = shutil.move(f"unsorted/{filename}", f"stud_files/{message.text}")
            up_all_files()
            bot.send_message(admin_id, "Файл успешно добавлен.")
            bot.delete_message(admin_id, msid)
            bot.delete_message(admin_id, cmsid)
    except Exception as e:
        bot.send_message(admin_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))



def file_info_input(message, msg_id):
    chat_id = message.chat.id
    # print(chat_id)
    #print(message.document.file_name)
    try:
        if message.document is not None and message.caption is not None:
            link = f'[{str(message.from_user.first_name)}](tg://user?id={str(message.chat.id)})'
            file_info = bot.get_file(message.document.file_id)
            file_info = file_info.wait()
            uploaded_file = bot.download_file(file_info.file_path)
            uploaded_file = uploaded_file.wait()
            src = f'unsorted/' + message.document.file_name
            with open(src, 'wb') as new_file:
                new_file.write(uploaded_file)
            doc = open(src, 'rb')
            up_user_files(chat_id)
            bot.reply_to(message, "Файл отправлен на модерацию.")
            bot.send_document(admin_id, doc,
                              caption=f"Файл отправлен пользователем {link} (`{chat_id}`)\n\n`{message.caption}`",
                              parse_mode="Markdown", reply_markup=file_moderation_keyboard())
            # bot.send_document(admin_id, uploaded_file, caption=f"Файл отправлен пользователем {link} (`{chat_id}`) - <<`{message.document.file_name}`>>\n\n{message.caption}", parse_mode="Markdown")
        elif message.document is None:
            bot.send_message(chat_id, "Документ не загружен, повторите попытку.")
        elif message.caption is None:
            bot.send_message(chat_id, "Повторите попытку, написав направление и курс.")
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def dir_input(message, msg_id):
    chat_id = message.chat.id
    try:
        course = message.text
        if os.path.exists(f"stud_files/{course}"):
            drs = list_full_path(f"stud_files/{course}")
            # print(drs)
            # splitted_text = util.smart_split(drs, chars_per_string=3000)
            # for text in splitted_text:
            bot.delete_message(chat_id, message.id)
            message = bot.edit_message_text(f"🗂/{message.text}/\n\nВыберите папку:\n{drs}", chat_id=chat_id,
                                            message_id=msg_id, parse_mode="Markdown")
            # message = bot.send_message(chat_id, text, parse_mode="Markdown")
            message = message.wait()
            bot.register_next_step_handler(message, file_input, msg_id, course)
        else:
            bot.send_message(chat_id, "Папка не найдена, повторите еще раз.")
            bot.delete_message(chat_id, msg_id)
            bot.delete_message(chat_id, message.id)
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def file_input(message, msg_id, course):
    chat_id = message.chat.id
    try:
        dir = f"stud_files/{course}/{str(message.text)}"
        drs = list_full_files(dir)
        # print(drs)
        if os.path.exists(dir):
            # splitted_text = util.smart_split(drs, chars_per_string=3000)
            # for text in splitted_text:
            bot.delete_message(chat_id, message.id)

            message = bot.edit_message_text(f"🗂/{course}/{message.text}/\n\nВыберите файл:\n{drs}", chat_id=chat_id,
                                            message_id=msg_id, parse_mode="Markdown")
            # message = bot.send_message(chat_id, text, parse_mode="Markdown")
            message = message.wait()
            bot.register_next_step_handler(message, file_download, msg_id, dir)
        else:
            bot.send_message(chat_id, "Файл не найден, повторите еще раз.")
            bot.delete_message(chat_id, msg_id)
            bot.delete_message(chat_id, message.id)
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def file_download(message, msg_id, dir):
    chat_id = message.chat.id
    try:
        doc = open(f"{dir}/{message.text}", 'rb')
        task1 = bot.send_message(chat_id, "Отправка файла📨")
        task2 = bot.send_document(chat_id, doc)
        task1 = task1.wait()
        task2.wait()
        doc.close()
        task11 = bot.delete_message(chat_id, task1.id)
        task11.wait()
        task22 = bot.delete_message(chat_id, msg_id)
        task22.wait()
        task33 = bot.delete_message(chat_id, message.id)
        task33.wait()
    except FileNotFoundError:
        bot.send_message(chat_id, "Файл не найден, повторите еще раз.")
        bot.delete_message(chat_id, msg_id)
        bot.delete_message(chat_id, message.id)
    except NotADirectoryError:
        bot.send_message(chat_id, "Файл не найден, повторите еще раз.")
        bot.delete_message(chat_id, msg_id)
        bot.delete_message(chat_id, message.id)
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def student_input(message):
    chat_id = message.chat.id
    try:
        student_num = str(message.text)[:-21]
        date1 = str(message.text)[-21:-11]
        # print(message.text)
        date2 = str(message.text)[-10:]
        r1 = requests.get(f'https://ruz.hse.ru/api/search?term={student_num}&type=student')
        # print(date1, date2)
        # print(room_num)
        students = "Выберите номер из списка:\n\n"
        # print(len(r1.json()))
        if len(message.text) >= 22:
            if r1.status_code == 200:
                if len(r1.json()) != 0:
                    for i in range(len(r1.json())):
                        students = students + f"🤓({i + 1}) {r1.json()[i]['label']}\n{r1.json()[i]['description']}\n\n"
                    message = bot.send_message(chat_id, students)
                    message = message.wait()
                    msg_id = message.id
                    bot.register_next_step_handler(message, sev_students, r1, date1, date2, msg_id)
                else:
                    bot.send_message(chat_id, "Студент не найден, проверьте ФИО.")

            else:
                bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        else:
            bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def room_input(message):
    chat_id = message.chat.id
    try:
        room_num = str(message.text)[:-21]
        date1 = str(message.text)[-21:-11]
        # print(message.text)
        date2 = str(message.text)[-10:]
        r1 = requests.get(f'https://ruz.hse.ru/api/search?term={room_num}&type=auditorium')
        # print(date1, date2)
        # print(room_num)
        rooms = "Выберите номер из списка:\n\n"
        # print(len(r1.json()))
        if len(message.text) >= 22:
            if r1.status_code == 200:
                if len(r1.json()) != 0:
                    for i in range(len(r1.json())):
                        rooms = rooms + f"🚪({i + 1}) {r1.json()[i]['label']}\n{r1.json()[i]['description']}\n\n"
                    message = bot.send_message(chat_id, rooms)
                    message = message.wait()
                    msg_id = message.id
                    bot.register_next_step_handler(message, sev_rooms, r1, date1, date2, msg_id)
                else:
                    bot.send_message(chat_id, "Аудитория не найдена, проверьте номер.")
            else:
                bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        else:
            bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def group_input(message):
    chat_id = message.chat.id
    try:
        group_num = str(message.text)[:-21]
        date1 = str(message.text)[-21:-11]
        # print(message.text)
        date2 = str(message.text)[-10:]
        # print(date1, date2)
        r1 = requests.get(f'https://ruz.hse.ru/api/search?term={group_num}&type=group')
        # print(group_num)
        groups = "Выберите номер из списка:\n\n"
        if len(message.text) >= 22:
            if r1.status_code == 200:
                if len(r1.json()) != 0:
                    for i in range(len(r1.json())):
                        groups = groups + f"👥({i + 1}) {r1.json()[i]['label']}\n{r1.json()[i]['description']}\n\n"
                    message = bot.send_message(chat_id, groups)
                    message = message.wait()
                    msg_id = message.id
                    bot.register_next_step_handler(message, sev_groups, r1, date1, date2, msg_id)
                else:
                    bot.send_message(chat_id, "Группа не найдена, проверьте номер.")
            else:
                bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        else:
            bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def prepod_input(message):
    chat_id = message.chat.id
    try:
        # print(str(message.text)[-22:])
        # print(str(message.text)[:-22])
        # print(r1.json())
        # print(message.text)
        date = str(message.text)[-21:]
        # print(date)
        date1 = str(date)[:10]
        # print(date1, '||')
        date2 = str(date)[11:]
        # print(date2)
        # print(str(message.text)[:-22])
        r1 = requests.get(f'https://ruz.hse.ru/api/search?term={str(message.text)[:-22]}&type=person')
        prepods = "Выберите номер из списка:\n\n"
        if len(message.text) >= 22:
            # print(r1.status_code, r1.json())
            if r1.status_code == 200:
                if len(r1.json()) != 0:
                    for i in range(len(r1.json())):
                        prepods = prepods + f"👨‍🏫({i + 1}) {r1.json()[i]['label']}\n{r1.json()[i]['description']}\n\n"
                    message = bot.send_message(chat_id, prepods)
                    message = message.wait()
                    msg_id = message.id
                    bot.register_next_step_handler(message, sev_preps, r1, date1, date2, msg_id)
                else:
                    bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
            else:
                bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        else:
            bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def parse_schedule(chat_id, r):
    try:
        # print(len(r.json()), 10)
        chkerr = str(r.text)[:7]
        chkerr = chkerr[2:]
        # print(chkerr)
        # print(r.json())
        if chkerr != "error":
            if len(r.json()) != 0:
                rasp_str = ''
                date = ''
                #print(len(r.json()))
                for i in range(len(r.json())):
                    if date != r.json()[i]['date']:
                        date = r.json()[i]['date']
                        rasp_str = rasp_str + f"\n<u>🗓{datetime.strptime(date, '%Y.%m.%d').strftime('%d.%m')}</u> (<i>{r.json()[i]['dayOfWeekString']}</i>)\n"
                    ptype = r.json()[i]['kindOfWork']
                    aud = str(r.json()[i]['auditorium'])
                    if str(ptype) == "Лекция Online" or str(ptype) == "Лекция":
                        ptype = "Лек"
                    elif str(ptype) == "Практическое занятие" or str(ptype) == "Практическое занятие Online":
                        ptype = "Прак"
                    elif str(ptype) == "Семинар" or str(ptype) == "Семинар Online":
                        ptype = "Сем"
                    else:
                        ptype = ptype
                    type = str(r.json()[i]['auditorium'])
                    #print(type)
                    #print(type == "On-line" or type == "on-line" or type == "On-Line")
                    if type.find("On-line") != -1 or type.find("on-line") != -1 or type.find("On-Line") != -1 or type.find("Online") != -1 or type.find("online") != -1:
                        aud = "🌐"
                    if r.json()[i]["url1"] is not None:
                        if len(r.json()[i]["url1"]) != 0:
                            link = f"<a href='{r.json()[i]['url1']}'>🔗</a>"
                            rasp_str = rasp_str + f"🕐<b>{r.json()[i]['lessonNumberStart']} [{r.json()[i]['beginLesson']}] </b>{str(r.json()[i]['discipline'])[:-6]} <i>{ptype}</i>|{aud} {link}\n"
                        else:
                            rasp_str = rasp_str + f"🕐<b>{r.json()[i]['lessonNumberStart']} [{r.json()[i]['beginLesson']}] </b>{str(r.json()[i]['discipline'])[:-6]} <i>{ptype}</i>|{aud}\n"
                    else:
                        rasp_str = rasp_str + f"🕐<b>{r.json()[i]['lessonNumberStart']} [{r.json()[i]['beginLesson']}] </b>{str(r.json()[i]['discipline'])[:-6]} <i>{ptype}</i>|{aud}\n"
                splitted_text = util.smart_split(rasp_str, chars_per_string=3000)
                for text in splitted_text:
                    message = bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=hide_schedule_keyboard(), disable_web_page_preview=True)
                    message.wait()
                # bot.send_message(chat_id, rasp_str)
            else:
                bot.send_message(chat_id, 'Расписание не найдено, выберите другой период.')
        elif chkerr == "error":
            bot.send_message(chat_id, 'Произошла ошибка, повторите попытку еще раз.')

        else:
            bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
    # except KeyError:
    #    bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def get_newsletter(message):
    usr_list = get_all_users()
    # print(usr_list)
    try:
        cpt = message.caption
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        file_info = file_info.wait()
        pinned_file = bot.download_file(file_info.file_path)
        pinned_file = pinned_file.wait()
        k = 0
        for usr in usr_list:
            task = bot.send_photo(usr[0], pinned_file, caption=cpt, parse_mode="Markdown")
            # print(pinned_file)
            # print(cpt)
            task.wait()
            k += 1
        bot.reply_to(message, f"Сообщение успешно разослано *{k}* пользователям!", parse_mode="Markdown")
    except TypeError:
        k = 0
        for usr in usr_list:
            # print(usr, usr[0])
            task = bot.send_message(usr[0], message.text, parse_mode="Markdown")
            task.wait()
            k += 1

        bot.reply_to(message, f"Сообщение успешно разослано *{k}* пользователям!", parse_mode="Markdown")
    except Exception as e:
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def get_schedule(date1, date2, chat_id, ruz_id):
    try:
        payload = {'start': date1, 'finish': date2, 'lng': 1}
        r1 = requests.get(f'https://ruz.hse.ru/api/schedule/student/{ruz_id}?', params=payload)
        # print(date1, date2, ruz_id)
        # print(r1.json())
        parse_schedule(chat_id, r1)
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def get_feedback(message, pmsg):
    chat_id = message.chat.id
    try:
        link = f'[{str(message.from_user.first_name)}](tg://user?id={str(message.chat.id)})'
        msg = message
        user_str = '👤Профиль\n\nВы зарегистрированы: '
        info = get_user_info(chat_id)
        # print(info[1])
        user_str = user_str + info[0] + '.\n\nВами загружено ' + info[1] + ' файлов.'
        if message.photo is not None:
            cpt = message.caption
            # print(str(cpt))
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            file_info = file_info.wait()
            pinned_file = bot.download_file(file_info.file_path)
            pinned_file = pinned_file.wait()
            splitted_text = util.smart_split(str(cpt), chars_per_string=3000)
            for text in splitted_text:
                message = bot.send_photo(admin_id, pinned_file,
                                         caption=f"Сообщение от пользователя {link} (`{chat_id}`) - {str(datetime.time(datetime.today()))[:8]}\n\n{text}",
                                         parse_mode="Markdown", reply_markup=feedback_keyboard())
                message.wait()

            bot.edit_message_text(user_str, chat_id=chat_id, message_id=pmsg, reply_markup=profile_keyboard())
            bot.reply_to(msg, "Сообщение успешно отправлено!")
        else:
            splitted_text = util.smart_split(message.text, chars_per_string=3000)
            for text in splitted_text:
                message = bot.send_message(admin_id,
                                           f"Сообщение от пользователя {link}(`{chat_id}`) - {str(datetime.time(datetime.today()))[:8]}\n\n{text}",
                                           parse_mode="Markdown", reply_markup=feedback_keyboard())
                message.wait()
            bot.edit_message_text(user_str, chat_id=chat_id, message_id=pmsg, reply_markup=profile_keyboard())
            bot.reply_to(msg, "Сообщение успешно отправлено!")
            # repl.wait()
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def id_reply(message):
    chat_id = message.chat.id
    try:
        rep_id = message.text
        message = bot.send_message(chat_id, "Сообщение с 1 картинкой:")
        message = message.wait()
        bot.register_next_step_handler(message, send_reply, rep_id)
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def user_send(message):
    chat_id = message.chat.id
    try:
        rep_id = message.text
        message = bot.send_message(chat_id, "Сообщение с 1 картинкой:")
        message = message.wait()
        bot.register_next_step_handler(message, send_reply, rep_id)
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def send_reply(message, rep_id):
    try:
        cpt = message.caption
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        file_info = file_info.wait()
        pinned_file = bot.download_file(file_info.file_path)
        pinned_file = pinned_file.wait()
        bot.send_photo(rep_id, pinned_file,
                       caption=f"Сообщение от *админа*:\n\n{cpt}",
                       parse_mode="Markdown")
        bot.reply_to(message, "Сообщение успешно отправлено!")
    except TypeError:
        bot.send_message(rep_id,
                         f"Сообщение от *админа*:\n\n{message.text}",
                         parse_mode="Markdown")
        bot.reply_to(message, "Сообщение успешно отправлено!")
    except Exception as e:
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def get_ruz_id(message):
    chat_id = message.chat.id
    msg_id = message.id
    # print(str(message.text))
    try:
        if str(message.text) != "None":

            fio = str(message.text)
            r1 = requests.get(f'https://ruz.hse.ru/api/search?term={fio}&type=student')
            if r1.status_code == 200:
                if len(r1.json()) == 1:
                    one_person_ruz(chat_id, r1)
                elif len(r1.json()) == 0:
                    bot.send_message(chat_id, "Студентов с таким ФИО не найдено!", reply_markup=fio_keyboard())
                else:
                    students = "Найдено несколько студентов с таким ФИО, выберите номер из списка:\n\n"
                    for i in range(len(r1.json())):
                        students = students + f"👤({i + 1}) {r1.json()[i]['label']}\n{r1.json()[i]['description']}\n\n"
                    # print(students)
                    message = bot.send_message(chat_id, students)
                    message = message.wait()
                    bot.register_next_step_handler(message, sev_person_ruz, r1, msg_id, message.id)
            else:
                bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        else:
            bot.edit_message_text("❌Ошибка при регистрации! Повторите попытку еще раз.", chat_id=chat_id,
                                  message_id=msg_id,
                                  reply_markup=fio_keyboard())
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def one_person_ruz(chat_id, r1):
    try:
        st_id = r1.json()[0]['id']
        # print(st_id)
        up_ruz_id(st_id, chat_id)
        bot.send_message(chat_id,
                         f"👋{r1.json()[0]['label']}, Вы успешно зарегистрированы!\nВоспользуйтесь кнопками для "
                         f"навигации по боту.",
                         reply_markup=main_keyboard())
    except Exception as e:
        bot.send_message(chat_id, "❌Ошибка при регистрации! Повторите попытку еще раз.", reply_markup=fio_keyboard())
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def sev_person_ruz(message, r1, msg_id, pmsg_id):
    chat_id = message.chat.id
    # print(admin_id, chat_id)
    try:
        if message.text.isdigit():
            num = int(message.text) - 1
            if 0 <= num <= len(r1.json()) - 1:
                st_id = r1.json()[num]['id']
                # print(st_id)
                up_ruz_id(st_id, chat_id)
                # task = bot.edit_message_text(f"👋{r1.json()[num]['label']}, Вы успешно зарегистрированы!\nВоспользуйтесь кнопками для навигации по боту.", chat_id=chat_id, message_id=pmsg_id, reply_markup=profile_keyboard())
                task1 = bot.send_message(chat_id,
                                         f"👋{r1.json()[num]['label']}, Вы успешно зарегистрированы!\nВоспользуйтесь кнопками для навигации по боту.",
                                         reply_markup=main_keyboard())
                task2 = bot.delete_message(chat_id, pmsg_id)
                task3 = bot.delete_message(chat_id, message.id)
                task1.wait()
                task2.wait()
                task3.wait()
            else:
                task1 = bot.edit_message_text("❌Ошибка при регистрации! Повторите попытку еще раз.", chat_id=chat_id,
                                              message_id=pmsg_id,
                                              reply_markup=fio_keyboard())
                task2 = bot.delete_message(chat_id, message.id)
                task1.wait()
                task2.wait()
        else:
            task1 = bot.edit_message_text("❌Ошибка при регистрации! Повторите попытку еще раз.", chat_id=chat_id,
                                          message_id=msg_id,
                                          reply_markup=fio_keyboard())
            task2 = bot.delete_message(message.chat.id, message.message_id)
            task1.wait()
            task2.wait()
    except ValueError as e:
        print(trcb.format_exc(e))
        task1 = bot.edit_message_text("❌Ошибка при регистрации! Повторите попытку еще раз.", chat_id=chat_id,
                                      message_id=msg_id,
                                      reply_markup=fio_keyboard())
        task2 = bot.delete_message(message.chat.id, message.message_id)
        task1.wait()
        task2.wait()
    except Exception as e:
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))
        task1 = bot.edit_message_text("❌Ошибка при регистрации! Повторите попытку еще раз.", chat_id=chat_id,
                                      message_id=msg_id,
                                      reply_markup=fio_keyboard())
        task2 = bot.delete_message(message.chat.id, message.message_id)
        task1.wait()
        task2.wait()


def sev_rooms(message, r1, date1, date2, msg_id):
    chat_id = message.chat.id
    try:
        if str(message.text).isdigit():
            num = int(message.text) - 1
            if 0 <= num <= len(r1.json()) - 1:
                rm_id = r1.json()[num]['id']
                # print(rm_id)
                payload = {'start': date1, 'finish': date2, 'lng': 1}
                r2 = requests.get(f'https://ruz.hse.ru/api/schedule/auditorium/{rm_id}?', params=payload)
                # print(date1, date2, r2.text)
                bot.delete_message(chat_id, msg_id)
                bot.delete_message(chat_id, message.id)
                parse_schedule(chat_id, r2)
            else:
                bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
                bot.delete_message(chat_id, msg_id)
                bot.delete_message(chat_id, message.id)
        else:
            bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
            bot.delete_message(chat_id, msg_id)
            bot.delete_message(chat_id, message.id)
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def sev_students(message, r1, date1, date2, msg_id):
    chat_id = message.chat.id
    try:
        if str(message.text).isdigit():
            num = int(message.text) - 1
            # print(len(r1.json()), num)
            if 0 <= num <= len(r1.json()) - 1:
                st_id = r1.json()[num]['id']
                # print(gr_id)
                bot.delete_message(chat_id, msg_id)
                bot.delete_message(chat_id, message.id)
                get_schedule(date1, date2, chat_id, st_id)
                # payload = {'start': date1, 'finish': date2, 'lng': 1}
                # r2 = requests.get(f'https://ruz.hse.ru/api/schedule/group/{st_id}?', params=payload)
                # print(date1, date2, r2.text)
                # parse_schedule(message.chat.id, r2)
            else:
                bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
                bot.delete_message(chat_id, msg_id)
                bot.delete_message(chat_id, message.id)
        else:
            bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
            bot.delete_message(chat_id, msg_id)
            bot.delete_message(chat_id, message.id)
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def sev_groups(message, r1, date1, date2, msg_id):
    chat_id = message.chat.id
    try:
        if str(message.text).isdigit():
            num = int(message.text) - 1
            if 0 <= num <= len(r1.json()) - 1:
                gr_id = r1.json()[num]['id']
                # print(gr_id)
                payload = {'start': date1, 'finish': date2, 'lng': 1}
                r2 = requests.get(f'https://ruz.hse.ru/api/schedule/group/{gr_id}?', params=payload)
                # print(date1, date2, r2.text)
                bot.delete_message(chat_id, msg_id)
                bot.delete_message(chat_id, message.id)
                parse_schedule(chat_id, r2)
            else:
                bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
                bot.delete_message(chat_id, msg_id)
                bot.delete_message(chat_id, message.id)
        else:
            bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
            bot.delete_message(chat_id, msg_id)
            bot.delete_message(chat_id, message.id)
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


def sev_preps(message, r1, date1, date2, msg_id):
    chat_id = message.chat.id
    try:
        if str(message.text).isdigit():
            num = int(message.text) - 1
            if 0 <= num <= len(r1.json()) - 1:
                pr_id = r1.json()[num]['id']
                # print(date1, date2)
                payload = {'start': date1, 'finish': date2, 'lng': 1}
                r2 = requests.get(f'https://ruz.hse.ru/api/schedule/person/{pr_id}?', params=payload)
                # print(date1, date2, r2.json())
                bot.delete_message(chat_id, msg_id)
                bot.delete_message(chat_id, message.id)
                parse_schedule(chat_id, r2)
            else:
                bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
                bot.delete_message(chat_id, msg_id)
                bot.delete_message(chat_id, message.id)
        else:
            bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
            bot.delete_message(chat_id, msg_id)
            bot.delete_message(chat_id, message.id)
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка, повторите еще раз.")
        err1 = str(trcb.format_exc())[84:]
        err1 = err1.split('\n')[:-1][0]
        err2 = str(trcb.format_exc())
        err2 = err2.split('\n')[-2:][0]
        logger.error(f"{err1} {err2}")
        print(str(trcb.format_exc()))


if __name__ == '__main__':
   try:
       bot.polling(True)
   except: #Exception as e:
       err1 = str(trcb.format_exc())[84:]
       err1 = err1.split('\n')[:-1][0]
       err2 = str(trcb.format_exc())
       err2 = err2.split('\n')[-2:][0]
       logger.error(f"{err1} {err2}")
       print(str(trcb.format_exc()))
       bot.polling(True)
