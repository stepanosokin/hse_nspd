from requests import Session
from vgdb_general import smart_http_request
import geopandas as pd
import os
import json


def refresh_token(s: Session, refresh_token=''):    # не работает
    data = {
        "grant_type": "refresh_token",
        "client_id": "nspd",
        "refresh_token": refresh_token
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
    status, result = smart_http_request(s, url=url, method='post', data=data, headers=headers)
    # result = s.post(url, data=params, headers=headers, verify=False)
    pass
    if status == 200:
        return result.json()
    return None


def download_nspd_layer(
    nspd_layer='36281', layer_alias='result',
    tiles_gpkg='tiles.gpkg', tiles_layer='khmao',
    width=512, height=512, i_from=0, i_to=512,
    j_from=0, j_to=512, pixel_step=3,
    cookie='',
    token=''
):
    current_dir = os.getcwd()
    tiles_gpkg_fullpath = os.path.join(current_dir, tiles_gpkg)
    if os.path.exists(tiles_gpkg_fullpath):
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
                "RANDOM": "0.4158997836664142",
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
            for index, row in gdf.iterrows():            
                xmin, ymin, xmax, ymax = row['geometry'].bounds
                headers = {
                        "Referer": f"https://nspd.gov.ru/map?thematic=Default&zoom=14.087600258143208&coordinate_x={str((xmin + xmax) / 2)}&coordinate_y={str((ymin + ymax) / 2)}&theme_id=1&is_copy_url=true&active_layers={nspd_layer}",
                        "Dnt": "1",
                        "Origin": "https://nspd.gov.ru",
                        'Authorization': f"Bearer {token}"
                        # "cookie": cookie
                        }
                params["BBOX"] = f"{xmin},{ymin},{xmax},{ymax}"
                for i in range(i_from, i_to + 1, pixel_step):
                    params["I"] = str(i)
                    for j in range(j_from, j_to + 1, pixel_step):
                        params["J"] = str(j)   
                        status, result = smart_http_request(s, url=url, params=params, headers=headers)
                        # result = s.get(url, params=params, headers=headers, verify=False)
                        # status = result.status_code
                        if status == 200:
                            jdata = result.json()
                            for feature in jdata["features"]:
                                # if feature["properties"]["options"]["guid"] not in [x["properties"]["guid"] for x in geojson_result.get("features")]:
                                if feature["id"] not in [x["id"] for x in geojson_result.get("features")]:
                                    for k, v in feature["properties"]["options"].items():
                                        feature["properties"][k] = v
                                    feature["properties"].pop('options', None)
                                    geojson_result["features"].append(feature)
        geojson_result_path = os.path.join(current_dir, 'results', f"{tiles_layer}_{layer_alias}.json")
        with open(geojson_result_path, 'w', encoding='utf-8') as of:
            json.dump(geojson_result, of, ensure_ascii=False)
            return True


if __name__ == '__main__':
    nspd_layers = [
        {"shortname": "югра_маг_труб", "id": "847064", "fullname": "ЮГРА - Магистральные трубопроводы для транспортировки жидких и газообразных углеводородов"},
        {"shortname": "югра_доб_транс_газ", "id": "848517", "fullname": "ЮГРА - Объекты добычи и транспортировки газа"},
        {"shortname": "югра_распред_труб_газ", "id": "844383", "fullname": "ЮГРА - Распределительные трубопроводы для транспортировки газа"},
        {"shortname": "югра_доб_транс_ж_ув", "id": "847799", "fullname": "ЮГРА - Объекты добычи и транспортировки жидких углеводородов"},
        {"shortname": "югра_труб_ж_ув", "id": "847076", "fullname": "ЮГРА - Трубопроводы жидких углеводородов"},
        {"shortname": "югра_уч_доп_пи_и_др", "id": "847178", "fullname": "ЮГРА - Участки недр, предоставленных для добычи полезных ископаемых, а также в целях, не связанных с их добычей"},
        {"shortname": "югра_местор_пи_пол", "id": "847284", "fullname": "ЮГРА - Месторождения и проявления полезных ископаемых (полигон)"},
        {"shortname": "югра_местор_пи_тчк", "id": "848623", "fullname": "ЮГРА - Месторождения и проявления полезных ископаемых (точка)"},
        {"shortname": "югра_функц_зон", "id": "847282", "fullname": "ЮГРА - Функциональные зоны"}
    ]
    # # cookie = "_ym_uid=1755248586340956431; _ym_d=1755248586; _ym_isad=1; authAccessToken=eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiIwMzM4NmRiZS01MTg1LTRiOTYtOTAwZC1jMmIxYmIzNjhlZDYiLCJjbGllbnRfaWQiOiIwMzM4NmRiZS01MTg1LTRiOTYtOTAwZC1jMmIxYmIzNjhlZDYiLCJkaXNwbGF5X25hbWUiOiLQntGB0L7QutC40L0g0KHRgtC10L_QsNC9INCQ0YDRgtC10LzQvtCy0LjRhyIsImVtYWlsIjoic3RlcGFub3Nva2luQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU1MjU1OTgxLCJleHBpcmVzX2luIjoxODAwLCJmYW1pbHlfbmFtZSI6ItCe0YHQvtC60LjQvSIsImdpdmVuX25hbWUiOiLQodGC0LXQv9Cw0L0iLCJpYXQiOjE3NTUyNTQxODEsImlzcyI6Imh0dHBzOi8vc3NvLm5zcGQuZ292LnJ1IiwianRpIjoiMzYzODIyYWEtYjI1My00ZjZmLWFkZTYtZDYwNGZhNzAwN2U4IiwibG9jYWxlIjoiZW4iLCJtaWRkbGVfbmFtZSI6ItCQ0YDRgtC10LzQvtCy0LjRhyIsIm5hbWUiOiLQntGB0L7QutC40L0g0KHRgtC10L_QsNC9INCQ0YDRgtC10LzQvtCy0LjRhyIsInByZWZlcnJlZF91c2VybmFtZSI6InAtMTIxLTI5OS02MTcgNTEiLCJzY29wZSI6InByb2ZpbGUgZW1haWwgdWlkIiwic2lkIjoiZjU3YzI3NjQtZmFhZi00YzJhLTlhYTktMzNjODM1YjY1NDVhIiwic3ViIjoiMjQxNWUzM2ItZmU4OC00Y2IzLWE4ZTctNDIyNjQyOTU0OGE5IiwidWlkIjoiMjQxNWUzM2ItZmU4OC00Y2IzLWE4ZTctNDIyNjQyOTU0OGE5IiwidXBkYXRlZF9hdCI6MTc1NTI0ODc3OH0.De_xZq6xAQ3wePuaNbhAmIN8vbFPCdzdt8kRA7iX55QfYUSQfA_xpkE0GyYTI35rLotGX-NauvJUS-Vt4cdJzqzOOByeidk0fL6ZF9Xl2fnp9MyU6L3Bqqt2usx_Tx-lcyLR3doOUVkAdWtyihPMSH86XuB1hsf1EMwgSC5nTGcaC6wF0U0e3Cx8s4n1gbecHKVuT7gHuhDy06Iq9VZxCHO1JRlFiJfUHdG-8XGTWVh1UVnmpRYHSM3d-MG9-sscQ6EpyfDn1pXAMDJgMzFfg2IGa0b2MBSG7tOwVCTW1vqWB2I8cj8mjbgL4Zur0p8FY2l1CoqXirktCJ29vkExqAuo8_3fSEH4qKQbqlfwqoh0GcMvTFvioKUYJMPhlawnWEWVogcLtb6GAj523HkvPtln-LHwfX_TjjMu0ElFOnwRbePzVKgzXNzd8adDYIrAe9STwDbwyfnxRnHzWz8g6O2S_zJ0iTvI_h-XqqTeB_TM9YT7LwhFvG6_ihCcvwioMkVzZmMLX_NKu-tS36AU2Gdh4WbraD6b1vK6ztjUzh4lIPL8N4shMfGfY8DqJcnWXDg8fP8VNDGzlkQ8VuhWxuqtfCVZ13yBogrJl5ypKST7_9RYXevl3SyWWqvv93KVO7choKnyCaa_1u64AShO1pVWF9HX61VnsXzStkJzLg8; authAccessTokenExpires=%222025-08-15T11%3A06%3A23.127Z%22; authRefreshToken=c7Lyxrst15Ho028RyB7HNS5NqcUAtR6GCUobkXUoHVatbFN3Bg9xWeQHGBZMhE8HwB0prL40ssq7ZGJiQK"
    
    # Перед использованием нужно зайти на https://nspd.gov.ru/map браузером, залогиниться, включить нужный слой на карте,
    # и скопировать значение токена из cookie любого запроса GetMap.
    # После этого оставить страницу висеть. Идея в том, что браузер будет сам обновлять этот токен.
    # Refresh Token каждый раз разный, а Auth Token - один и тот же.
    # Нет это не работает - токен меняется при каждом обновлении
    
    # ЗАМЕНИТЬ!!!
    token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiIwMzM4NmRiZS01MTg1LTRiOTYtOTAwZC1jMmIxYmIzNjhlZDYiLCJjbGllbnRfaWQiOiIwMzM4NmRiZS01MTg1LTRiOTYtOTAwZC1jMmIxYmIzNjhlZDYiLCJkaXNwbGF5X25hbWUiOiLQntGB0L7QutC40L0g0KHRgtC10L_QsNC9INCQ0YDRgtC10LzQvtCy0LjRhyIsImVtYWlsIjoic3RlcGFub3Nva2luQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU1MjY2OTEwLCJleHBpcmVzX2luIjoxODAwLCJmYW1pbHlfbmFtZSI6ItCe0YHQvtC60LjQvSIsImdpdmVuX25hbWUiOiLQodGC0LXQv9Cw0L0iLCJpYXQiOjE3NTUyNjUxMTAsImlzcyI6Imh0dHBzOi8vc3NvLm5zcGQuZ292LnJ1IiwianRpIjoiOWQzZmQ5NTktM2RmNy00NDhjLWI4OTctNDMxYmVkY2ZlY2UxIiwibG9jYWxlIjoiZW4iLCJtaWRkbGVfbmFtZSI6ItCQ0YDRgtC10LzQvtCy0LjRhyIsIm5hbWUiOiLQntGB0L7QutC40L0g0KHRgtC10L_QsNC9INCQ0YDRgtC10LzQvtCy0LjRhyIsInByZWZlcnJlZF91c2VybmFtZSI6InAtMTIxLTI5OS02MTcgNTEiLCJzY29wZSI6InByb2ZpbGUgZW1haWwgdWlkIiwic2lkIjoiZjU3YzI3NjQtZmFhZi00YzJhLTlhYTktMzNjODM1YjY1NDVhIiwic3ViIjoiMjQxNWUzM2ItZmU4OC00Y2IzLWE4ZTctNDIyNjQyOTU0OGE5IiwidWlkIjoiMjQxNWUzM2ItZmU4OC00Y2IzLWE4ZTctNDIyNjQyOTU0OGE5IiwidXBkYXRlZF9hdCI6MTc1NTI2NTEwOX0.SqT44E8NGO3etgJ4PFZK2F9WEo_1v8tifPJ0hp5tH2m0noHOClzr3cydbSoEbNQnu8HLziptT4cQgNAib9U9sXigRO1WSvXSxVgy0vxapxTFan5EivfRgz5dihScciGWx3M8AKd6ikz6_pBtLWQIC87fwExqzWUpPjBvvtUSoRMsXCiVYTsrAMrp3Cz8jvoebpxFHFSNxRIUPe7Ljlwv1MfapqIS5PwyTdh1pIaOOTrY_A1QbH38OvOwlqDvwFG0WcShFicHuvn-EMR_eXAOHmHEbf5L5jdEMhV5b2gTPgiMK_cJbxKTVHa_p4Goj88cWJnWxNdnwbu9SpZSZaCXm-JxDjG0obPkJt2Lv9b5UkQMJZ6ICsOmttQji6HPdKeYYhzPMV745DgbexvuNVuc6ODGOpWKGdz79G2kyUgv_G-pWQ8jPT9bARpvyWO5BJ4Pu9Z1itZey9S0JAgjAFD2KcWK7-NLI0KNPGxOK88rNxl3guwXmCnUPMQeDRdypajT0cI7xsbVkoYU3NkmFbueq7TYMMd9rZv36IKJT3h4hFl4w56IBPUGqPJkvzkDEsd63kwx1FHyWaxOs0srH43VA38TVQz--WGSCFtGeBY_7iLID02MtVcBgIk0BjMY_w_iafbzX6XuO3TZLiRGW1VTW8rSbgoZyJq3JebuvxYng38'
    
    for layer in nspd_layers:
        if layer['shortname'] == 'югра_маг_труб':
            download_nspd_layer(
                nspd_layer=layer['id'],
                layer_alias=layer['shortname'],
                tiles_gpkg='tiles.gpkg',
                tiles_layer='test',
                width=128, height=128, 
                i_from=0, i_to=128, j_from=0, j_to=128, 
                pixel_step=3,
                # cookie=cookie,
                token=token
            )
    
    # # Это не работает
    # with Session() as s:
    #     token_response = refresh_token(s, refresh_token="c7Lz4CfOSTf0c3c1YsEYFmE9JcH1Kd2RHgd7aZCaoaRUiUkDyFTRki2211y513ajLaaZU3fKkcO98l4tIc")
    #     pass