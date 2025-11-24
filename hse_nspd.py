from requests import Session, utils
from vgdb_general import smart_http_request
import geopandas as pd
import os
import json
import brotli                                       # это нужно, чтобы requests умела декодировать br                       
from datetime import datetime, timezone, timedelta
import pytz
from tqdm import tqdm
import urllib3
from time import sleep


def request_refresh_token(s: Session, refresh_token=''):
    """Функция обновляет токен авторизации на Госуслугах

    Args:
        s (Session): активная сессия Requests.Session, в которой происходит работа
        refresh_token (str, optional): Токен обновления. Defaults to ''.

    Raises:
        Exception: Если запрос обновления токена взвращает статус не 200, вызывается Exception с сообщением 'Не удалось обновить токен. Результат запроса: {result.content}'

    Returns:
        json: словарь со значениями: 
        access_token - новый ключ доступа, 
        refresh_token - новый токен обновления ключа доступа, 
        expires_in - срок истечения нового ключа доступа в UTC
    """
    # client_secret = 'MIINVwYJKoZIhvcNAQcCoIINSDCCDUQCAQExDDAKBggqhQMHAQECAjALBgkqhkiG9w0BBwGgggkDMIII_zCCCKygAwIBAgIQW9YkNOjmFO0v521L0IXrEzAKBggqhQMHAQEDAjCCAWExIDAeBgkqhkiG9w0BCQEWEXVjX2ZrQHJvc2them5hLnJ1MRgwFgYDVQQIDA83NyDQnNC-0YHQutCy0LAxFTATBgUqhQNkBBIKNzcxMDU2ODc2MDEYMBYGBSqFA2QBEg0xMDQ3Nzk3MDE5ODMwMWAwXgYDVQQJDFfQkdC-0LvRjNGI0L7QuSDQl9C70LDRgtC-0YPRgdGC0LjQvdGB0LrQuNC5INC_0LXRgNC10YPQu9C-0LosINC0LiA2LCDRgdGC0YDQvtC10L3QuNC1IDExGTAXBgNVBAcMENCzLiDQnNC-0YHQutCy0LAxCzAJBgNVBAYTAlJVMS4wLAYDVQQKDCXQmtCw0LfQvdCw0YfQtdC50YHRgtCy0L4g0KDQvtGB0YHQuNC4MTgwNgYDVQQDDC_QpNC10LTQtdGA0LDQu9GM0L3QvtC1INC60LDQt9C90LDRh9C10LnRgdGC0LLQvjAeFw0yNDA4MDIxMjMxMDNaFw0yNTEwMjYxMjMxMDNaMIIB8DELMAkGA1UEBhMCUlUxGTAXBgNVBAgMENCzLiDQnNC-0YHQutCy0LAxMjAwBgNVBAkMKdGD0LsuINCS0L7RgNC-0L3RhtC-0LLQviDQv9C-0LvQtSwg0LQuNNCwMRUwEwYDVQQHDAzQnNC-0YHQutCy0LAxgZAwgY0GA1UECgyBhdCk0JXQlNCV0KDQkNCb0KzQndCQ0K8g0KHQm9Cj0JbQkdCQINCT0J7QodCj0JTQkNCg0KHQotCS0JXQndCd0J7QmSDQoNCV0JPQmNCh0KLQoNCQ0KbQmNCYLCDQmtCQ0JTQkNCh0KLQoNCQINCYINCa0JDQoNCi0J7Qk9Cg0JDQpNCY0JgxGDAWBgUqhQNkARINMTA0Nzc5Njk0MDQ2NTEVMBMGBSqFA2QEEgo3NzA2NTYwNTM2MSQwIgYJKoZIhvcNAQkBFhUwMF9vemlsMUByb3NyZWVzdHIucnUxgZAwgY0GA1UEAwyBhdCk0JXQlNCV0KDQkNCb0KzQndCQ0K8g0KHQm9Cj0JbQkdCQINCT0J7QodCj0JTQkNCg0KHQotCS0JXQndCd0J7QmSDQoNCV0JPQmNCh0KLQoNCQ0KbQmNCYLCDQmtCQ0JTQkNCh0KLQoNCQINCYINCa0JDQoNCi0J7Qk9Cg0JDQpNCY0JgwZjAfBggqhQMHAQEBATATBgcqhQMCAiQABggqhQMHAQECAgNDAARAncHiBpT5hZi7kZb56fbzY5aKGGryq-bvSk5b-cRfy8Bj6_EXcSF2ZS9MHVG39usPSdREzeQyT3-TOd87XLN99KOCBKQwggSgMA4GA1UdDwEB_wQEAwID-DAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwEwYDVR0gBAwwCjAIBgYqhQNkcQEwDAYFKoUDZHIEAwIBATAtBgUqhQNkbwQkDCLQmtGA0LjQv9GC0L7Qn9GA0L4gQ1NQICg1LjAuMTIwMDApMIIBoQYFKoUDZHAEggGWMIIBkgyBh9Cf0YDQvtCz0YDQsNC80LzQvdC-LdCw0L_Qv9Cw0YDQsNGC0L3Ri9C5INC60L7QvNC_0LvQtdC60YEgVmlQTmV0IFBLSSBTZXJ2aWNlICjQvdCwINCw0L_Qv9Cw0YDQsNGC0L3QvtC5INC_0LvQsNGC0YTQvtGA0LzQtSBIU00gMjAwMFEyKQxo0J_RgNC-0LPRgNCw0LzQvNC90L4t0LDQv9C_0LDRgNCw0YLQvdGL0Lkg0LrQvtC80L_Qu9C10LrRgSDCq9Cu0L3QuNGB0LXRgNGCLdCT0J7QodCiwrsuINCS0LXRgNGB0LjRjyA0LjAMTUPQtdGA0YLQuNGE0LjQutCw0YIg0YHQvtC-0YLQstC10YLRgdGC0LLQuNGPIOKEltCh0KQvMTI0LTQzMjgg0L7RgiAyOS4wOC4yMDIyDE1D0LXRgNGC0LjRhNC40LrQsNGCINGB0L7QvtGC0LLQtdGC0YHRgtCy0LjRjyDihJbQodCkLzEyOC00NjM5INC-0YIgMDQuMTAuMjAyMzBmBgNVHR8EXzBdMC6gLKAqhihodHRwOi8vY3JsLnJvc2them5hLnJ1L2NybC91Y2ZrXzIwMjQuY3JsMCugKaAnhiVodHRwOi8vY3JsLmZrLmxvY2FsL2NybC91Y2ZrXzIwMjQuY3JsMHcGCCsGAQUFBwEBBGswaTA0BggrBgEFBQcwAoYoaHR0cDovL2NybC5yb3NrYXpuYS5ydS9jcmwvdWNma18yMDI0LmNydDAxBggrBgEFBQcwAoYlaHR0cDovL2NybC5may5sb2NhbC9jcmwvdWNma18yMDI0LmNydDAdBgNVHQ4EFgQUHpmFbGT-Z7mBm0OSmgon7jPgzs0wggF2BgNVHSMEggFtMIIBaYAUBmQTp87gg-KmfZ-Jp9ZWGZhM2aehggFDpIIBPzCCATsxITAfBgkqhkiG9w0BCQEWEmRpdEBkaWdpdGFsLmdvdi5ydTELMAkGA1UEBhMCUlUxGDAWBgNVBAgMDzc3INCc0L7RgdC60LLQsDEZMBcGA1UEBwwQ0LMuINCc0L7RgdC60LLQsDFTMFEGA1UECQxK0J_RgNC10YHQvdC10L3RgdC60LDRjyDQvdCw0LHQtdGA0LXQttC90LDRjywg0LTQvtC8IDEwLCDRgdGC0YDQvtC10L3QuNC1IDIxJjAkBgNVBAoMHdCc0LjQvdGG0LjRhNGA0Ysg0KDQvtGB0YHQuNC4MRgwFgYFKoUDZAESDTEwNDc3MDIwMjY3MDExFTATBgUqhQNkBBIKNzcxMDQ3NDM3NTEmMCQGA1UEAwwd0JzQuNC90YbQuNGE0YDRiyDQoNC-0YHRgdC40LiCCmwJwHYAAAAACYwwCgYIKoUDBwEBAwIDQQAvqmRe2MK9ALBRo97pb3f67iP8ek3WGUfv91pT-c3lVvMWTRn-MQbeKtAmsJQ0wmOGPjsEgjLtd8JMUJUJDI3RMYIEGzCCBBcCAQEwggF3MIIBYTEgMB4GCSqGSIb3DQEJARYRdWNfZmtAcm9za2F6bmEucnUxGDAWBgNVBAgMDzc3INCc0L7RgdC60LLQsDEVMBMGBSqFA2QEEgo3NzEwNTY4NzYwMRgwFgYFKoUDZAESDTEwNDc3OTcwMTk4MzAxYDBeBgNVBAkMV9CR0L7Qu9GM0YjQvtC5INCX0LvQsNGC0L7Rg9GB0YLQuNC90YHQutC40Lkg0L_QtdGA0LXRg9C70L7Quiwg0LQuIDYsINGB0YLRgNC-0LXQvdC40LUgMTEZMBcGA1UEBwwQ0LMuINCc0L7RgdC60LLQsDELMAkGA1UEBhMCUlUxLjAsBgNVBAoMJdCa0LDQt9C90LDRh9C10LnRgdGC0LLQviDQoNC-0YHRgdC40LgxODA2BgNVBAMML9Ck0LXQtNC10YDQsNC70YzQvdC-0LUg0LrQsNC30L3QsNGH0LXQudGB0YLQstC-AhBb1iQ06OYU7S_nbUvQhesTMAoGCCqFAwcBAQICoIICOzAYBgkqhkiG9w0BCQMxCwYJKoZIhvcNAQcBMBwGCSqGSIb3DQEJBTEPFw0yNTA4MjAxMjEyNTFaMC8GCSqGSIb3DQEJBDEiBCBvS9MhpS8A7-f05OFc0DENfstByjBIqlWV4nmcdH2IfzCCAc4GCyqGSIb3DQEJEAIvMYIBvTCCAbkwggG1MIIBsTAKBggqhQMHAQECAgQglqo-0XHSoqxmai7UR7xMrVhgEYj_TrAx5PC-PyKeWEEwggF_MIIBaaSCAWUwggFhMSAwHgYJKoZIhvcNAQkBFhF1Y19ma0Byb3NrYXpuYS5ydTEYMBYGA1UECAwPNzcg0JzQvtGB0LrQstCwMRUwEwYFKoUDZAQSCjc3MTA1Njg3NjAxGDAWBgUqhQNkARINMTA0Nzc5NzAxOTgzMDFgMF4GA1UECQxX0JHQvtC70YzRiNC-0Lkg0JfQu9Cw0YLQvtGD0YHRgtC40L3RgdC60LjQuSDQv9C10YDQtdGD0LvQvtC6LCDQtC4gNiwg0YHRgtGA0L7QtdC90LjQtSAxMRkwFwYDVQQHDBDQsy4g0JzQvtGB0LrQstCwMQswCQYDVQQGEwJSVTEuMCwGA1UECgwl0JrQsNC30L3QsNGH0LXQudGB0YLQstC-INCg0L7RgdGB0LjQuDE4MDYGA1UEAwwv0KTQtdC00LXRgNCw0LvRjNC90L7QtSDQutCw0LfQvdCw0YfQtdC50YHRgtCy0L4CEFvWJDTo5hTtL-dtS9CF6xMwCgYIKoUDBwEBAQEEQOaqaTaJbqbwv917bz2BbcfUL1mEjDZln5gW42St6w2y3UKS8tI4V3G_MlOlwTRSzel4SjuRlZIGdBoCispnhJg%3D'
    payload = {
        "grant_type": "refresh_token",
        "client_id": "nspd",
        # "client_id": "ROREESTR26",
        "refresh_token": refresh_token,
        # "redirect_uri": 'https://nspd.gov.ru',
        # "client_secret": client_secret
    }
    headers = {                
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en,ru;q=0.9,en-GB;q=0.8,en-US;q=0.7",
        "cache-control": "no-cache",
        "dnt": "1",
        "origin": "https://nspd.gov.ru",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://nspd.gov.ru/",
        "sec-ch-ua": '''`"Not;A=Brand`";v=`"99`", `"Microsoft Edge`";v=`"139`", `"Chromium`";v=`"139`"''',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '''"`"Windows`""''',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"        
    }
    url = 'https://sso.nspd.gov.ru/oauth2/token'
    # status, response = smart_http_request(s, url=url, method='post', data=payload, headers=headers)
    response = s.post(url, data=payload, headers=headers, verify=False)
    if response.status_code == 200:
        result = json.loads(response.text)
        return result
    else:
        raise Exception(f"Не удалось обновить токен. Результат запроса: {result.content}")    


def download_nspd_settlements(
    s: Session, 
    tiles_gpkg='tiles.gpkg', 
    tiles_layer='kaluga', 
    width=128, 
    height=128, 
    i_from=0, 
    i_to=128, 
    j_from=0, 
    j_to=128, 
    pixel_step=3
):
    # Это чтобы не валились постоянно сообщения о неподтвержденности сертификата. Российские сертификаты сейчас все неподтвержденные.
    from urllib3.exceptions import InsecureRequestWarning
    urllib3.disable_warnings(InsecureRequestWarning)

    current_dir = os.getcwd()
    tiles_gpkg_fullpath = os.path.join(current_dir, tiles_gpkg)
    if os.path.exists(tiles_gpkg_fullpath):
        geojson_result = {
            "type": "FeatureCollection",
            "features": []
        }

        # driver = ogr.GetDriverByName('GPKG')
        gdf = pd.read_file(tiles_gpkg_fullpath, layer=tiles_layer)
        # ds = driver.Open(tiles_gpkg_fullpath)
        # layer = ds.GetLayer(tiles_layer)
        # if layer:
        if not gdf.empty:
            url = "https://nspd.gov.ru/api/aeggis/v3/36281/wms"
            params = {
                "REQUEST": "GetFeatureInfo",
                "SERVICE":"WMS",
                "VERSION": "1.3.0",
                "FORMAT": 'image/png',
                "STYLES": "",
                "TRANSPARENT": "true",
                "LAYERS": "36281",
                "RANDOM": "0.4158997836664142",
                "INFO_FORMAT": "application/json",
                "FEATURE_COUNT": "10",
                "I": "0",
                "J": "0",
                "WIDTH": str(width),
                "HEIGHT": str(height),
                "CRS": "EPSG:3857",
                "BBOX": "7592337.145509988,8000941.147561606,7670608.662474008,8079212.664525626",
                "QUERY_LAYERS": "36281"
                }
            pass
            # for grid_feature in layer:
            for index, row in tqdm(gdf.iterrows(), desc='tiles loop', total=gdf.shape[0]):
                xmin, ymin, xmax, ymax = row['geometry'].bounds
                # extent = grid_feature.geometry().GetEnvelope()
                # xmin, xmax, ymin, ymax = extent
                headers = {
                    "Referer": f"https://nspd.gov.ru/map?thematic=Default&zoom=14.087600258143208&coordinate_x={str((xmin + xmax) / 2)}&coordinate_y={str((ymin + ymax) / 2)}&theme_id=1&is_copy_url=true&active_layers=36281"
                    }
                params["BBOX"] = f"{xmin},{ymin},{xmax},{ymax}"
                for i in range(i_from, i_to + 1, pixel_step):
                    params["I"] = str(i)
                    for j in range(j_from, j_to + 1, pixel_step):
                        params["J"] = str(j)                        
                        status, result = smart_http_request(s, url=url, params=params, headers=headers)
                        if status == 200:
                            jdata = result.json()
                            # geojson_result["features"].extend(jdata["features"])
                            flag = False
                            for feature in jdata["features"]:
                                # if feature["properties"]["options"]["guid"] not in [x["properties"]["options"]["guid"] for x in geojson_result.get("features")]:
                                #     geojson_result["features"].append(feature)
                                if feature["properties"]["options"]["guid"] not in [x["properties"]["guid"] for x in geojson_result.get("features")]:
                                    flag = True
                                    for k, v in feature["properties"]["options"].items():
                                        feature["properties"][k] = v
                                    feature["properties"].pop('options', None)
                                    geojson_result["features"].append(feature)
                pass
            geojson_result_path = os.path.join(current_dir, 'results', f"{tiles_layer}.json")
            with open(geojson_result_path, 'w', encoding='utf-8') as of:
                json.dump(geojson_result, of, ensure_ascii=False)
                return True
        pass
    
    return False


def download_nspd_layer(
    nspd_layer='36281', layer_alias='result',
    tiles_gpkg='tiles.gpkg', tiles_layer='khmao',
    width=128, height=128, i_from=0, i_to=128,
    j_from=0, j_to=128, pixel_step=3,
    access_token='',
    refresh_token='',
    auth_access_token_expires='',
    pause=0
):
    """Функция выполняет выгрузку данных из заданного слоя (WMS-сервиса) НСПД через запрос GetFeatureInfo методом скользящего окна. 
    на вход неоходимо подать Geopackage со слоем тайлов, по которым будет происходить парсинг. 
    Внутри каждого тайла происходит перебор пикселей через заданный шаг, и в каждом пикселе выполняется GetFeatureInfo. 
    После этого объекты с уникальными id записываются в GeoJSON в папку results.  
    Самое главное - это подать на вход начальное значение access_token, refresh_token и auth_access_token_expires для API Госуслуг. 
    Это нужно для того, чтобы программа могла обновлять токен аутентификации Госуслуг и  продолжать работу даже после истечения исходного токена. 
    Чтобы получить исходные значения access_token, refresh_token и auth_access_token_expires, нужно в Google Chrome зайти на сайт 
    https://nspd.gov.ru/map, залогиниться через Госуслуги (часть слоев на карте доступны и без логина. Если нужны эти слои, то логиниться не обязательно). 
    Затем включить devtools (F12), перейти в раздел Network. 
    На странице включить любой тематический слой. После этого в devtools найти любой запрос GetMap. 
    В нем есть Cookie, где кроме прочего записаны текущие значения authAccessToken, authAccessTokenExpires, authRefreshToken. 
    Их надо скопировать и подать на вход функции.
    ВНИМАНИЕ! Есть риск, что работа данной функции будет расценена как DDOS-атака на сайт nspd.gov.ru. 
    Кроме этого, если выполнен логин на Госуслугах, то токен привязывается к этой учетной записи и она отслеживается.

    Args:
        nspd_layer (str, optional): идентификатор слоя на сервере nspd.gov.ru/map. Соответствует отдельному WMS. 
        Чтобы узнать идентификатор нужного вам слоя, включите его на карте, найдите соответствующий запрос GetMap в Devtools/Network. 
        Идентификатор вшит в URL запроса. Defaults to '36281'.
        layer_alias (str, optional): любое краткое название слоя. Будет использовано как имя файла результата. Defaults to 'result'.
        tiles_gpkg (str, optional): Относительный путь к Geopackage со слоем тайлов. Defaults to 'tiles.gpkg'.
        tiles_layer (str, optional): Слой с тайлами. Тайлы можно создать в QGIS инструментом Create grid. 
        Рекомендуемый размер тайлов 78271.517000 x 78271.517000 м. Проекция EPSG:3857. Defaults to 'khmao'.
        width (int, optional): Ширина тайла в пикселах. Рекомендуется 128. Протестировано 512 и 256. Defaults to 128.
        height (int, optional): Высота тайла в пикселах. Рекомендуется 128. Протестировано 512 и 256. Defaults to 128.
        i_from (int, optional): Начало отсчета столбцов пикселов. Defaults to 0.
        i_to (int, optional): Конец отсчета столбцов пикселов. Не может быть больше чем ширина тайла. Defaults to 128.
        j_from (int, optional): Начало отсчета строк пикселов. Defaults to 0.
        j_to (int, optional): Конец отсчета строк пикселов. Не может быть больше чем высота тайла. Defaults to 128.
        pixel_step (int, optional): Шаг перебора пикселов. Может быть от 1 до любого значения (не больше минимального из ширины/высоты). 
        Это промежуток, через который будет выполняться запрос GetFeatureInfo в пикселе. Если 1, то запрос будет в каждом пикселе.
        Общее количество запросов обратно пропорционально квадрату этого шага. Для среднестатистического региона РФ нет смысла брать меньше 3,
        т.к. иначе парсинг выпоняется очень долго. Для больших регионов, как ХМАО, протестирован шаг 9. Defaults to 3.
        access_token (str, optional): Ключ безопасности, первоначальное згачение. Чтобы его получить, нужно в Google Chrome зайти на сайт 
        https://nspd.gov.ru/map, залогиниться через Госуслуги (часть слоев на карте доступны и без логина. Если нужны эти слои, то логиниться не обязательно). 
        Затем включить devtools (F12), перейти в раздел Network. 
        На странице включить любой тематический слой. После этого в devtools найти любой запрос GetMap. 
        В нем есть Cookie, из которого надо скопировать authAccessToken.
        refresh_token (str, optional): Ключ обновления ключа безопасности, первоначальное значение. Получать аналогично access_token,
        но взять параметр authRefreshToken. Defaults to ''.
        auth_access_token_expires (str, optional): срок истечения ключа безопасности, первоначальное значение. Получать аналогично access_token,
        но взять параметр authAccessTokenExpires. Пример - %222025-08-24T06%3A16%3A00.521Z%22. Defaults to ''.
        pause (int, optional): пауза между запросами GetFeatureInfo, чтобы снизить риск обвинений в атаке. Defaults to 0.

    Returns:
        tuple: В случае успешного выполнения, функция сохраняет загруженные данные в файл results/<tiles_layer>_<layer_alias>.json
        в формате GeoJSON, А ТАКЖЕ возвращает кортеж с последними актуальными значениями access_token, refresh_token, auth_access_token_expires.
        Это можно использовать для запуска функции в цикле для нескольких слоев.
    """
    # Это чтобы не валились постоянно сообщения о неподтвержденности сертификата. Российские сертификаты сейчас все неподтвержденные.
    from urllib3.exceptions import InsecureRequestWarning
    urllib3.disable_warnings(InsecureRequestWarning)
    
    # Конвертация времени истечения токена в datetime
    try:
        auth_access_token_expires = utils.unquote(auth_access_token_expires).replace('"', '')
        auth_access_token_expires_dt = datetime.strptime(auth_access_token_expires, '%Y-%m-%dT%H:%M:%S.%fZ')
        utc_tz = pytz.timezone('utc')
        auth_access_token_expires_dt = utc_tz.localize(auth_access_token_expires_dt)    # Это чтобы время было локализовано в UTC
    except Exception:
        raise ValueError("некорректный параметр auth_access_token_expires")
    
    if any([not access_token, not refresh_token]):
        raise ValueError("Не заданы токены access_token и/или refresh_token")
    
    # Создать папку results, если ее нет
    current_dir = os.getcwd()
    if not os.path.isdir(os.path.join(current_dir, 'results')):
        os.mkdir(os.path.join(current_dir, 'results'))
    
    tiles_gpkg_fullpath = os.path.join(current_dir, tiles_gpkg)
    if os.path.exists(tiles_gpkg_fullpath) and access_token and refresh_token and auth_access_token_expires:
        geojson_result = {
            "type": "FeatureCollection",
            "features": []
        }
        url = f"https://nspd.gov.ru/api/aeggis/v3/{nspd_layer}/wms"
        params = {
                "REQUEST": "GetFeatureInfo",
                "SERVICE":"WMS",
                "VERSION": "1.3.0",
                "FORMAT": 'image/png',
                "STYLES": "",
                "TRANSPARENT": "true",
                "LAYERS": nspd_layer,
                "RANDOM": "0.32651699381268684",
                "INFO_FORMAT": "application/json",
                "FEATURE_COUNT": "10",
                "I": "0",
                "J": "0",
                "WIDTH": str(width),
                "HEIGHT": str(height),
                "CRS": "EPSG:3857",
                "BBOX": "7592337.145509988,8000941.147561606,7670608.662474008,8079212.664525626",
                "QUERY_LAYERS": nspd_layer
                }
        gdf = pd.read_file(tiles_gpkg_fullpath, layer=tiles_layer)
        with Session() as s:
            # https://tqdm.github.io/docs/tqdm/
            # stdout будет показывать прогресс-бар по перебору тайлов
            for index, row in tqdm(gdf.iterrows(), desc='tiles loop', total=gdf.shape[0]):
                xmin, ymin, xmax, ymax = row['geometry'].bounds
                headers = {
                        "accept": '*/*',
                        "accept-encoding": "gzip, deflate, br, zstd",
                        "accept-language": "en,ru;q=0.9,en-GB;q=0.8,en-US;q=0.7",
                        "cache-control": "no-cache",
                        "Dnt": "1",
                        "pragma": "no-cache",
                        "priority": "u=1, i",                        
                        # "Referer": f"https://nspd.gov.ru/map?thematic=Default&zoom=14.087600258143208&coordinate_x={str((xmin + xmax) / 2)}&coordinate_y={str((ymin + ymax) / 2)}&theme_id=1&is_copy_url=true&active_layers={nspd_layer}",
                        "Referer": f"https://nspd.gov.ru/map?zoom=14.087600258143208&coordinate_x={str((xmin + xmax) / 2)}&coordinate_y={str((ymin + ymax) / 2)}&baseLayerId=235&theme_id=99&is_copy_url=true&active_layers={nspd_layer}",
                        "sec-ch-ua": '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": '"Windows"',
                        "sec-fetch-dest": "empty",
                        "sec-fetch-mode": "cors",
                        "sec-fetch-site": "same-origin",
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",                        
                        # "Origin": "https://nspd.gov.ru",
                        'Authorization': f"Bearer {access_token}"
                        # "cookie": cookie
                        }
                params["BBOX"] = f"{xmin},{ymin},{xmax},{ymax}"
                for i in range(i_from, i_to + 1, pixel_step):
                    params["I"] = str(i)
                    for j in range(j_from, j_to + 1, pixel_step):
                        params["J"] = str(j)
                        cur_datetime_utc = datetime.now(timezone.utc)
                        # Обновляем токен за 10 минут до его истечения, т.к. если сайт остался открытым в браузере, то там обновление идет за несколько минут до срока
                        if auth_access_token_expires_dt <= cur_datetime_utc + timedelta(minutes=10):
                            refreshed_auth = request_refresh_token(s, refresh_token)
                            auth_access_token_expires_dt = cur_datetime_utc + timedelta(seconds=int(refreshed_auth.get('expires_in')))
                            access_token = refreshed_auth.get('access_token')
                            refresh_token = refreshed_auth.get('refresh_token')
                        headers['Authorization'] = f"Bearer {access_token}"
                        if pause > 0:
                            sleep(pause)                            
                        status, result = smart_http_request(s, url=url, params=params, headers=headers)
                        # result = s.get(url, params=params, headers=headers, verify=False)
                        # status = result.status_code
                        if status == 200:
                            jdata = result.json()
                            for feature in jdata["features"]:
                                pass
                                if feature["id"] not in [x["id"] for x in geojson_result.get("features")]:
                                    for k, v in feature["properties"]["options"].items():
                                        feature["properties"][k] = v
                                    feature["properties"].pop('options', None)
                                    geojson_result["features"].append(feature)
        geojson_result_path = os.path.join(current_dir, 'results', f"{tiles_layer}_{layer_alias}.json")
        with open(geojson_result_path, 'w', encoding='utf-8') as of:
            json.dump(geojson_result, of, ensure_ascii=False)
            return (access_token, refresh_token, auth_access_token_expires)


if __name__ == '__main__':
    # Это пример отдельных слоев, которые можно парсить. Функции download_nspd_layer надо кроме прочего подать на вход id слоя
    nspd_layers = [
        # {"shortname": "югра_маг_труб", "id": "847064", "fullname": "ЮГРА - Магистральные трубопроводы для транспортировки жидких и газообразных углеводородов"},
        # {"shortname": "югра_доб_транс_газ", "id": "848517", "fullname": "ЮГРА - Объекты добычи и транспортировки газа"},
        # {"shortname": "югра_распред_труб_газ", "id": "844383", "fullname": "ЮГРА - Распределительные трубопроводы для транспортировки газа"},
        # {"shortname": "югра_доб_транс_ж_ув", "id": "847799", "fullname": "ЮГРА - Объекты добычи и транспортировки жидких углеводородов"},
        # {"shortname": "югра_труб_ж_ув", "id": "847076", "fullname": "ЮГРА - Трубопроводы жидких углеводородов"},
        # {"shortname": "югра_уч_доп_пи_и_др", "id": "847178", "fullname": "ЮГРА - Участки недр, предоставленных для добычи полезных ископаемых, а также в целях, не связанных с их добычей"},
        # {"shortname": "югра_местор_пи_пол", "id": "847284", "fullname": "ЮГРА - Месторождения и проявления полезных ископаемых (полигон)"},
        # {"shortname": "югра_местор_пи_тчк", "id": "848623", "fullname": "ЮГРА - Месторождения и проявления полезных ископаемых (точка)"},
        # {"shortname": "югра_функц_зон", "id": "847282", "fullname": "ЮГРА - Функциональные зоны"},
        # {"shortname": "сан_курорт", "id": "848566", "fullname": "Объекты санаторно-курортного назначения"}
        {"shortname": "зоуит", "id": "37581", "fullname": "Объекты санаторно-курортного назначения"}
    ]
    
    # Перед использованием нужно зайти на https://nspd.gov.ru/map браузером, залогиниться, включить нужный слой на карте,
    # и скопировать значение access_token, refresh_token и auth_access_token_expires из cookie любого запроса GetMap.
    # Пример cookie:
    # _ym_uid=1756110247627323266; _ym_d=1756110247; _ym_isad=1; 
    # authAccessToken=eyJhbGci<тут длинющая строка>; authAccessTokenExpires=%222025-08-25T10%3A01%3A11.688Z%22; 
    # authRefreshToken=c7M8ixRGrknyW4xuDAkcQxRdWbhluEvR6Qf7Ki70aL2ALxLyaJqfj0p3knOQOqu4o7w1ZZeAQRNQrafJy5
    #
    # В этом примере:
    # access_token = 'eyJhbGci<тут длинющая строка>'
    # auth_access_token_expires = '%222025-08-25T10%3A01%3A11.688Z%22'
    # refresh_token = 'c7M8ixRGrknyW4xuDAkcQxRdWbhluEvR6Qf7Ki70aL2ALxLyaJqfj0p3knOQOqu4o7w1ZZeAQRNQrafJy5'
       
    # ЗАМЕНИТЬ!!!
    # cookie = '_ym_uid=1757065220249938669; _ym_d=1757065220; _ym_isad=1; _ym_visorc=w; authAccessToken=eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiIwMzM4NmRiZS01MTg1LTRiOTYtOTAwZC1jMmIxYmIzNjhlZDYiLCJjbGllbnRfaWQiOiIwMzM4NmRiZS01MTg1LTRiOTYtOTAwZC1jMmIxYmIzNjhlZDYiLCJkaXNwbGF5X25hbWUiOiLQntGB0L7QutC40L0g0KHRgtC10L_QsNC9INCQ0YDRgtC10LzQvtCy0LjRhyIsImVtYWlsIjoic3RlcGFub3Nva2luQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU3MDcyMzc3LCJleHBpcmVzX2luIjoxODAwLCJmYW1pbHlfbmFtZSI6ItCe0YHQvtC60LjQvSIsImdpdmVuX25hbWUiOiLQodGC0LXQv9Cw0L0iLCJpYXQiOjE3NTcwNzA1NzcsImlzcyI6Imh0dHBzOi8vc3NvLm5zcGQuZ292LnJ1IiwianRpIjoiNTViZWM3MWQtMGQ0MC00NWNkLWE5Y2ItODEyODQyMjk0Mzc1IiwibG9jYWxlIjoiZW4iLCJtaWRkbGVfbmFtZSI6ItCQ0YDRgtC10LzQvtCy0LjRhyIsIm5hbWUiOiLQntGB0L7QutC40L0g0KHRgtC10L_QsNC9INCQ0YDRgtC10LzQvtCy0LjRhyIsInByZWZlcnJlZF91c2VybmFtZSI6InAtMTIxLTI5OS02MTcgNTEiLCJzY29wZSI6InByb2ZpbGUgZW1haWwgdWlkIiwic2lkIjoiNWJhYTI2ZDktNTMyMy00MGU1LTgxOTktMzZjOGY3MWVhNTRjIiwic3ViIjoiMjQxNWUzM2ItZmU4OC00Y2IzLWE4ZTctNDIyNjQyOTU0OGE5IiwidWlkIjoiMjQxNWUzM2ItZmU4OC00Y2IzLWE4ZTctNDIyNjQyOTU0OGE5IiwidXBkYXRlZF9hdCI6MTc1NzA3MDU3NX0.FPMw5VrSODeJ7d4EiOYMHFlNaS9FMCg7LCveRrloD0qhJNZVT-jC47G2kprQQw_HUbLbQSHPNER95FOdjbk4RfusqBfAHr7_cx4L7J9EPJL8hMOk5qKqxNn_uX84NmgBD7Nz8pyuY_JMWIWhRurle6ntYkOUy0x9L9mHfVFmEQXKt_MTTmVdgmIfI6imKluB8jiWbbBVOEm2oktdscU5epgLQeMPRLBC9rBcq3mgrLuYSLXkcxyEdIZ_V16xpzlcyLUNDCo_nR4Y-PcmlOzRQW84LuQs-xNpoEWlalhr6Zs2NQ-2Y-PSHfppe2VPzbi4-rXrcGsAgBTtrI5iy--YLLlkg8H_qZNxYhSyRXTIP8-cSc1fFU0jfD6pD3oF1KJvERqiUoqYfXLRRNkD3Mk8DLVvWtdTU5Sa3_qPNMfefcrSjht4EZayK_I5azSgedjFT3JVTgOBkHx3SX3GE2i-SdKS5OviTHjCIka-JjE1a4utWAqkJAAyPeD-YJ5tKGDjpiwystuyktzM1vpvscG5Yw590BrKxmXWjjQY79ykjVugg3dzWCNa9RDlEhgnBvxpKVn9M-PQ7M6PPpF-qdKhEWw9BlhfT3wvbAjllGJosszjScfQ7VQ2iDXe7v5ZvEMVrdDB9hjOXkkDKjuTmwfu-lYDeWjOF8hJTZodae6eXRI; authAccessTokenExpires=%222025-09-05T11%3A39%3A37.493Z%22; authRefreshToken=c7MJZk9xIUqKX5HwR6mLWpBS4HEvjUbeAStYhBnZiMvB7oMzQVqevP5IGbuEbJ6VlNkKA6WZLpmlCB6not'
    access_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiIwMzM4NmRiZS01MTg1LTRiOTYtOTAwZC1jMmIxYmIzNjhlZDYiLCJjbGllbnRfaWQiOiIwMzM4NmRiZS01MTg1LTRiOTYtOTAwZC1jMmIxYmIzNjhlZDYiLCJkaXNwbGF5X25hbWUiOiLQntGB0L7QutC40L0g0KHRgtC10L_QsNC9INCQ0YDRgtC10LzQvtCy0LjRhyIsImVtYWlsIjoic3RlcGFub3Nva2luQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzYzNjQ0ODczLCJleHBpcmVzX2luIjoxODAwLCJmYW1pbHlfbmFtZSI6ItCe0YHQvtC60LjQvSIsImdpdmVuX25hbWUiOiLQodGC0LXQv9Cw0L0iLCJpYXQiOjE3NjM2NDMwNzMsImlzcyI6Imh0dHBzOi8vc3NvLm5zcGQuZ292LnJ1IiwianRpIjoiNDk1MzkxMWYtYmQ0Yi00MzljLTlhYjMtNGFmYjRiMDk4MmIyIiwibG9jYWxlIjoiZW4iLCJtaWRkbGVfbmFtZSI6ItCQ0YDRgtC10LzQvtCy0LjRhyIsIm5hbWUiOiLQntGB0L7QutC40L0g0KHRgtC10L_QsNC9INCQ0YDRgtC10LzQvtCy0LjRhyIsInByZWZlcnJlZF91c2VybmFtZSI6InAtMTIxLTI5OS02MTcgNTEiLCJzY29wZSI6InByb2ZpbGUgZW1haWwgdWlkIiwic2lkIjoiZTVhNGFlNjktYjcyNS00YmM4LTllMTMtYzc4MWE4MGJjMDQ2Iiwic3ViIjoiMjQxNWUzM2ItZmU4OC00Y2IzLWE4ZTctNDIyNjQyOTU0OGE5IiwidWlkIjoiMjQxNWUzM2ItZmU4OC00Y2IzLWE4ZTctNDIyNjQyOTU0OGE5IiwidXBkYXRlZF9hdCI6MTc2MzY0MzA3Mn0.w2F0Bciccr4V-4nCBUAbzsrXoEe3KjTeX243dK8hvcOnkVRigYWBBoU7WVP9NIu1jpdAjg9A7_GBYycpF11irrv3k7eX3gEOeP6GBIu9C-aOOUvEpryZyXT89d0CquzzOjKc8Leaj-NS5jlwEyUeHVpU834BrWBw4fjS1tiAjiozmXlpTceDwV02rpQrp2UcPmVoboP1MMPPN8rk20MSNyVa21wd_oIe-eRcIyZHLFaJBcOMRE-OVW_3H-yfjBDkHUipTcLJP4EjZQrmFXp0znQunxqWezh6ecWVYSNEEEXXrK9fhAba9dLPSqqoDTHS0Pw6kxTd7_kkAYJS2VToznu6uFtH_V_2EcXCu3inMw8nFEjf8KqVoP-48X_F_ThLZRAtiggTxz9KF8RVyS9rja6hYm4hityk5GMG6L4FHHUbKZoauv40_x0t5P35lV-gktHECx0ZRr2x16ElCMefEvokkmFyGqdthC92HqZ8mckqb71XejxAYmEf8Yzdh5ee89Ei0m8vLM4Bygxz_ic2LsnrkTGrJZqgwTZDSyGfSnd4sWDHAsGqIAhiZV7ZprBcUVnU24-JhTdvMyCzK8vIbeOh5Q4cqFbjbV7QdTsmuDEHj5H-4sA379nHNV0WdrEP8D6uoniDmowJZfSvpByizLCF7FDnWnL_nGo3GaGkvnQ'
    auth_access_token_expires = '%222025-11-20T13%3A21%3A13.384Z%22'
    refresh_token = 'c7NW9dqYwJuAhVVr3dA9CKDvmCGul25gFTxboBXN4SwFdms9UY2JGLtDTMWkGJnJcdkstvBeCl203CMjms'    
    
    # пример того, как можно перебирать слои в цикле и парсить по очереди.
    for layer in nspd_layers:
        # if layer['shortname'] == 'югра_доб_транс_газ':   # это просто чтобы парсить какой-то один слой, можно и убрать
        access_token, refresh_token, auth_access_token_expires = download_nspd_layer(
            nspd_layer=layer['id'],                     # идентификатор слоя, взятый из URL запроса на nspd.gov.ru/map
            layer_alias=layer['shortname'],             # любое короткое имя слоя
            tiles_gpkg='nspd_zouit.gpkg',
            tiles_layer='grid_zatop',                        # В Geopackage должен быть этот слой с тайлами
            width=128, height=128,                      # рекомендованные значения для размера тайла 128x128
            i_from=0, i_to=128, j_from=0, j_to=128,     # в общем случае, должно совпадать с widht и height
            pixel_step=5,                               # Для ХМАО рекомендовано 9. Для регионов поменьше можно 3.
            access_token=access_token,                  # при первом запуске цикла берутся значения, заданные в разделе "ЗАМЕНИТЬ!!!". Потом будут браться автоматом из данных, возвращаемых функцией.
            refresh_token=refresh_token,
            auth_access_token_expires=auth_access_token_expires,
            pause=0
        )
        print(f"access_token: {access_token}; refresh_token: {refresh_token}; auth_access_token_expires: {auth_access_token_expires}")

# Запуск скрипта:
# 1. Установить uv https://docs.astral.sh/uv/getting-started/installation/
# 2. в папке проекта: uv sync
# 3. Заменить значения в разделе "ЗАМЕНИТЬ!!!"
# 4. Запустить данный файл в IDE или командой uv run hse_nspd.py
#    Будет отображен прогресс-бар по перебору тайлов