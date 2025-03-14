import telebot
from telebot import types
from database import *

API_TOKEN = API_token
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if is_admin(user_id):
        bot.send_message(
            message.chat.id,
            "Привіт! Я допоможу Вам створювати посилання та відслідковувати переходи.\n\n"
            "Для початку оберіть одну з опцій нижче.",
            reply_markup=main_menu())
    else:
        pass

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Створити посилання")
    item2 = types.KeyboardButton("Переглянути статистику")
    item3 = types.KeyboardButton("Управління адмінами")
    item4 = types.KeyboardButton("Управління лінками")
    markup.add(item1, item2, item3, item4)
    return markup



# Створення посилань
@bot.message_handler(func=lambda message: message.text == "Створити посилання")
def create_link(message):
    msg = bot.send_message(message.chat.id, "Уведіть оригінальну URL-адресу:")
    bot.register_next_step_handler(msg, get_original_url)

def get_original_url(message):
    original_url = message.text
    msg = bot.send_message(message.chat.id, "Уведіть домен для редиректу:")
    bot.register_next_step_handler(msg, lambda msg: get_domain_name(msg, original_url))

def get_domain_name(message, original_url):
    domain_name = message.text
    msg = bot.send_message(message.chat.id, "Уведіть назву URL:")
    bot.register_next_step_handler(msg, lambda msg: get_name_URL(msg, original_url, domain_name))

def get_name_URL(message, original_url, domain_name):
    name_url = message.text
    if "youtube" in original_url:
        short_url = "https://"+ domain_name + "/?watch=" + original_url[32:]
    else:
        bot.send_message(message.chat.id, "Це доменне ім'я наразі не обслуговується")
    user_id = message.from_user.id
    id_admin = get_id(user_id)

    if id_admin:
        save_link_to_db(name_url, original_url, short_url, domain_name, id_admin)
        bot.send_message(message.chat.id, f"Посилання створено: {short_url}")
    else:
        bot.send_message(message.chat.id, "Виникла помилка при збереженні посилання.")



# Перегляд статистики

@bot.message_handler(func=lambda message: message.text == "Переглянути статистику")
def view_statistics(message):
    links = get_links()
    if links:
        stats_message = "Статистика по лінках:\n\n"
        for link in links:
            link_id = link[0]
            original_url = link[2]
            transition_count = get_transition_count(original_url)
            stats_message += f"ID: {link_id}, URL: {original_url}, Переходи: {transition_count}\n"

        bot.send_message(message.chat.id, stats_message)
    else:
        bot.send_message(message.chat.id, "Лінки не знайдені.")

    bot.send_message(message.chat.id, "Виберіть опцію:", reply_markup=main_menu())


# Управління лінками
@bot.message_handler(func=lambda message: message.text == "Управління лінками")
def manage_links(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Переглянути список лінків")
    item2 = types.KeyboardButton("Дія з лінком")
    item3 = types.KeyboardButton("Назад у меню")
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, "Виберіть опцію:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Переглянути список лінків")
def view_links(message):
    links = get_links()
    if links:
        links_list = "\n".join([f"ID: {link[0]}, ім'я посилання: {link[1]}, посилання: {link[2]}" for link in links])
        bot.send_message(message.chat.id, f"Список лінків:\n{links_list}")
    else:
        bot.send_message(message.chat.id, "Лінки не знайдені.")
    bot.send_message(message.chat.id, "Виберіть опцію:", reply_markup=manage_links_menu())


@bot.message_handler(func=lambda message: message.text == "Дія з лінком")
def do_link(message):
    user_id = message.from_user.id
    if check_admin(user_id):
        msg = bot.send_message(message.chat.id, "Уведіть ID лінки для перевірки статусу:")
        bot.register_next_step_handler(msg, process_link_id_for_archiving)
    else:
        bot.send_message(message.chat.id, "Доступ до цієї функції обмежено.")

def process_link_id_for_archiving(message):
    link_id = message.text

    if not link_id.isdigit():
        bot.send_message(message.chat.id, "Будь ласка, введіть правильний ID лінки.")
        return

    link_data = get_link_by_id(link_id)

    if link_data:
        arch_status = link_data[0]
        if arch_status == 0:
            bot.send_message(message.chat.id, f"Лінка з ID {link_id} є активною.")
        elif arch_status == 1:
            bot.send_message(message.chat.id, "Ця лінка вже архівована.")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Архівувати лінк")
        item2 = types.KeyboardButton("Розархівувати лінк")
        item3 = types.KeyboardButton("Видалити лінк")
        item4 = types.KeyboardButton("Назад у меню")
        markup.add(item1, item2, item3, item4)

        bot.send_message(message.chat.id, "Виберіть дію з лінком:", reply_markup=markup)
        bot.register_next_step_handler(message, handle_link_action, link_id, arch_status)

    else:
        bot.send_message(message.chat.id, "Лінка з таким ID не знайдена.")
        bot.send_message(message.chat.id, "Виберіть опцію:", reply_markup=manage_links_menu())\

def handle_link_action(message, link_id, arch_status):
    action = message.text

    if action == "Архівувати лінк":
        if arch_status == 0:
            update_link_arch_status(link_id, 1)
            bot.send_message(message.chat.id, f"Лінка з ID {link_id} була успішно архівована!")
        elif arch_status == 1:
            bot.send_message(message.chat.id, "Ця лінка вже архівована.")

    elif action == "Розархівувати лінк":
        if arch_status == 0:
            bot.send_message(message.chat.id, "Ця лінка вже активна.")
        elif arch_status == 1:
            update_link_arch_status(link_id, 0)
            bot.send_message(message.chat.id, f"Лінка з ID {link_id} була успішно розархівована й доступна знову!")

    elif action == "Видалити лінк":
        delete_link(link_id)
        bot.send_message(message.chat.id, f"Лінка з ID {link_id} була успішно видалена!")

    bot.send_message(message.chat.id, "Виберіть опцію:", reply_markup=manage_links_menu())

def manage_links_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Переглянути список лінків")
    item2 = types.KeyboardButton("Дія з лінком")
    item3 = types.KeyboardButton("Назад у меню")
    markup.add(item1, item2, item3)
    return markup



# Адмін-панель
@bot.message_handler(func=lambda message: message.text == "Управління адмінами")
def manage_admins(message):
    user_id = message.from_user.id
    if check_admin(user_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Переглянути список адмінів")
        item2 = types.KeyboardButton("Додати адміна")
        item3 = types.KeyboardButton("Назад у меню")
        markup.add(item1, item2, item3)
        bot.send_message(message.chat.id, "Виберіть опцію:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Доступ до цієї функції обмежено.")


@bot.message_handler(func=lambda message: message.text == "Переглянути список адмінів")
def view_admins(message):
    admins = get_admins()
    if admins:
        admin_list = ""
        for admin in admins:
            super_admin_status = "Супер адмін" if admin[3] == 1 else "Адмін"
            admin_list += f"ID: {admin[0]}, ім'я адміна: {admin[1]}, TG_ID: {admin[2]}, статус: {super_admin_status}\n"
        bot.send_message(message.chat.id, f"Список адмінів:\n{admin_list}")
    else:
        bot.send_message(message.chat.id, "Адміни не знайдені.")
    bot.send_message(message.chat.id, "Виберіть опцію:", reply_markup=manage_admins_menu())


@bot.message_handler(func=lambda message: message.text == "Додати адміна")
def add_admin_handler(message):
    bot.send_message(message.chat.id, "Уведіть ім'я нового адміна:")
    bot.register_next_step_handler(message, get_admin_name)

def get_admin_name(message):
    admin_name = message.text
    bot.send_message(message.chat.id, "Уведіть ID Telegram адміна:")
    bot.register_next_step_handler(message, lambda msg: get_admin_id(msg, admin_name))

def get_admin_id(message, admin_name):
    id_telegram = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Так")
    item2 = types.KeyboardButton("Ні")
    markup.add(item1, item2)

    bot.send_message(message.chat.id, "Надати роль супер адміна?", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: get_super_admin_status(msg, admin_name, id_telegram, markup))

def get_super_admin_status(message, admin_name, id_telegram, markup):
    super_admin = 0
    if message.text == "Так":
        super_admin = 1
    markup_remove = types.ReplyKeyboardRemove()

    success, error_message = add_admin(admin_name, id_telegram, super_admin)
    if success:
        bot.send_message(message.chat.id,
                         f"Адміна {admin_name} з ID {id_telegram} було успішно додано! Роль: {'Супер адмін' if super_admin == 1 else 'Адмін'}")
    else:
        bot.send_message(message.chat.id, f"Сталася помилка при додаванні адміна!")

    bot.send_message(message.chat.id, "Виберіть опцію:", reply_markup=manage_admins_menu())


@bot.message_handler(func=lambda message: message.text == "Назад у меню")
def back_to_main_menu(message):
    bot.send_message(message.chat.id, "Переміщаємо в основне меню", reply_markup=main_menu())

def manage_admins_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Переглянути список адмінів")
    item2 = types.KeyboardButton("Додати адміна")
    item3 = types.KeyboardButton("Назад у меню")
    markup.add(item1, item2, item3)
    return markup


bot.polling()