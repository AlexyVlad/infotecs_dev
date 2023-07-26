import http.server
import urllib


# Загрузка данных из файла БД
def load_data():
    data = {}
    with open("RU.txt", "r", encoding="utf-8") as file:
        for line in file:
            fields = line.strip().split("\t")
            data[int(fields[0])] = {
                "name": fields[1],
                "asciiname": fields[2],
                "alternatenames": fields[3],
                "latitude": fields[4],
                "longitude": fields[5],
                "feature_class": fields[6],
                "feature_code": fields[7],
                "country_code": fields[8],
                "cc2": fields[9],
                "admin1_code": fields[10],
                "admin2_code": fields[11],
                "admin3_code": fields[12],
                "admin4_code": fields[13],
                "population": fields[14],
                "elevation": fields[15],
                "dem": fields[16],
                "timezone": fields[17],
                "modification_date": fields[18],
            }
    return data


def load_time_zone():
    time_zone = {}
    with open("timeZones.txt", "r", encoding="utf-8") as file:
        for line in file:
            fields = line.strip().split("\t")
            time_zone[fields[1]] = {
                "GMT": float(fields[3]),
            }
    return time_zone


# Метод принимает идентификатор geonameid и возвращает информацию о городе.
def get_city_by_geonameid(geonameid):
    return data[geonameid]


# Метод принимает страницу и количество отображаемых на странице городов и возвращает список городов с их информацией.
def get_cities_by_page(page, items_per_page):
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    cities = list(data.values())[start_idx:end_idx]
    return cities


# Возвращает подсказку с возможными вариантами продолжений по введенной части названия города
def city_analyzer(part_name):
    result = []
    for geonameid, info in data.items():
        alternatenames = info['alternatenames'].lower().split(',')
        if part_name.lower() in info['name'].lower():
            result.append(info['name'].lower().replace(part_name.lower(), ''))
            continue
        for alt_name in alternatenames:
            if part_name.lower() in alt_name.strip():
                result.append(alt_name.lower().replace(part_name.lower(), ''))
                break
    return set(result)


# Возвращает город по имени (обрабатывает если город не 1)
def get_city_by_name(name):
    result = []
    for geonameid, info in data.items():
        alternatenames = info['alternatenames'].lower().split(',')
        if name.lower() == info['name'].lower():
            result.append(info)
            continue
        for alt_name in alternatenames:
            if name.lower() == alt_name.strip():
                result.append(info)
                break

    if len(result) > 1:
        return max(result, key=lambda city: int(city["population"]))
    elif result:
        return result[0]
    else:
        return None


# Сравнение 2 городов, вывод инфы о них, различие time зоны (на сколько), какой севернее
def compare_cities(city1, city2):
    city_info1 = get_city_by_name(city1)
    city_info2 = get_city_by_name(city2)

    if city_info1 is None or city_info2 is None:
        return None

    northern_city = city_info1 if city_info1["latitude"] > city_info2["latitude"] else city_info2
    same_timezone = city_info1["timezone"] == city_info2["timezone"]
    same_timezone_difference = 0

    if not same_timezone:
        time_zone = load_time_zone()

        same_timezone_difference = abs(time_zone[city_info1["timezone"]]["GMT"]) - \
                                   abs(time_zone[city_info2["timezone"]]["GMT"])
    return {
        "city1": city_info1,
        "city2": city_info2,
        "northern_city": northern_city["name"],
        "same_timezone": same_timezone,
        "same_timezone_difference": abs(same_timezone_difference),
    }


class GeoServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        path_components = path.split('/')

        if path_components[1] == 'city':
            geonameid = int(path_components[2])
            city_info = get_city_by_geonameid(geonameid)

            if city_info:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(str(city_info).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'City not found')

        elif path_components[1] == 'cities':
            page_number = int(path_components[2])
            items_per_page = int(path_components[3])
            cities = get_cities_by_page(page_number, items_per_page)

            if cities:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(str(cities).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Page not found')

        elif path_components[1] == 'compare':
            citi1 = urllib.parse.unquote(path_components[2])
            citi2 = urllib.parse.unquote(path_components[3])
            cities = compare_cities(citi1, citi2)

            if cities:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(str(cities).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Page not found')

        elif path_components[1] == 'analis':
            part_citi = urllib.parse.unquote(path_components[2])
            cities = city_analyzer(part_citi)

            if cities:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(str(cities).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Page not found')

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'404 Not Found')


if __name__ == "__main__":
    data = load_data()

    server_address = ('', 8000)
    httpd = http.server.HTTPServer(server_address, GeoServer)
    print('Сервер запущен...')
    httpd.serve_forever()