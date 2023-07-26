# infotecs_dev

Описание методов:

load_data - загружает всю инфу из БД.

get_city_by_geonameid - получаем инфу по geonameid, вызывается: http://127.0.0.1:8000/city/12478208

get_cities_by_page - передаем страницу и кол-во городов на странице, вызывается: http://127.0.0.1:8000/cities/2/2, где после cities первое значение - это номер страницы, а второе это кол-во городов.

get_city_by_name - вспомогательный метод, который возвращает словарь по названию города (в том числе и на русском)

compare_cities - метод принимает названия двух городов (на русском языке) и получает информацию о найденных городах, а также дополнительно: какой из них расположен севернее и одинаковая ли у них временная зона и на сколько она отличается (когда несколько городов имеют одно и то же название, неоднозначность разрешается выборкой город с большим населением; если население совпадает, брать первый попавшийся), вызывается: http://127.0.0.1:8000/compare/Доброград/Gora Zarechnaya

city_analyzer - метод, который пользователь вводит часть названия города и возвращает ему подсказку с возможными вариантами продолжений, вызывается: http://127.0.0.1:8000/analis/барсучк

do_GET - обрабатывает входящие запросы и отправляет ответ.
