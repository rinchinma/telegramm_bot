import requests
import json
import re
import telebot.types
from config_data.config import RAPID_API_KEY
from loader import bot
from loguru import logger


headers = {
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
    "X-RapidAPI-Key": RAPID_API_KEY
}


def request_to_api(url: str, querystring: dict):
    """
    Функция запрос и проверка информации с сайта

    :param url: url сайта
    :param querystring: Строка запроса
    :return: Ответ сайта
    """

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=20)  # 60
        if response.status_code == requests.codes.ok:
            return response
    except requests.exceptions.ReadTimeout:
        print('API error')


def city_founding(city='New York') -> list:
    """
    Функция для уточнения районов города

    :param city: Город для поиска в city_group (По умолчанию Нью-Йорк)
    :return: список районов города
    """

    if bool(re.search('[а-яА-Я]', city)):
        locale = "ru_RU"
    else:
        locale = "en_US"

    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": city, "locale": locale, "currency": "USD"}

    response = request_to_api(url=url, querystring=querystring)
    pattern = r'(?<="CITY_GROUP",).+?[\]]'

    find = re.search(pattern, response.text)
    city_res = json.loads(f"{{{find[0]}}}")

    cities = list()
    for index, elem in enumerate(city_res['entities']):  # Обрабатываем результат
        cities.append({'city_name': elem['name'], 'destination_id': elem['destinationId']})
    # for elem in city_res['entities']:
    #     cities.append({'city_name': elem['name'], 'destination_id': elem['destinationId']})

    return cities


def hotel_founding(city_id, command="lowprice", page="1") -> list:
    """
    Функция для поиска отелей

    :param city_id: id района города
    :return: Список отелей в указанной части города
    """

    url = "https://hotels4.p.rapidapi.com/properties/list"

    if command == 'high_price':
        sort_order = 'PRICE_HIGHEST_FIRST'
    else:
        sort_order = 'PRICE'

    querystring = {"destinationId": city_id, "pageNumber": page, "pageSize": "25",
                   "checkIn": "2020-01-08", "checkOut": "2020-01-15", "adults1": "1",
                   "sortOrder": sort_order, "locale": "en_US", "currency": "USD"}

    response = request_to_api(url=url, querystring=querystring)
    price_find = re.search(r'(?<=,)"results":.+?(?=,"pagination)', response.text)

    if price_find:
        data = json.loads(f'{{{price_find[0]}}}')
        hotels_list = data['results']
        return hotels_list


def photo_founding(hotel_id) -> json:
    """
    Функция для поиска фото

    :param hotel_id: id отеля
    :return: json для фото
    """

    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": hotel_id}

    response = request_to_api(url=url, querystring=querystring)

    pattern = r'(?<=,)"hotelImages":.+?(?=,"roomImages)'
    find_photo = re.search(pattern, response.text)

    if find_photo:
        data = json.loads(f'{{{find_photo[0]}}}')
        return data


def best_deal_founding(bot_data):  # Возвращает список согласно бестдил
    hotels_result = list()

    for page in range(1, 4):
        hotels = hotel_founding(city_id=bot_data['city_neighborhood_id'], command='bestdeal', page=str(page))

        if hotels:
            counter = 0
            for hotel in hotels:
                if hotel["landmarks"][0].get("distance"):
                    distance_from_api = hotel["landmarks"][0]["distance"].split()[0].replace(',', '.')
                    price_from_api = hotel["ratePlan"]["price"]["exactCurrent"]

                    if counter == int(bot_data['hotel_quantity']):
                        return hotels_result
                    elif float(bot_data['center_min']) <= float(distance_from_api) <= float(bot_data['center_max']):
                        if float(bot_data['min_price']) <= float(price_from_api) <= float(bot_data['max_price']):
                            hotels_result.append(hotel)
                        counter += 1

            if counter == int(bot_data['hotel_quantity']):  # 10
                return hotels_result











































