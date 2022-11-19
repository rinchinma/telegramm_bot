from loader import bot
from states.state_for_lowprice import UserInfoState
from telebot.types import Message
from loguru import logger
from keyboards.inline.buttons import quantity_hotels_markup


@bot.message_handler(state=UserInfoState.min_price)
@logger.catch
def min_price(message: Message) -> None:
    if message.text.isdigit():
        bot.send_message(message.from_user.id, 'Теперь введите максимальную стоимость отеля за ночь:')
        bot.set_state(message.from_user.id, UserInfoState.max_price, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['min_price'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста, введите число')


@bot.message_handler(state=UserInfoState.max_price)
@logger.catch
def max_price(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as bot_data:
        if message.text.isdigit() and int(bot_data['min_price']) < int(message.text):
            bot_data['max_price'] = message.text
            bot.send_message(message.from_user.id, '🖊Спасибо! Укажите минимальное расстояние от центра города '
                                                   '(в киломертах)')
            bot.set_state(message.from_user.id, UserInfoState.min_distance, message.chat.id)
        else:
            bot.send_message(message.from_user.id, 'Пожалуйста, введите число')


@bot.message_handler(state=UserInfoState.min_distance)
@logger.catch
def min_distance(message: Message) -> None:
    if message.text.isdigit() or message.text.find(',' or '.'):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['min_distance'] = message.text

        bot.send_message(message.from_user.id, 'Теперь укажите максимальное расстояние от центра города '
                                               '(в киломертах)')
        bot.set_state(message.from_user.id, UserInfoState.max_distance, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста, введите число')


@bot.message_handler(state=UserInfoState.max_distance)
@logger.catch
def max_distance(message: Message) -> None:
    if message.text.isdigit() or message.text.find(',' or '.'):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as bot_data:
            bot_data['max_distance'] = message.text
            if float(bot_data['min_distance']) < float(bot_data['max_distance']):
                bot.send_message(message.chat.id, 'Сколько отелей показать?',
                                 reply_markup=quantity_hotels_markup())
                bot.set_state(message.from_user.id, UserInfoState.photo_y_n, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста, введите число')
















