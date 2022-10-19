from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    command = State()
    city = State()
    # city_area = State()
    quantity_hotels = State()
    min_price = State()
    max_price = State()
    min_distance = State()
    max_distance = State()
    photo_y_n = State()
    quantity_photo = State()
    hotels = State()


# 1 Город
# 2 Район города
# 3 Количество отелей
# 4 Необходимость загрузки и вывода фотографий для каждого отеля (“Да/Нет”)
# 4.а) Количество необходимых фотографий, если ответ положительный  quantity_photo = State()
# 5 Отели
