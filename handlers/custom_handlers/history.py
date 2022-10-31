import re
from loader import bot
from loguru import logger
from database.models import HistoryUsers


def database_request(user_id):
    # запрос к базе данных

    return HistoryUsers.select().where(HistoryUsers.id_user == user_id)


@bot.message_handler(commands=['history'])
@logger.catch
def history(message):
    for row in database_request(message.from_user.id):
        text = row.result_command
        hotels_result = re.sub(r'_', '\n', text)
        bot.send_message(message.chat.id, 'Город: {city}\nКоманда: {command}\nДата: {date}\n'
                                          'Результат:\n{result}'.format(city=row.chosen_city,
                                                                        command=row.command_choice,
                                                                        date=row.date,
                                                                        result=hotels_result),
                         disable_web_page_preview=True)



