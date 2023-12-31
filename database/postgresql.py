import asyncio
import datetime
from typing import Literal
from typing import List

from database.data import *
from datetime_now import dt_now
import asyncpg
import json
from config import *

class Database:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.pool: asyncio.pool.Pool = loop.run_until_complete(
            asyncpg.create_pool(
                database=DATABASE,
                user=PGUSER,
                password=PASSWORD,
                host=ip,
            )
        )

    async def sql_start(self):
        if self.pool:
            print('Data base connected ok!')
            await self._create_table_all_users()
            await self._create_table_all_users_driver()
            await self._create_table_drivers()
            await self._create_table_orders_driver()
            await self._create_table_orders_client()
            await self._create_table_orders_accepted()
            await self._create_wallet_pay()

            await self._create_table_models()
            await self._create_table_car_subtype()
            await self._create_table_colors()
            await self._create_table_spots()

            # await self._add_models(models=models)
            # await self._add_car_subtype(car_subtype=car_subtype)
            # await self._add_colors(colors=colors)
            # await self._add_spots(spots=spots)

    async def _create_table_spots(self):
        sql = """CREATE TABLE IF NOT EXISTS spots(
                   id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                   location JSONB NOT NULL,
                   rus VARCHAR(255) NOT NULL,
                   ozb VARCHAR(255) NOT NULL,
                   uzb VARCHAR(255) NOT NULL
                   )"""
        await self.pool.execute(sql)

    async def _create_table_models(self):
        sql = """CREATE TABLE IF NOT EXISTS models(
                   id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                   model VARCHAR(255) NOT NULL ,
                   car_type VARCHAR(255) NOT NULL, 
                   car_subtype VARCHAR(255) NOT NULL
                   )"""
        await self.pool.execute(sql)

    async def _create_table_car_subtype(self):
        sql = """CREATE TABLE IF NOT EXISTS car_subtype(
                   id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                   car_type VARCHAR(255) NOT NULL, 
                   car_subtype VARCHAR(255) NOT NULL,
                   rus VARCHAR(255) NOT NULL,
                   ozb VARCHAR(255) NOT NULL,
                   uzb VARCHAR(255) NOT NULL,
                   pay_per_minute BIGINT NOT NULL,
                   pay_per_kilometer BIGINT NOT NULL,
                   pay_first_kilometer BIGINT NOT NULL,
                   n_first_kilometer FLOAT NOT NULL, 
                   n_first_minutes BIGINT NOT NULL
                   )"""
        await self.pool.execute(sql)

    async def _create_table_colors(self):
        sql = """CREATE TABLE IF NOT EXISTS colors(
                   id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                   rus VARCHAR(255) NOT NULL,
                   ozb VARCHAR(255) NOT NULL,
                   uzb VARCHAR(255) NOT NULL
                   )"""
        await self.pool.execute(sql)

    async def _create_wallet_pay(self):
        sql = """CREATE TABLE IF NOT EXISTS wallet_pay(
                pay_id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                driver_id BIGINT NOT NULL,
                cash BIGINT NOT NULL,
                type_of_payment VARCHAR(255) NOT NULL,             
                datetime_payment timestamp NOT NULL,
                status BOOL NOT NULL
                )"""
        await self.pool.execute(sql)

    async def _add_models(self, models: List):
        sql = """INSERT INTO models(model, car_type, car_subtype)
                 VALUES($1, $2, $3)"""
        await self.pool.executemany(sql, models)

    async def _add_colors(self, colors: List):
        sql = """INSERT INTO colors(rus, ozb, uzb)
                 VALUES($1, $2, $3)"""
        await self.pool.executemany(sql, colors)

    async def _add_car_subtype(self, car_subtype: List):
        sql = """INSERT INTO car_subtype(car_type, car_subtype, rus, ozb, uzb, 
                                         pay_per_minute, pay_per_kilometer, pay_first_kilometer, 
                                         n_first_kilometer, n_first_minutes)
                 VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)"""
        await self.pool.executemany(sql, car_subtype)

    async def _add_spots(self, spots: List):
        modified_spots = []
        for spot in spots:
            json_str = json.dumps(spot[0])  # Convert the dictionary to a JSON string
            modified_spot = (json_str, *spot[1:])  # Create a new tuple with the modified JSON string
            modified_spots.append(modified_spot)
        sql = """INSERT INTO spots(location, rus, ozb, uzb)
                 VALUES($1, $2, $3, $4)"""
        await self.pool.executemany(sql, modified_spots)

    async def _create_table_all_users(self):
        sql = """CREATE TABLE IF NOT EXISTS all_users(
                   id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                   user_id BIGINT NOT NULL, 
                   name VARCHAR(255) NOT NULL, 
                   username VARCHAR(255),
                   phone VARCHAR(255),
                   language VARCHAR(255),
                   status BOOL,
                   cashback BIGINT NOT NULL, 
                   datetime_registration timestamp NOT NULL
                   )"""
        await self.pool.execute(sql)

    async def _create_table_all_users_driver(self):
        sql = """CREATE TABLE IF NOT EXISTS all_users_driver(
                   id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                   user_id BIGINT NOT NULL, 
                   name VARCHAR(255) NOT NULL, 
                   username VARCHAR(255),
                   language VARCHAR(255),
                   status BOOL,
                   datetime_registration timestamp NOT NULL
                   )"""
        await self.pool.execute(sql)

    async def _create_table_drivers(self):
        sql = """CREATE TABLE IF NOT EXISTS drivers(
                   id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                   driver_id BIGINT NOT NULL,
                   name VARCHAR(255) NOT NULL,
                   username VARCHAR(255),        
                   phone VARCHAR(255),
                   car BIGINT NOT NULL,
                   car_type VARCHAR(255) NOT NULL, 
                   car_subtype VARCHAR(255) NOT NULL,
                   color BIGINT ,
                   number VARCHAR(255) NOT NULL,
                   driver_rate NUMERIC(2,1) NOT NULL,
                   datetime_registration timestamp NOT NULL,
                   status BOOL NOT NULL, 
                   wallet_main BIGINT NOT NULL,
                   wallet_bonus BIGINT NOT NULL,
                   wallet_holiday BIGINT NOT NULL
                   )"""
        await self.pool.execute(sql)

    async def _create_table_orders_driver(self):
        sql = """CREATE TABLE IF NOT EXISTS orders_driver(      
                   order_driver_id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                   driver_id BIGINT NOT NULL,
                   spots BIGINT[] NOT NULL, 
                   delivery bool NOT NULL, 
                   truck bool NOT NULL, 
                   datetime_open timestamp NOT NULL,
                   
                   datetime_close timestamp,
                   cancel BOOL,
                   on_route BOOL
                   )"""
        await self.pool.execute(sql)

    async def _create_table_orders_client(self):
        sql = """CREATE TABLE IF NOT EXISTS orders_client(      
                   order_client_id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                   client_id BIGINT NOT NULL,
                   order_type VARCHAR(255) NOT NULL, 
                   location JSONB NOT NULL,
                   comment VARCHAR(255),
                   spot BIGINT NOT NULL,
                   payment_type VARCHAR(255) NOT NULL,
                   datetime_open timestamp NOT NULL,
                   order_accept BOOL 
                   )"""
        await self.pool.execute(sql)

    async def _create_table_orders_accepted(self):
        sql = """CREATE TABLE IF NOT EXISTS orders_accepted(
                   order_accept_id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                   order_client_id BIGINT NOT NULL,
                   order_driver_id BIGINT NOT NULL,
                   datetime_accepted timestamp NOT NULL,

                   datetime_arrive timestamp,
                   fee BIGINT,
                   waiting_fee BIGINT,
                   datetime_finish timestamp,
                   
                   datetime_cancel timestamp,
                   cancel_by VARCHAR(255),
                   finish BOOL
                   )"""
        await self.pool.execute(sql)

    # database
    async def add_spots(self, spots: list):
        sql = """INSERT INTO public.sub_spots (town_rus, district_rus, spot_rus, sub_spot_rus, 
                                               town_uzb, district_uzb, spot_uzb, sub_spot_uzb, 
                                               town_ozb, district_ozb, spot_ozb, sub_spot_ozb)
                 VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)"""
        await self.pool.executemany(sql, spots)

    # exist
    async def exist_client(self, user_id: int):
        sql = """SELECT CASE WHEN EXISTS (SELECT * FROM public.all_users WHERE user_id = $1)
                THEN TRUE ELSE FALSE END"""
        return (await self.pool.fetchrow(sql, user_id))[0]

    async def exist_client_driver(self, user_id: int):
        sql = """SELECT CASE WHEN EXISTS (SELECT * FROM public.all_users_driver WHERE user_id = $1)
                THEN TRUE ELSE FALSE END"""
        return (await self.pool.fetchrow(sql, user_id))[0]

    async def exist_driver(self, driver_id: int):
        sql = """SELECT CASE WHEN
                EXISTS (SELECT * FROM public.drivers WHERE driver_id = $1)
                THEN TRUE ELSE FALSE END"""
        return (await self.pool.fetchrow(sql, driver_id))[0]

    async def exist_lang(self, user_id: int):
        sql = """SELECT CASE WHEN EXISTS (SELECT * FROM public.all_users 
                WHERE user_id = $1 and language is not NULL)
                THEN TRUE ELSE FALSE END"""
        return (await self.pool.fetchrow(sql, user_id))[0]

    async def exist_lang_driver(self, user_id: int):
        sql = """SELECT CASE WHEN EXISTS (SELECT * FROM public.all_users_driver 
                WHERE user_id = $1 and language is not NULL)
                THEN TRUE ELSE FALSE END"""
        return (await self.pool.fetchrow(sql, user_id))[0]

    async def name_driver(self, driver_id: int):
        sql = """SELECT name FROM public.drivers WHERE driver_id = $1"""
        return (await self.pool.fetchrow(sql, driver_id))[0]

    # block_status
    async def block_status(self, user_id: int, status: bool):
        sql = """UPDATE public.all_users SET status = $2 WHERE user_id = $1"""
        await self.pool.execute(sql, user_id, status)

    async def block_status_driver(self, user_id: int, status: bool):
        sql = """UPDATE public.all_users_driver SET status = $2 WHERE user_id = $1"""
        await self.pool.execute(sql, user_id, status)

    # language
    async def select_language(self, user_id: int):
        sql = """ SELECT language FROM public.all_users 
                  WHERE user_id = $1 """
        return (await self.pool.fetchrow(sql, user_id))[0]

    async def select_language_driver(self, user_id: int):
        sql = """ SELECT language FROM public.all_users_driver
                  WHERE user_id = $1 """
        return (await self.pool.fetchrow(sql, user_id))[0]

    async def update_language(self, language: str, user_id: int):
        sql = """UPDATE public.all_users SET language = $1 WHERE user_id = $2"""
        await self.pool.execute(sql, language, user_id)

    async def update_language_driver(self, language: str, user_id: int):
        sql = """UPDATE public.all_users_driver SET language = $1 WHERE user_id = $2"""
        await self.pool.execute(sql, language, user_id)

    async def exist_phone_client(self, user_id: int):
        sql = """SELECT CASE WHEN EXISTS (SELECT * FROM public.all_users WHERE user_id = $1 AND phone IS NOT NULL)
                THEN TRUE ELSE FALSE END"""
        return (await self.pool.fetchrow(sql, user_id))[0]

    async def update_phone(self, phone: str, user_id: int):
        sql = """UPDATE public.all_users SET phone = $1 WHERE user_id = $2"""
        await self.pool.execute(sql, phone, user_id)


    async def select_phone(self, user_id: int):
        sql = """ SELECT phone FROM public.all_users 
                  WHERE user_id = $1 """
        return (await self.pool.fetchrow(sql, user_id))[0]

    async def check_order_accept(self, order_id: int):
        sql = """ SELECT order_accept FROM public.orders_client WHERE order_client_id = $1 """
        return (await self.pool.fetchrow(sql, order_id))[0]

    async def update_order(self, order_client_id: int, status: bool):
        sql = """UPDATE public.orders_client SET order_accept = $2 WHERE order_client_id = $1"""
        await self.pool.execute(sql, order_client_id, status)

    async def update_cancel_order(self, order_client_id: int, cancel_by: Literal["client", "driver"] = "client"):
        sql = """UPDATE public.orders_accepted SET cancel_by = $2 WHERE order_client_id = $1 RETURNING order_driver_id"""
        return await self.pool.fetchrow(sql, order_client_id, cancel_by)

    # first rec
    async def first_rec_client(self, user_id: int, name: str, username: str, status: bool):
        date = dt_now.now()
        sql = """INSERT INTO all_users (user_id, name, username, status, datetime_registration, cashback)
                 VALUES ($1, $2, $3, $4, $5, 0)"""
        await self.pool.execute(sql, user_id, name, username, status, date)

    async def first_rec_in_driver(self, user_id: int, name: str, username: str, status: bool):
        date = dt_now.now()
        sql = """INSERT INTO all_users_driver (user_id, name, username, status, datetime_registration)
                 VALUES ($1, $2, $3, $4, $5)"""
        await self.pool.execute(sql, user_id, name, username, status, date)

    async def first_rec_driver(self, driver_id: int, name: str, username: str, car: int,
                               car_type: str, car_subtype: str,  color: int, number: str, phone: int, wallet: int):
        date = dt_now.now()
        sql = """INSERT INTO public.drivers (driver_id, name, username, car, car_type, car_subtype, color, number,  phone, 
                                             driver_rate, datetime_registration, wallet_main, wallet_bonus, 
                                             wallet_holiday, status)
                                             
                 VALUES ($1, $2, $3, $4, $5, $6,  $7, $8, $9, 5,  $10, 0, $11, 0, False)"""
        await self.pool.execute(sql, driver_id, name, username, car, car_type, car_subtype, color, number, phone, date, wallet)

    async def new_order_client(self, client_id: int, order_type: Literal["standard", "comfort", "delivery"],
                               location: str, comment: str, spot: int, payment_type: Literal["cash", "card"]):
        date = dt_now.now()
        location = json.dumps(location)
        sql = """INSERT into public.orders_client(client_id, order_type, location, comment, spot, payment_type, datetime_open) 
                 VALUES($1, $2, $3, $4, $5, $6, $7) RETURNING order_client_id"""
        return (await self.pool.fetchrow(sql, client_id, order_type, location, comment, spot, payment_type, date))[0]

    async def select_spot(self, location: dict):
        sql = """
            SELECT *
            FROM public.spots 
            ORDER BY (
                ABS(
                    (3958 * 3.1415926 * 
                    SQRT(
                        ($1 - (spots.location->>'latitude')::numeric)^2 +
                        COS($1/57.29578) * COS((spots.location->>'latitude')::numeric/57.29578) * 
                        ($2 - (spots.location->>'longitude')::numeric)^2
                        ) / 180
                    )
                )
            )
        """
        return (await self.pool.fetchrow(sql, location['latitude'], location['longitude']))[0]

    # car id and value
    async def id_and_model(self, car_type: str):
        sql = 'SELECT * FROM public.models WHERE car_type = $1'
        return await self.pool.fetch(sql, car_type)

    async def id_and_model2(self, car_type: str, car_subtype: str):
        sql = 'SELECT * FROM public.models WHERE car_type = $1 and car_subtype = $2'
        return await self.pool.fetch(sql, car_type, car_subtype)

    async def id_to_model(self, car_id):
        sql = 'SELECT model, car_type, car_subtype FROM public.models WHERE id = $1'
        return await self.pool.fetchrow(sql, car_id)

    async def id_and_car_subtype(self, car_type: str, language: str):
        sql = f'SELECT car_subtype, "{language}"  FROM public.car_subtype WHERE car_type = $1'
        return await self.pool.fetch(sql, car_type)

    async def id_and_color(self, language: str):
        sql = f'SELECT id, "{language}" FROM public.colors'
        return await self.pool.fetch(sql)

    async def id_to_color(self, id, language: str):
        sql = f'SELECT "{language}" FROM public.colors WHERE id = $1'
        return (await self.pool.fetchrow(sql, id))[0]

    async def id_and_spot(self, language: str):
        sql = f'SELECT id, "{language}" FROM public.spots'
        return await self.pool.fetch(sql)

    async def id_to_spot(self, id, language: str):
        sql = f'SELECT "{language}" FROM public.spots WHERE id = $1'
        return (await self.pool.fetchrow(sql, id))[0]

    async def id_to_car_subtype(self, car_subtype: str, language: str):
        sql = f'''SELECT "{language}", 
                  pay_per_minute, pay_per_kilometer, pay_first_kilometer, n_first_kilometer, n_first_minutes 
                  FROM public.car_subtype WHERE "car_subtype" = $1'''
        return await self.pool.fetchrow(sql, car_subtype)

    async def car_subtype_to_id(self, car_subtype: str, language: str):
        sql = f'SELECT "car_subtype" FROM public.car_subtype WHERE "{language}" = $1'
        return (await self.pool.fetchrow(sql, car_subtype))[0]

    # основные параметры водителя
    async def select_parameters_driver(self, driver_id):
        sql = '''SELECT name, phone, car, car_type, car_subtype, color, number, round(driver_rate, 1)::numeric 
                 FROM public.drivers WHERE driver_id = $1'''
        return await self.pool.fetchrow(sql, driver_id)

    async def select_status_driver(self, driver_id: int):
        sql = '''SELECT status FROM public.drivers WHERE drivers.driver_id = $1'''
        return (await self.pool.fetchrow(sql, driver_id))[0]

    async def update_drivers_status(self, driver_id: int, status: bool):
        sql = """   UPDATE public.drivers SET status = $2 WHERE driver_id = $1 """
        await self.pool.execute(sql, driver_id, status)

    # personal data
    async def update_drivers_name(self, driver_id: int, name: str):
        sql = """   UPDATE public.drivers
                    SET  name = $2
                    WHERE driver_id = $1 """
        await self.pool.execute(sql, driver_id, name)

    async def update_drivers_phone(self, driver_id: int, phone: int):
        sql = """   UPDATE public.drivers
                    SET  phone = $2
                    WHERE driver_id = $1 """
        await self.pool.execute(sql, driver_id, phone)

    async def update_drivers_car(self, driver_id: int, car: int, car_type: str, car_subtype: str):
        sql = """   UPDATE public.drivers
                    SET  car = $2, car_type = $3, car_subtype = $4
                    WHERE driver_id = $1 """
        await self.pool.execute(sql, driver_id, car, car_type, car_subtype)

    async def update_drivers_color(self, driver_id: int, color: int):
        sql = """   UPDATE public.drivers
                    SET  color = $2
                    WHERE driver_id = $1 """
        await self.pool.execute(sql, driver_id, color)

    async def update_drivers_number(self, driver_id: int, number: str):
        sql = """   UPDATE public.drivers
                    SET  number = $2
                    WHERE driver_id = $1 """
        await self.pool.execute(sql, driver_id, number)

    # ##################################### payments ###################################################################
    async def select_all_wallet(self, driver_id: int):
        sql = """SELECT WALLET_MAIN + WALLET_BONUS + WALLET_HOLIDAY AS WALLET_ALL 
                            FROM PUBLIC.DRIVERS
                            WHERE DRIVER_ID = $1"""
        return (await self.pool.fetchrow(sql, driver_id))[0]

    async def select_wallets(self, driver_id: int):
        sql = """SELECT WALLET_MAIN,
                    WALLET_BONUS + WALLET_HOLIDAY
                    FROM PUBLIC.DRIVERS
                    WHERE DRIVER_ID = $1"""
        return await self.pool.fetchrow(sql, driver_id)

    async def select_every_wallet(self, driver_id: int):
        sql = """SELECT WALLET_MAIN, WALLET_BONUS, WALLET_HOLIDAY
                    FROM PUBLIC.DRIVERS
                    WHERE DRIVER_ID = $1"""
        return await self.pool.fetchrow(sql, driver_id)

    async def new_route_driver(self, driver_id: int, spots: list, delivery: bool, truck: bool):
        datenow = dt_now.now()
        sql = """INSERT INTO public.orders_driver(driver_id, spots, datetime_open, cancel, delivery, truck)
                 VALUES ($1, $2, $3, False, $4, $5)"""
        await self.pool.execute(sql, driver_id, spots, datenow, delivery, truck)

    async def cancel_route_driver(self, driver_id: int):
        datenow = dt_now.now()
        sql = """UPDATE public.orders_driver SET cancel = True, datetime_close = $2 WHERE driver_id = $1"""
        return await self.pool.fetchrow(sql, driver_id, datenow)

    async def select_route_driver(self, driver_id: int):
        sql = """SELECT order_driver_id FROM public.orders_driver WHERE driver_id = $1"""
        return await self.pool.fetchrow(sql, driver_id)

    async def select_route_driver2(self, order_driver_id: int):
        sql = """SELECT od.driver_id, aud.language  FROM public.orders_driver od
                  FULL JOIN public.all_users_driver aud ON aud.user_id = od.driver_id
                  WHERE order_driver_id = $1 """
        return await self.pool.fetchrow(sql, order_driver_id)

    async def accept_order(self, order_client_id: int, driver_id: int):
        date = dt_now.now()
        sql = """INSERT INTO public.orders_accepted (order_client_id, order_driver_id, datetime_accepted)
                 VALUES ($1, (SELECT order_driver_id FROM public.orders_driver 
                              WHERE driver_id = $2 and cancel != True 
                              ORDER BY order_driver_id DESC LIMIT 1), $3)"""
        await self.pool.execute(sql, order_client_id, driver_id, date)

    async def finish_accept_order(self, fee: int,  waiting_fee: int, orders_accepted_id: int, datetime_arrive: str, status: bool = None):
        datetime_arrive = datetime.datetime.strptime(datetime_arrive, "%d.%m.%y %H:%M:%S")
        date = dt_now.now()
        sql = """UPDATE public.orders_accepted 
                 SET finish = $6, fee = $1, waiting_fee = $2, datetime_finish = $3, datetime_arrive = $5
                 WHERE order_accept_id = $4"""
        await self.pool.execute(sql, fee, waiting_fee, date, orders_accepted_id, datetime_arrive, status)

    async def select_spot_client(self, location: dict):
        sql = """SELECT id From public.spots Order by (abs((3958 * 3.1415926 
                    * sqrt(($1 - (spots.location->>'latitude')::numeric)^2  + cos($1/ 57.29578) 
                    * cos((spots.location->>'latitude')::numeric / 57.29578) 
                    * ($2 - (spots.location->>'longitude')::numeric)^2) / 180) Limit 1"""
        return await self.pool.fetchrow(sql, location['latitude'], location['longitude'])

    async def select_drivers_taxi(self, spot: int, _type: str):
        sql = """ SELECT od.driver_id FROM orders_driver od
                  JOIN public.drivers d ON od.driver_id = d.driver_id
                  WHERE $1 = ANY(spots) 
                  and cancel is not True 
                  and on_route is not True 
                  and d.car_subtype = $2"""
        return await self.pool.fetch(sql, spot, _type)

    async def select_all_drivers(self, spot: int, _type: str):
        sql = """ SELECT od.driver_id FROM orders_driver od
                  JOIN public.drivers d ON od.driver_id = d.driver_id
                  WHERE NOT ($1 = ANY(spots)) 
                  and cancel is not True 
                  and on_route is not True
                  and d.car_subtype = $2"""
        return await self.pool.fetch(sql, spot, _type)

    async def select_all_drivers_delivery(self):
        sql = """SELECT driver_id FROM orders_driver 
                 WHERE cancel is not True 
                 and on_route is not True 
                 and delivery is True"""
        return await self.pool.fetch(sql)

    async def select_drivers_trucks(self, _type: str):
        sql = """ SELECT od.driver_id FROM orders_driver od
                  JOIN public.drivers d ON od.driver_id = d.driver_id
                  WHERE cancel is not True 
                  and on_route is not True 
                  and d.car_subtype = $1  
                  and truck is True"""
        return await self.pool.fetch(sql, _type)

    async def update_on_route_status(self, driver_id: int, status: bool):
        sql = """   UPDATE public.orders_driver
                    SET  on_route = $2
                    WHERE driver_id = $1 """
        await self.pool.execute(sql, driver_id, status)

    async def select_active_order(self, client_id: int, language: str):
        sql = f"""SELECT oc.order_client_id, oa.order_accept_id, oc.order_type, oc.location, oc.comment,
                    au.phone, 
                    c.{language}, m.model, d.number, d.phone, d.name, oa.datetime_arrive, cs.car_type
        
                    FROM orders_client oc
                    
                    FULL JOIN orders_accepted oa ON oc.order_client_id = oa.order_client_id
                    JOIN public.all_users au ON oc.client_id = au.user_id
                    FULL JOIN public.orders_driver od  ON oa.order_driver_id = od.order_driver_id
                    FULL JOIN public.drivers d ON od.driver_id = d.driver_id
                    FULL JOIN public.models m ON d.car = m.id
                    FULL JOIN public.colors c ON d.color = c.id
                    FULL JOIN public.car_subtype cs ON oc.order_type = cs.car_subtype
                    
                    WHERE oc.client_id = $1
                        AND oc.order_accept is not False
                        AND oa.finish is not True
                        AND oa.cancel_by is null 
                    ORDER BY oa.order_client_id DESC """
        return await self.pool.fetch(sql, client_id)

    async def select_active_order_driver(self, driver_id: int):
        sql = f"""SELECT  oc.client_id, au.language, oc.location, oc.order_type, oa.order_accept_id, oa.order_client_id,
                        au.phone, au.language, oc.comment, au.cashback

                    FROM orders_accepted oa

                    JOIN orders_driver od ON od.order_driver_id = oa.order_driver_id
                    JOIN orders_client oc ON oc.order_client_id = oa.order_client_id
                    JOIN public.all_users au ON oc.client_id = au.user_id
                    
                    WHERE od.driver_id = $1 
                          AND oa.finish is not True
                          AND oa.cancel_by is null 
                    ORDER BY order_accept_id DESC """
        return await self.pool.fetchrow(sql, driver_id)

    async def active_location(self, order_client_id: int):
        sql = """   SELECT LOCATION FROM PUBLIC.orders_client
                    WHERE ORDER_client_ID = $1 """
        return json.loads((await self.pool.fetchrow(sql, order_client_id))[0])

    async def wallet_pay(self, driver_id: int, cash: int, type_of_payment: str, status: bool):
        datenow = dt_now.now()
        sql = """INSERT INTO public.wallet_pay(driver_id, cash, type_of_payment, datetime_payment, status)
                 VALUES ($1, $2, $3, $4, $5) RETURNING pay_id"""
        return (await self.pool.fetchrow(sql, driver_id, cash, type_of_payment, datenow, status))[0]

    async def update_wallet_pay(self, pay_id: int):
        sql = """UPDATE public.wallet_pay set status = True WHERE  pay_id = $1 """
        await self.pool.execute(sql, pay_id)

    async def update_cash_to_wallet(self,  pay_id: str):
        sql = """  UPDATE drivers SET wallet_main = (SELECT cash FROM wallet_pay WHERE pay_id = $1)  
                   WHERE driver_id = (SELECT driver_id FROM wallet_pay WHERE pay_id = $1)"""
        await self.pool.execute(sql, int(pay_id))

    async def update_driver_wallet_accept(self, driver_id: int, wallet):
        wallet_main, wallet_bonus, wallet_holiday = wallet
        sql = """   UPDATE public.drivers
                    SET   wallet_main=$2 , wallet_bonus=$3 , wallet_holiday=$4
                    WHERE driver_id = $1 """
        await self.pool.execute(sql, driver_id, wallet_main, wallet_bonus, wallet_holiday)

    async def update_driver_wallet_payment(self, driver_id: int, cash: int):
        sql = """   UPDATE public.drivers
                    SET  wallet_main = wallet_main + $2
                    WHERE driver_id = $1 """
        await self.pool.execute(sql, driver_id, cash)

    async def update_client_cashback(self, client_id: int, cashback: int):
        sql = """   UPDATE public.all_users
                    SET  cashback = cashback + $2
                    WHERE user_id = $1 RETURNING cashback"""
        return (await self.pool.fetchrow(sql, client_id, cashback))[0]

    async def select_client_cashback(self, client_id: int):
        sql = """   SELECT cashback FROM PUBLIC.all_users WHERE user_id = $1 """
        return (await self.pool.fetchrow(sql, client_id))[0]

    async def select_order_fee(self, order_id: int):
        sql = """   SELECT fee + waiting_fee, od.driver_id, au.language, oa.datetime_finish
                    FROM PUBLIC.orders_accepted oa 
                    
                    JOIN orders_driver od ON od.order_driver_id = oa.order_driver_id
                    JOIN public.all_users_driver au ON od.driver_id = au.user_id
                    
                    WHERE order_accept_id = $1 """
        return await self.pool.fetchrow(sql, order_id)

