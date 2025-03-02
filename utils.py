import osmnx as ox
import requests
import os
import json
from shapely import wkt


def geocode_city(place_name: str) -> list:
    """
    Геокодирует населенный пункт и возвращает его как полигональную область.
    :param place_name: Название населенного пункта.
    :return: Полигональная область.
    """
    gdf = ox.geocode_to_gdf(place_name)
    polygon = None
    if not gdf.empty:
        polygon = gdf['geometry'].iloc[0]
        polygon = [
            polygon.bounds[1], polygon.bounds[0],
            polygon.bounds[3], polygon.bounds[0],
            polygon.bounds[3], polygon.bounds[2],
            polygon.bounds[1], polygon.bounds[2]
        ]
    else:
        print(f"Населенный пункт '{place_name}' не найден.")

    return polygon


def overpass_query(polygon: list, query_filter: list) -> dict:
    """
    Отправляет запрос к Overpass API.
    :param polygon: Полигональная область.
    :param query_filter: Фильтр запроса.
    :return: Результат запроса.
    """
    polygon = 'poly:"' + ' '.join(map(str, polygon)) + '"'
    query = f"""
            [out:json];
            (
    """
    query += ''.join(f'{f}({polygon});' for f in query_filter)

    query += """
        );
        out geom;
    """

    return requests.post('http://overpass-api.de/api/interpreter', data={'data': query}).json()


def get_polygon_centroid(polygon_wkt: str) -> tuple:
    """
    Вычисляет центр полигона.
    :param polygon_wkt: WKT-строка полигона.
    :return: Координаты центра полигона.
    """
    polygon = wkt.loads(polygon_wkt)
    return polygon.centroid.x, polygon.centroid.y


def merge_geojson_files(data_dir: str) -> None:
    """
    Объединяет geojson-файлы в одном каталоге.
    :param data_dir: Каталог с geojson-файлами.
    :return: None
    """
    merged_data = {
        'type': 'FeatureCollection',
        'features': []
    }

    for filename in os.listdir(data_dir):
        if filename.endswith(".geojson"):
            with open(os.path.join(data_dir, filename)) as f:
                data = json.load(f)
                merged_data['features'].extend(data['features'])

    with open(os.path.join(data_dir, 'merged.geojson'), 'w') as f:
        json.dump(merged_data, f, indent=4, ensure_ascii=False)

    # delete old files
    for filename in os.listdir(data_dir):
        if not (filename.startswith('merged') and filename.endswith('.geojson')):
            os.remove(os.path.join(data_dir, filename))


def get_address_from_coordinates(longitude: float, latitude: float) -> str:
    """
    Получает адрес по координатам.
    :param longitude: Координата X.
    :param latitude: Координата Y.
    :return: Адрес.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}&addressdetails=1"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        display_name = 'Address not found'
        if 'display_name' in data:
            display_name = data['display_name']
        return display_name
    else:
        return 'Error retrieving address'