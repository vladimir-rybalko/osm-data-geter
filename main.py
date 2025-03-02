from config import query_filters
from utils import *
import os

# создаем папку для хранения результатов, если ее нет
if not os.path.exists('data'):
    os.makedirs('data')

if os.path.exists('./data/merged.geojson'):
    os.remove('./data/merged.geojson')


def main(city_name: str):
    # получаем полигон города
    polygon = geocode_city(city_name)
    # для каждого фильтра из конфига
    for query_filter in query_filters:
        # создаем FeatureCollection
        fc = {
            "type": "FeatureCollection",
            "features": []
        }
        # получаем имя фильтра
        query_name = query_filter['name']
        # получаем свойства, которые нужно добавить в Feature
        properties = query_filter['properties']
        # получаем свойства, которые нужно заменить
        replace_properties = query_filter['replaceProperties'].split('-')
        # получаем фильтры для Overpass
        query_filter = query_filter['filter']
        # получаем результаты запроса
        res = overpass_query(polygon, query_filter)
        # для каждого элемента из результатов
        for element in res['elements']:
            # получаем координаты
            lon = None
            lat = None
            if element['type'] == 'node':
                # если это точка, то берем координаты
                lon = element['lon']
                lat = element['lat']
            elif element['type'] == 'way':
                # если это линия, то получаем полигон
                poly = 'POLYGON(('
                for i, point in enumerate(element['geometry']):
                    poly += f"{point['lon']} {point['lat']}"
                    if i < len(element['geometry'])-1:
                        poly += ','
                poly += '))'
                # получаем координаты центра полигона
                lon, lat = get_polygon_centroid(poly)

            # создаем Feature
            feat = {
                "type": "Feature",
                "properties": {
                    "id": element['id']
                },
                "geometry": {
                    "coordinates": [ lon, lat ],
                    "type": "Point"
                }
            }
            # добавляем свойства
            for property in properties:
                if property in element['tags'] and replace_properties[0] == property:
                    # если свойство заменяемое, то заменяем его
                    feat['properties'][replace_properties[1]] = element['tags'][property]
                elif property in element['tags']:
                    # если свойство не заменяемое, то добавляем его
                    feat['properties'][property] = element['tags'][property]
            # добавляем адрес
            feat['properties']['address'] = get_address_from_coordinates(lon, lat)
            # добавляем Feature в FeatureCollection
            fc['features'].append(feat)

        # сохраняем FeatureCollection в файл
        with open(os.path.join('data', f'{query_name}_features.geojson'), 'w', encoding='utf-8') as file:
            json.dump(fc, file, ensure_ascii=False, indent=4)

    # объединяем все FeatureCollection-ы
    merge_geojson_files('./data')


if __name__ == '__main__':
    # city_name = input("Введите название города: ")
    city_name = 'Яр-Сале'
    main(city_name)