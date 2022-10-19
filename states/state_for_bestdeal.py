from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    min_price = State()
    max_price = State()
    min_distance = State()
    max_distance = State()


# 1 Минимальная цена
# 2 Максимальная цена
# 3 Минимальное расстояние от центра города
# 4 Максимальное расстояние от центра города

