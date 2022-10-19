from rapid_api import city_founding
from keyboards.inline.buttons import city_markup, quantity_hotels_markup, \
    photo_y_n_markup, quantity_photo_markup
from loader import bot
from states.state_for_lowprice import UserInfoState
from loguru import logger


@bot.message_handler(commands=['low_price', 'high_price', 'bestdeal'])
@logger.catch
def start(message):
    bot.set_state(message.from_user.id, UserInfoState.command, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = message.text[1:]

    bot.send_message(message.chat.id, 'В какой город направляетесь?')
    bot.register_next_step_handler(message, city)


@bot.message_handler(state=UserInfoState.city)
@logger.catch
def city(message):
    # список районов города

    cities_list = city_founding(message.text)
    if cities_list is not None:
        bot.send_message(message.chat.id, 'Уточните, пожалуйста, район города:',
                         reply_markup=city_markup(cities_list))
        bot.set_state(message.from_user.id, UserInfoState.quantity_hotels, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text
    else:
        bot.send_message(message.chat.id, 'Извините, не могу найти такой город! '
                                          'Пожалуйста, проверьте правильность написания города.')


@bot.message_handler(state=UserInfoState.quantity_hotels)
@bot.callback_query_handler(func=lambda call: call.data.endswith('_1'))
@logger.catch
def quantity_hotels(call):
    # сохраняет id района города
    # запрашивает количество отелей

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['city_area_id'] = call.data[:-2]

        if data['command'] == 'bestdeal':
            bot.send_message(call.message.chat.id, 'Введите, пожалуйста, минимальную стоимость отеля за ночь:')
            bot.set_state(call.from_user.id, UserInfoState.min_price, call.message.chat.id)
        else:
            bot.send_message(call.message.chat.id, 'Сколько отелей показать?',
                             reply_markup=quantity_hotels_markup())
            bot.set_state(call.message.from_user.id, UserInfoState.photo_y_n, call.message.chat.id)


@bot.message_handler(state=UserInfoState.photo_y_n)
@bot.callback_query_handler(func=lambda call: call.data.endswith('_2'))
def photo_y_n(call):
    # сохраняет количество отелей
    # фото отелей

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['quantity_hotels'] = call.data[:-2]

    bot.send_message(call.message.chat.id, 'Показать фото отелей?',
                     reply_markup=photo_y_n_markup())
    bot.set_state(call.message.from_user.id, UserInfoState.quantity_photo, call.message.chat.id)


@bot.message_handler(state=UserInfoState.quantity_photo)
@bot.callback_query_handler(func=lambda call: call.data.endswith('_3'))
def quantity_photo(call):
    # если да - запрашивает количество фото
    # если нет - список отелей

    if call.data[:-2] == 'Да':
        bot.send_message(call.message.chat.id, 'Сколько фото показать?',
                         reply_markup=quantity_photo_markup())
    else:
        pass  # create_hotel_message()

    bot.set_state(call.message.from_user.id, UserInfoState.hotels, call.message.chat.id)


@bot.message_handler(state=UserInfoState.hotels)
@bot.callback_query_handler(func=lambda call: call.data.endswith('_4'))
def hotels(call):
    # сохраняет количество фото
    # список отелей

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['quantity_photo'] = call.data[:-2]

    # bot.send_message(call.message.chat.id, 'Отели в выбранном районе:',
    #                  reply_markup=hotel_markup(data['city_area_id']))






























