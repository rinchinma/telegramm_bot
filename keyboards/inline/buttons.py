from telebot import types


def city_markup(cities):

    destinations = types.InlineKeyboardMarkup()
    for part in cities:
        destinations.add(types.InlineKeyboardButton(text=part['city_name'],
                                                    callback_data=f'{part["destination_id"]}_1'))
    return destinations


def quantity_hotels_markup():
    destinations = types.InlineKeyboardMarkup()
    destinations.add(types.InlineKeyboardButton(text=5,
                                                callback_data=f'{5}_2'))
    destinations.add(types.InlineKeyboardButton(text=10,
                                                callback_data=f'{10}_2'))
    return destinations


def photo_y_n_markup():
    destinations = types.InlineKeyboardMarkup()
    destinations.add(types.InlineKeyboardButton(text='Да',
                                                callback_data="Да_3"))
    destinations.add(types.InlineKeyboardButton(text='Нет',
                                                callback_data="Нет_3"))
    return destinations


def quantity_photo_markup():
    destinations = types.InlineKeyboardMarkup()
    destinations.add(types.InlineKeyboardButton(text=5,
                                                callback_data=f'{5}_2'))
    destinations.add(types.InlineKeyboardButton(text=10,
                                                callback_data=f'{10}_2'))
    return destinations

