import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from datetime import datetime

# Замените на токен вашего бота
TOKEN = 'ТОКЕН ВАШЕГО БОТА'
# Замените на ID вашего чата (должен быть int, а не str)
CHAT_ID = -12345678  # Пример ID чата
# Замените на ID владельца бота
OWNER_ID = 12345678  # Пример ID владельца бота

bot = telebot.TeleBot(TOKEN)
scheduler = BackgroundScheduler()
scheduler.start()

# Проверка, является ли пользователь владельцем бота
def is_owner(message):
    return message.from_user.id == OWNER_ID and message.chat.type == 'private'

# Функция для планирования сообщений
def schedule_message_to_chat(chat_id, text, schedule_time):
    # Установка часового пояса для времени отправки
    tz = timezone('Asia/Yekaterinburg')
    schedule_time = tz.localize(schedule_time)
    # Планирование сообщения
    scheduler.add_job(bot.send_message, 'date', run_date=schedule_time, args=[chat_id, text])

# Обработчик команды для планирования сообщения
@bot.message_handler(commands=['schedule'])
def handle_schedule(message):
    if is_owner(message):
        msg = bot.send_message(message.chat.id, "Введите время сообщения в формате YYYY-MM-DD HH:MM")
        bot.register_next_step_handler(msg, get_datetime_for_message)
    else:
        bot.send_message(message.chat.id, "У вас нет прав на выполнение этой команды.")

# Получение даты и времени сообщения
def get_datetime_for_message(message):
    try:
        send_time = datetime.strptime(message.text, '%Y-%m-%d %H:%M')
        # Запрос текста сообщения
        msg = bot.send_message(message.chat.id, "Введите текст сообщения")
        bot.register_next_step_handler(msg, send_scheduled_message, send_time)
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат времени. Попробуйте еще раз.")

# Отправка запланированного сообщения
def send_scheduled_message(message, send_time):
    schedule_message_to_chat(CHAT_ID, message.text, send_time)
    bot.send_message(message.chat.id, "Сообщение запланировано.")

# Планирование автоматических сообщений
scheduler.add_job(lambda: bot.send_message(CHAT_ID, "Это сообщение на каждый понедельник"), 'cron', day_of_week='mon', hour=9, minute=0, timezone=timezone('Asia/Yekaterinburg'))
scheduler.add_job(lambda: bot.send_message(CHAT_ID, "Это сообщение на каждое первое число месяца"), 'cron', day=1, hour=9, minute=0, timezone=timezone('Asia/Yekaterinburg'))

# Функция для отправки тестового сообщения
@bot.message_handler(commands=['test'])
def send_test_message(message):
    if is_owner(message):
        bot.send_message(CHAT_ID, "Тестовое сообщение")
    else:
        bot.send_message(message.chat.id, "У вас нет прав на выполнение этой команды.")

# Функция для отображения списка запланированных сообщений
@bot.message_handler(commands=['check_schedule'])
def check_schedule(message):
    if is_owner(message):
        jobs = scheduler.get_jobs()
        if jobs:
            response = "Запланированные сообщения:\n"
            for job in jobs:
                response += f"{job.id} - {job.next_run_time}: {job.args[1]}\n"
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "Нет запланированных сообщений.")
    else:
        bot.send_message(message.chat.id, "У вас нет прав на выполнение этой команды.")

if __name__ == '__main__':
    bot.polling(none_stop=True)