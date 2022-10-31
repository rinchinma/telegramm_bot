from rapid_api import city_founding, create_hotel_message
from keyboards.inline.buttons import city_markup, quantity_hotels_markup, \
    photo_y_n_markup, quantity_photo_markup
from loader import bot
from states.state_for_lowprice import UserInfoState
from loguru import logger
from datetime import date
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


@bot.message_handler(commands=['low_price', 'high_price', 'bestdeal'])
@logger.catch
def start(message):
    bot.set_state(message.from_user.id, UserInfoState.command, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = message.text[1:]

    bot.send_message(message.chat.id, 'В какой город направляетесь?')
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)


@bot.message_handler(state=UserInfoState.city)
@logger.catch
def city(message):
    # список районов города

    cities_list = city_founding(message.text)
    if cities_list is not None:
        bot.send_message(message.chat.id, 'Уточните, пожалуйста, район города:',
                         reply_markup=city_markup(cities_list))
        # bot.set_state(message.from_user.id, UserInfoState.quantity_hotels, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text
    else:
        bot.send_message(message.chat.id, 'Извините, не могу найти такой город! '
                                          'Пожалуйста, проверьте правильность написания города.')


@bot.callback_query_handler(func=lambda call: call.data.endswith('_1'))
@logger.catch
def quantity_hotels(call):
    # сохраняет id района города
    # календарь

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['city_area_id'] = call.data[:-2]

    calendar, step = DetailedTelegramCalendar(calendar_id='in',
                                              min_date=date.today(),
                                              max_date=date(2024, 10, 21)).build()

    ru_steps = {'y': 'год', 'm': 'месяц', 'd': 'день'}
    bot.send_message(call.message.chat.id, f'Выберите дату заезда:\n{ru_steps[step]}',
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id='in'))
@logger.catch
def call_back_check_in(call):
    result, key, step = DetailedTelegramCalendar(
        calendar_id='in',
        locale='ru',
        min_date=date.today(),
        max_date=date(2024, 3, 31)
    ).process(call.data)

    ru_steps = {'y': 'год', 'm': 'месяц', 'd': 'день'}

    if not result and key:
        bot.edit_message_text(f"Выберите: {ru_steps[step]}",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Дата заезда: {result}",
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['check_in'] = result

        calendar, step = DetailedTelegramCalendar(
            calendar_id='out',
            min_date=date.today(),
            max_date=date(2024, 3, 31)
        ).build()

        bot.send_message(call.message.chat.id, f'Выберите дату выезда:\n{ru_steps[step]}',
                         reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id='out'))
@logger.catch
def call_back_check_out(call):
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        result, key, step = DetailedTelegramCalendar(
            calendar_id='out',
            locale='ru',
            min_date=data['check_in'],
            max_date=date(2024, 3, 31)).process(call_data=call.data)

    if not result and key:
        ru_steps = {'y': 'год', 'm': 'месяц', 'd': 'день'}
        bot.edit_message_text(f"Выберите {ru_steps[step]}",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Дата выезда: {result}",
                              call.message.chat.id,
                              call.message.message_id)

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['check_out'] = result

            if data['command'] == 'bestdeal':
                bot.send_message(call.message.chat.id, 'Введите, пожалуйста, минимальную стоимость отеля за ночь:')
                bot.set_state(call.from_user.id, UserInfoState.min_price, call.message.chat.id)
            else:
                bot.send_message(call.message.chat.id, 'Сколько отелей показать?',
                                 reply_markup=quantity_hotels_markup())
                # bot.set_state(call.message.from_user.id, UserInfoState.photo_y_n, call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.endswith('_2'))
def photo_y_n(call):
    # сохраняет количество отелей
    # фото отелей

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['quantity_hotels'] = int(call.data[:-2])

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, 'Показать фото отелей?',
                     reply_markup=photo_y_n_markup())
    # bot.set_state(call.message.from_user.id, UserInfoState.quantity_photo, call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.endswith('_3'))
def quantity_photo(call):
    # если да - запрашивает количество фото
    # если нет - список отелей

    bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.data[:-2] == 'Да':
        bot.send_message(call.message.chat.id, 'Сколько фото показать?',
                         reply_markup=quantity_photo_markup())
        # bot.set_state(call.message.from_user.id, UserInfoState.hotels, call.message.chat.id)
    else:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            days = (data['check_out'] - data['check_in']).days
            create_hotel_message(bot_data=data,
                                 days_count=days,
                                 user_id=call.from_user.id)


@bot.callback_query_handler(func=lambda call: call.data.endswith('_4'))
def hotels(call):
    # сохраняет количество фото
    # список отелей

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['quantity_photo'] = int(call.data[:-2])

        bot.delete_message(call.message.chat.id, call.message.message_id)
        days = (data['check_out'] - data['check_in']).days
        create_hotel_message(bot_data=data,
                             days_count=days,
                             user_id=call.from_user.id,
                             photo_quantity=data['quantity_photo'])





