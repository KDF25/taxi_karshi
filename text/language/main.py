from text.language.ru import Ru_language
from text.language.ozb import Ozb_language

RU = Ru_language()
OZB = Ozb_language()
UZB = Ozb_language()



class Text_main:

    choose_language = f"🇺🇿 Tilni tanlang 👇\n" \
                      f"🇷🇺 Выберите язык 👇\n"

    language = {"rus": RU, "ozb": OZB, "uzb": UZB}

    class settings:
        rus = "🇷🇺 Ru"
        ozb = "🇺🇿 O’z"
        uzb = "🇺🇿 Узб"
        language = [rus, ozb, uzb]

    class client:
        class menu:
            menu = [RU.menu.client.menu, OZB.menu.client.menu, UZB.menu.client.menu]
            taxi = [RU.menu.client.taxi, OZB.menu.client.taxi, UZB.menu.client.taxi]
            delivery = [RU.menu.client.delivery, OZB.menu.client.delivery, UZB.menu.client.delivery]
            truck = [RU.menu.client.truck, OZB.menu.client.truck, UZB.menu.client.truck]
            order = [RU.menu.client.order, OZB.menu.client.order, UZB.menu.client.order]
            phone = [RU.menu.client.phone, OZB.menu.client.phone, UZB.menu.client.phone]
            tarif = [RU.menu.client.tarif, OZB.menu.client.tarif, UZB.menu.client.tarif]
            change = [RU.menu.client.change, OZB.menu.client.change, UZB.menu.client.change]
            lang = [RU.menu.client.lang, OZB.menu.client.lang, UZB.menu.client.lang]
            myPhone = [RU.menu.client.myPhone, OZB.menu.client.myPhone, UZB.menu.client.myPhone]

        class taxi:
            standard = [RU.buttons.client.taxi.standard, OZB.buttons.client.taxi.standard, UZB.buttons.client.taxi.standard]
            comfort = [RU.buttons.client.taxi.comfort, OZB.buttons.client.taxi.comfort, UZB.buttons.client.taxi.comfort]
            location = [RU.buttons.client.taxi.location, OZB.buttons.client.taxi.location, UZB.buttons.client.taxi.location]
            comment = [RU.buttons.client.taxi.comment, OZB.buttons.client.taxi.comment, UZB.buttons.client.taxi.comment]

        class truck:
            small = [RU.buttons.client.truck.small, OZB.buttons.client.truck.small, UZB.buttons.client.truck.small]
            medium = [RU.buttons.client.truck.medium, OZB.buttons.client.truck.medium, UZB.buttons.client.truck.medium]
            big = [RU.buttons.client.truck.big, OZB.buttons.client.truck.big, UZB.buttons.client.truck.big]

    class driver:
        class menu:
            menu = [RU.menu.driver.menu, OZB.menu.driver.menu, UZB.menu.driver.menu]
            online = [RU.menu.driver.online, OZB.menu.driver.online, UZB.menu.driver.online]
            offline = [RU.menu.driver.offline, OZB.menu.driver.offline, UZB.menu.driver.offline]
            activity = [RU.menu.driver.activity, OZB.menu.driver.activity, UZB.menu.driver.activity]
            wallet = [RU.menu.driver.wallet, OZB.menu.driver.wallet, UZB.menu.driver.wallet]
            phone = [RU.menu.client.phone, OZB.menu.client.phone, UZB.menu.client.phone]
            settings = [RU.menu.driver.settings, OZB.menu.driver.settings, UZB.menu.driver.settings]
            onSpot = [RU.menu.driver.onSpot, OZB.menu.driver.onSpot, UZB.menu.driver.onSpot]
            orderData = [RU.menu.driver.orderData, OZB.menu.driver.orderData, UZB.menu.driver.orderData]
            myPhone = [RU.menu.driver.myPhone, OZB.menu.driver.myPhone, UZB.menu.driver.myPhone]
            lang = [RU.menu.driver.lang, OZB.menu.driver.lang, UZB.menu.driver.lang]

        class onSpot:
            start = [RU.buttons.driver.onSpot.start, OZB.buttons.driver.onSpot.start, UZB.buttons.driver.onSpot.start]
            orderData = [RU.buttons.driver.onSpot.orderData, OZB.buttons.driver.onSpot.orderData, UZB.buttons.driver.onSpot.orderData]
            waiting = [RU.buttons.driver.onSpot.waiting, OZB.buttons.driver.onSpot.waiting, UZB.buttons.driver.onSpot.waiting]
            letsGo = [RU.buttons.driver.onSpot.letsGo, OZB.buttons.driver.onSpot.letsGo, UZB.buttons.driver.onSpot.letsGo]
            finish = [RU.buttons.driver.onSpot.finish, OZB.buttons.driver.onSpot.finish, UZB.buttons.driver.onSpot.finish]

    class information:
        about_us = [RU.information.about_us, OZB.information.about_us, UZB.information.about_us]
        how_to_use = [RU.information.how_to_use, OZB.information.how_to_use, UZB.information.how_to_use]
        feedback = [RU.information.feedback, OZB.information.feedback, UZB.information.feedback]
        language = [RU.information.language, OZB.information.language, UZB.information.language]
        personalData = [RU.information.personalData, OZB.information.personalData, UZB.information.personalData]

    class money:
        class driver:
            price = [5000, 7000, 9000, 10000, 12000, 15000, 17000, 20000, 23000,
                     25000, 30000, 35000, 40000, 50000, 60000]
            order_min_price = 1000
            commission = 0.1  # 10 %

        class client:
            cashback = 0.05  # 5 %
            min_cashback = 3000
            cashback_time = 5

        class wallet:
            tax = 1000
            wallet = 50000
            price = [1000, 3000, 5000, 10000, 20000, 40000, 50000, 70000]