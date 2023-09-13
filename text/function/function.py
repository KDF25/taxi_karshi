import math

from aiogram import types
from aiohttp import ClientSession

from looping import pg
from text.language.main import Text_main

Txt = Text_main()


class TextFunc:

    @staticmethod
    async def int_to_str(num: int):
        new_num = ""
        num = str(num)
        num_len = len(num)
        for i in range(0, num_len, 3):
            if i < num_len - 3:
                part = num[num_len - 3 - i:num_len - i:]
                new_num = f"{part} {new_num}"
        new_num_len = len(new_num.replace(" ", ""))
        if new_num_len < num_len:
            new_num = f"{num[0:num_len - new_num_len]} {new_num}"
        return new_num

    @staticmethod
    async def percent_price(price: int):
        tax = int(price * 10 / 100)
        tax = math.ceil(tax / 500) * 500
        tax = tax if tax < 9000 else 9000
        return tax

    @staticmethod
    async def distance(location_client: dict, location_driver: dict):
        url = "https://cubinc.uz/maps/route"
        params = {"longitude_a": location_client['longitude'], "latitude_a": location_client['latitude'],
                  "longitude_b": location_driver['latitude'], "latitude_b": location_driver['latitude']}
        async with ClientSession() as session:
            response = await session.get(url=url, params=params)
            distance = int((await response.json())['distance'])
        return distance

    @staticmethod
    async def cost_distance(distance: [int, float], __type: str):
        distance = round(distance / 1000, 2)
        lang, pay_per_minute, pay_per_kilometer, pay_first_kilometer, n_first_kilometer, n_first_minutes =\
            await pg.id_to_car_subtype(car_subtype=__type, language="rus")
        if distance <= n_first_kilometer:
            cost = pay_first_kilometer
        else:
            cost = pay_first_kilometer + (distance - n_first_kilometer) * pay_per_kilometer
        return int(cost)

    @staticmethod
    async def cost_time(time: [int, float], __type: str):
        lang, pay_per_minute, pay_per_kilometer, pay_first_kilometer, n_first_kilometer, n_first_minutes =\
            await pg.id_to_car_subtype(car_subtype=__type, language="rus")
        if time <= n_first_minutes:
            cost = 0
        else:
            cost = (time - n_first_minutes) * pay_per_minute
        return int(cost)

    @staticmethod
    async def personal_data(message: [types.Message, types.CallbackQuery], data):
        driver_id = message.from_user.id
        name, phone_driver, car, car_type, car_subtype, color, number, rate = \
            await pg.select_parameters_driver(driver_id=driver_id)
        data['driver_id'] = driver_id
        data['name'] = name
        data['phone_driver'] = phone_driver
        data['car_id'] = car
        data['model'] = (await pg.id_to_model(data['car_id']))[0]
        data['color_id'] = color
        data['number'] = number
        data['car_subtype'] = car_subtype
        data['car_type'] = car_type

    @staticmethod
    async def change_wallet(data: dict, price: int):
        if data['wallet'][2] == data['wallet'][1] == 0:
            data['wallet'][0] -= price
        elif data['wallet'][2] >= 0:
            if data['wallet'][2] >= price:
                data['wallet'][2] -= price
            elif data['wallet'][2] < price:
                price -= data['wallet'][2]
                data['wallet'][2] = 0
                if data['wallet'][1] >= price:
                    data['wallet'][1] -= price
                elif data['wallet'][1] < price:
                    price -= data['wallet'][1]
                    data['wallet'][1] = 0
                    data['wallet'][0] -= price
