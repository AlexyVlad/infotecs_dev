import http.server
import urllib


# Загрузка данных из файла БД
def load_data():
    data = {}
    with open("RU.txt", "r", encoding="utf-8") as file:
        for line in file:
            fields = line.strip().split("\t")
            geonameid = int(fields[0])
            name = fields[1]
            asciiname = fields[2]
            alternatenames = fields[3]
            latitude = fields[4]
            longitude = fields[5]
            feature_class = fields[6]
            feature_code = fields[7]
            country_code = fields[8]
            cc2 = fields[9]
            admin1_code = fields[10]
            admin2_code = fields[11]
            admin3_code = fields[12]
            admin4_code = fields[13]
            population = fields[14]
            elevation = fields[15]
            dem = fields[16]
            timezone = fields[17]
            modification_date = fields[18]

            data[geonameid] = {
                "name": name,
                "asciiname": asciiname,
                "alternatenames": alternatenames,
                "latitude": latitude,
                "longitude": longitude,
                "feature_class": feature_class,
                "feature_code": feature_code,
                "country_code": country_code,
                "cc2": cc2,
                "admin1_code": admin1_code,
                "admin2_code": admin2_code,
                "admin3_code": admin3_code,
                "admin4_code": admin4_code,
                "population": population,
                "elevation": elevation,
                "dem": dem,
                "timezone": timezone,
                "modification_date": modification_date,
            }

    return data


# Метод принимает идентификатор geonameid и возвращает информацию о городе.
def get_city_by_geonameid(geonameid):
    return data[geonameid]


# Метод принимает страницу и количество отображаемых на странице городов и возвращает список городов с их информацией.
def get_cities_by_page(page, items_per_page):
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    cities = list(data.values())[start_idx:end_idx]
    return cities


# Метод принимает названия двух городов (на русском языке) и получает информацию о найденных городах,
# а также дополнительно: какой из них расположен севернее и на сколько часов различается их временная зона.
def compare_cities(city1, city2):
    # Ваш код обработки запроса по названиям городов и возврат информации о городах
    pass


class GeoServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Извлечь путь из URL запроса
        path = urllib.parse.urlparse(self.path).path

        # Разбить путь на компоненты, отделенные '/'
        path_components = path.split('/')

        # Проверить, если запрос начинается с '/city/'
        if path_components[1] == 'city':
            # Получить geonameid из запроса (предполагается, что geonameid находится вторым элементом)
            geonameid = int(path_components[2])

            # Вызвать метод get_city_by_geonameid(geonameid) и получить информацию о городе
            city_info = get_city_by_geonameid(geonameid)

            if city_info:
                # Отправить успешный ответ с информацией о городе в формате JSON
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(str(city_info).encode())
            else:
                # Отправить ответ с ошибкой, если город с указанным geonameid не найден
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'City not found')

        # Добавить обработку запроса для получения списка городов по страницам
        elif path_components[1] == 'cities':
            # Получить номер страницы из запроса (предполагается, что номер страницы находится вторым элементом,
            # а количество городов на странице - третьим элементом)
            page_number = int(path_components[2])
            items_per_page = int(path_components[3])

            # Вызвать метод get_cities_by_page(page_number, items_per_page)
            # и получить список городов для данной страницы
            cities = get_cities_by_page(page_number, items_per_page)

            if cities:
                # Отправить успешный ответ с информацией о городах в формате JSON
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(str(cities).encode())
            else:
                # Отправить ответ с ошибкой, если страница не найдена или другая ошибка
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Page not found')

        else:
            # Отправить ответ с ошибкой для всех остальных запросов
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'404 Not Found')


if __name__ == "__main__":
    data = load_data()

    #for key, value in data.items():
        #print(f'{value}')

    server_address = ('', 8000)
    httpd = http.server.HTTPServer(server_address, GeoServer)
    print('Сервер запущен...')
    httpd.serve_forever()