from requests import Session, utils
from vgdb_general import smart_http_request
import geopandas as pd
import os
import json
import brotli
from datetime import datetime, timezone, timedelta
import pytz


def request_refresh_token(s: Session, refresh_token=''):    # не работает
    client_secret = 'MIINVwYJKoZIhvcNAQcCoIINSDCCDUQCAQExDDAKBggqhQMHAQECAjALBgkqhkiG9w0BBwGgggkDMIII_zCCCKygAwIBAgIQW9YkNOjmFO0v521L0IXrEzAKBggqhQMHAQEDAjCCAWExIDAeBgkqhkiG9w0BCQEWEXVjX2ZrQHJvc2them5hLnJ1MRgwFgYDVQQIDA83NyDQnNC-0YHQutCy0LAxFTATBgUqhQNkBBIKNzcxMDU2ODc2MDEYMBYGBSqFA2QBEg0xMDQ3Nzk3MDE5ODMwMWAwXgYDVQQJDFfQkdC-0LvRjNGI0L7QuSDQl9C70LDRgtC-0YPRgdGC0LjQvdGB0LrQuNC5INC_0LXRgNC10YPQu9C-0LosINC0LiA2LCDRgdGC0YDQvtC10L3QuNC1IDExGTAXBgNVBAcMENCzLiDQnNC-0YHQutCy0LAxCzAJBgNVBAYTAlJVMS4wLAYDVQQKDCXQmtCw0LfQvdCw0YfQtdC50YHRgtCy0L4g0KDQvtGB0YHQuNC4MTgwNgYDVQQDDC_QpNC10LTQtdGA0LDQu9GM0L3QvtC1INC60LDQt9C90LDRh9C10LnRgdGC0LLQvjAeFw0yNDA4MDIxMjMxMDNaFw0yNTEwMjYxMjMxMDNaMIIB8DELMAkGA1UEBhMCUlUxGTAXBgNVBAgMENCzLiDQnNC-0YHQutCy0LAxMjAwBgNVBAkMKdGD0LsuINCS0L7RgNC-0L3RhtC-0LLQviDQv9C-0LvQtSwg0LQuNNCwMRUwEwYDVQQHDAzQnNC-0YHQutCy0LAxgZAwgY0GA1UECgyBhdCk0JXQlNCV0KDQkNCb0KzQndCQ0K8g0KHQm9Cj0JbQkdCQINCT0J7QodCj0JTQkNCg0KHQotCS0JXQndCd0J7QmSDQoNCV0JPQmNCh0KLQoNCQ0KbQmNCYLCDQmtCQ0JTQkNCh0KLQoNCQINCYINCa0JDQoNCi0J7Qk9Cg0JDQpNCY0JgxGDAWBgUqhQNkARINMTA0Nzc5Njk0MDQ2NTEVMBMGBSqFA2QEEgo3NzA2NTYwNTM2MSQwIgYJKoZIhvcNAQkBFhUwMF9vemlsMUByb3NyZWVzdHIucnUxgZAwgY0GA1UEAwyBhdCk0JXQlNCV0KDQkNCb0KzQndCQ0K8g0KHQm9Cj0JbQkdCQINCT0J7QodCj0JTQkNCg0KHQotCS0JXQndCd0J7QmSDQoNCV0JPQmNCh0KLQoNCQ0KbQmNCYLCDQmtCQ0JTQkNCh0KLQoNCQINCYINCa0JDQoNCi0J7Qk9Cg0JDQpNCY0JgwZjAfBggqhQMHAQEBATATBgcqhQMCAiQABggqhQMHAQECAgNDAARAncHiBpT5hZi7kZb56fbzY5aKGGryq-bvSk5b-cRfy8Bj6_EXcSF2ZS9MHVG39usPSdREzeQyT3-TOd87XLN99KOCBKQwggSgMA4GA1UdDwEB_wQEAwID-DAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwEwYDVR0gBAwwCjAIBgYqhQNkcQEwDAYFKoUDZHIEAwIBATAtBgUqhQNkbwQkDCLQmtGA0LjQv9GC0L7Qn9GA0L4gQ1NQICg1LjAuMTIwMDApMIIBoQYFKoUDZHAEggGWMIIBkgyBh9Cf0YDQvtCz0YDQsNC80LzQvdC-LdCw0L_Qv9Cw0YDQsNGC0L3Ri9C5INC60L7QvNC_0LvQtdC60YEgVmlQTmV0IFBLSSBTZXJ2aWNlICjQvdCwINCw0L_Qv9Cw0YDQsNGC0L3QvtC5INC_0LvQsNGC0YTQvtGA0LzQtSBIU00gMjAwMFEyKQxo0J_RgNC-0LPRgNCw0LzQvNC90L4t0LDQv9C_0LDRgNCw0YLQvdGL0Lkg0LrQvtC80L_Qu9C10LrRgSDCq9Cu0L3QuNGB0LXRgNGCLdCT0J7QodCiwrsuINCS0LXRgNGB0LjRjyA0LjAMTUPQtdGA0YLQuNGE0LjQutCw0YIg0YHQvtC-0YLQstC10YLRgdGC0LLQuNGPIOKEltCh0KQvMTI0LTQzMjgg0L7RgiAyOS4wOC4yMDIyDE1D0LXRgNGC0LjRhNC40LrQsNGCINGB0L7QvtGC0LLQtdGC0YHRgtCy0LjRjyDihJbQodCkLzEyOC00NjM5INC-0YIgMDQuMTAuMjAyMzBmBgNVHR8EXzBdMC6gLKAqhihodHRwOi8vY3JsLnJvc2them5hLnJ1L2NybC91Y2ZrXzIwMjQuY3JsMCugKaAnhiVodHRwOi8vY3JsLmZrLmxvY2FsL2NybC91Y2ZrXzIwMjQuY3JsMHcGCCsGAQUFBwEBBGswaTA0BggrBgEFBQcwAoYoaHR0cDovL2NybC5yb3NrYXpuYS5ydS9jcmwvdWNma18yMDI0LmNydDAxBggrBgEFBQcwAoYlaHR0cDovL2NybC5may5sb2NhbC9jcmwvdWNma18yMDI0LmNydDAdBgNVHQ4EFgQUHpmFbGT-Z7mBm0OSmgon7jPgzs0wggF2BgNVHSMEggFtMIIBaYAUBmQTp87gg-KmfZ-Jp9ZWGZhM2aehggFDpIIBPzCCATsxITAfBgkqhkiG9w0BCQEWEmRpdEBkaWdpdGFsLmdvdi5ydTELMAkGA1UEBhMCUlUxGDAWBgNVBAgMDzc3INCc0L7RgdC60LLQsDEZMBcGA1UEBwwQ0LMuINCc0L7RgdC60LLQsDFTMFEGA1UECQxK0J_RgNC10YHQvdC10L3RgdC60LDRjyDQvdCw0LHQtdGA0LXQttC90LDRjywg0LTQvtC8IDEwLCDRgdGC0YDQvtC10L3QuNC1IDIxJjAkBgNVBAoMHdCc0LjQvdGG0LjRhNGA0Ysg0KDQvtGB0YHQuNC4MRgwFgYFKoUDZAESDTEwNDc3MDIwMjY3MDExFTATBgUqhQNkBBIKNzcxMDQ3NDM3NTEmMCQGA1UEAwwd0JzQuNC90YbQuNGE0YDRiyDQoNC-0YHRgdC40LiCCmwJwHYAAAAACYwwCgYIKoUDBwEBAwIDQQAvqmRe2MK9ALBRo97pb3f67iP8ek3WGUfv91pT-c3lVvMWTRn-MQbeKtAmsJQ0wmOGPjsEgjLtd8JMUJUJDI3RMYIEGzCCBBcCAQEwggF3MIIBYTEgMB4GCSqGSIb3DQEJARYRdWNfZmtAcm9za2F6bmEucnUxGDAWBgNVBAgMDzc3INCc0L7RgdC60LLQsDEVMBMGBSqFA2QEEgo3NzEwNTY4NzYwMRgwFgYFKoUDZAESDTEwNDc3OTcwMTk4MzAxYDBeBgNVBAkMV9CR0L7Qu9GM0YjQvtC5INCX0LvQsNGC0L7Rg9GB0YLQuNC90YHQutC40Lkg0L_QtdGA0LXRg9C70L7Quiwg0LQuIDYsINGB0YLRgNC-0LXQvdC40LUgMTEZMBcGA1UEBwwQ0LMuINCc0L7RgdC60LLQsDELMAkGA1UEBhMCUlUxLjAsBgNVBAoMJdCa0LDQt9C90LDRh9C10LnRgdGC0LLQviDQoNC-0YHRgdC40LgxODA2BgNVBAMML9Ck0LXQtNC10YDQsNC70YzQvdC-0LUg0LrQsNC30L3QsNGH0LXQudGB0YLQstC-AhBb1iQ06OYU7S_nbUvQhesTMAoGCCqFAwcBAQICoIICOzAYBgkqhkiG9w0BCQMxCwYJKoZIhvcNAQcBMBwGCSqGSIb3DQEJBTEPFw0yNTA4MjAxMjEyNTFaMC8GCSqGSIb3DQEJBDEiBCBvS9MhpS8A7-f05OFc0DENfstByjBIqlWV4nmcdH2IfzCCAc4GCyqGSIb3DQEJEAIvMYIBvTCCAbkwggG1MIIBsTAKBggqhQMHAQECAgQglqo-0XHSoqxmai7UR7xMrVhgEYj_TrAx5PC-PyKeWEEwggF_MIIBaaSCAWUwggFhMSAwHgYJKoZIhvcNAQkBFhF1Y19ma0Byb3NrYXpuYS5ydTEYMBYGA1UECAwPNzcg0JzQvtGB0LrQstCwMRUwEwYFKoUDZAQSCjc3MTA1Njg3NjAxGDAWBgUqhQNkARINMTA0Nzc5NzAxOTgzMDFgMF4GA1UECQxX0JHQvtC70YzRiNC-0Lkg0JfQu9Cw0YLQvtGD0YHRgtC40L3RgdC60LjQuSDQv9C10YDQtdGD0LvQvtC6LCDQtC4gNiwg0YHRgtGA0L7QtdC90LjQtSAxMRkwFwYDVQQHDBDQsy4g0JzQvtGB0LrQstCwMQswCQYDVQQGEwJSVTEuMCwGA1UECgwl0JrQsNC30L3QsNGH0LXQudGB0YLQstC-INCg0L7RgdGB0LjQuDE4MDYGA1UEAwwv0KTQtdC00LXRgNCw0LvRjNC90L7QtSDQutCw0LfQvdCw0YfQtdC50YHRgtCy0L4CEFvWJDTo5hTtL-dtS9CF6xMwCgYIKoUDBwEBAQEEQOaqaTaJbqbwv917bz2BbcfUL1mEjDZln5gW42St6w2y3UKS8tI4V3G_MlOlwTRSzel4SjuRlZIGdBoCispnhJg%3D'
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
    # status, result = smart_http_request(s, url=url, method='post', data=payload, headers=headers)
    response = s.post(url, data=payload, headers=headers, verify=False)
    if response.status_code == 200:
        result = json.loads(response.text)
        print('Token refreshed successfully!')
        print(result)
        pass
        return result
    else:
        raise Exception(f"Не удалось обновить токен. Результат запроса: {result.content}")
        print(f"Не удалось обновить токен. Результат запроса: {result.content}")
        return None
    # pass
    # if status == 200:
    #     # return result.json()
    #     decoded = result.content.decode('cp1251')
    #     pass
    # return None


def download_nspd_layer(
    nspd_layer='36281', layer_alias='result',
    tiles_gpkg='tiles.gpkg', tiles_layer='khmao',
    width=512, height=512, i_from=0, i_to=512,
    j_from=0, j_to=512, pixel_step=3,
    cookie='',
    access_token='',
    refresh_token='',
    auth_access_token_expires=''
):
    auth_access_token_expires = utils.unquote(auth_access_token_expires).replace('"', '')
    auth_access_token_expires_dt = datetime.strptime(auth_access_token_expires, '%Y-%m-%dT%H:%M:%S.%fZ')
    utc_tz = pytz.timezone('utc')
    auth_access_token_expires_dt = utc_tz.localize(auth_access_token_expires_dt)
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
                        'Authorization': f"Bearer {access_token}"
                        # "cookie": cookie
                        }
                params["BBOX"] = f"{xmin},{ymin},{xmax},{ymax}"
                for i in range(i_from, i_to + 1, pixel_step):
                    params["I"] = str(i)
                    for j in range(j_from, j_to + 1, pixel_step):
                        params["J"] = str(j)
                        # %222025-08-22T11%3A34%3A47.750Z%22
                        # auth_access_token_expires = utils.unquote(auth_access_token_expires).replace('"', '')
                        # auth_access_token_expires_dt = datetime.strptime(auth_access_token_expires, '%Y-%m-%dT%H:%M:%S.%fZ')
                        cur_datetime_utc = datetime.now(timezone.utc)
                        pass
                        if auth_access_token_expires_dt <= cur_datetime_utc - timedelta(seconds=10):
                            refreshed_auth = request_refresh_token(s, refresh_token)
                            auth_access_token_expires_dt = cur_datetime_utc + timedelta(seconds=int(refreshed_auth.get('expires_in')))
                            access_token = refreshed_auth.get('access_token')
                            refresh_token = refreshed_auth.get('refresh_token')
                        pass
                        headers['Authorization'] = f"Bearer {access_token}"
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
    # и скопировать значение access_token, refresh_token и auth_access_token_expires из cookie любого запроса GetMap.
    # После этого оставить страницу висеть. (?)
    
    # ЗАМЕНИТЬ!!!
    access_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiIwMzM4NmRiZS01MTg1LTRiOTYtOTAwZC1jMmIxYmIzNjhlZDYiLCJjbGllbnRfaWQiOiIwMzM4NmRiZS01MTg1LTRiOTYtOTAwZC1jMmIxYmIzNjhlZDYiLCJkaXNwbGF5X25hbWUiOiLQntGB0L7QutC40L0g0KHRgtC10L_QsNC9INCQ0YDRgtC10LzQvtCy0LjRhyIsImVtYWlsIjoic3RlcGFub3Nva2luQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU1ODY3MTA3LCJleHBpcmVzX2luIjoxODAwLCJmYW1pbHlfbmFtZSI6ItCe0YHQvtC60LjQvSIsImdpdmVuX25hbWUiOiLQodGC0LXQv9Cw0L0iLCJpYXQiOjE3NTU4NjUzMDcsImlzcyI6Imh0dHBzOi8vc3NvLm5zcGQuZ292LnJ1IiwianRpIjoiNmViNTZiZTQtOWU4YS00MGRjLTlkOTYtMTBiN2ZhYmUxM2QzIiwibG9jYWxlIjoiZW4iLCJtaWRkbGVfbmFtZSI6ItCQ0YDRgtC10LzQvtCy0LjRhyIsIm5hbWUiOiLQntGB0L7QutC40L0g0KHRgtC10L_QsNC9INCQ0YDRgtC10LzQvtCy0LjRhyIsInByZWZlcnJlZF91c2VybmFtZSI6InAtMTIxLTI5OS02MTcgNTEiLCJzY29wZSI6InByb2ZpbGUgZW1haWwgdWlkIiwic2lkIjoiZjdjOTc4MTAtMmYwNS00ODFlLWFkNTgtY2U3ODAxZWRiMDhlIiwic3ViIjoiMjQxNWUzM2ItZmU4OC00Y2IzLWE4ZTctNDIyNjQyOTU0OGE5IiwidWlkIjoiMjQxNWUzM2ItZmU4OC00Y2IzLWE4ZTctNDIyNjQyOTU0OGE5IiwidXBkYXRlZF9hdCI6MTc1NTg2NTMwNn0.RB8pzDQaaHxKhdKA3fswN9FYSZwZA2iBYmI1r3C0fT8w590U7GekEk4RXuFOkLz-gCAoP6BxiOeWipvhdAUbOzQ3-MhwgG359sf_2_qHAKUPjf8P0puq0J2tCx8DzpwIKiWCIE0Q8FmP66nUYVyeCgKhUZPLAoZGBfMj8pBvOG5A_FLy_nHsTIu0aFSt8eMCsgc2gAL0mFx1a-15nU0rqNfN_WFHzHfWP5-gN8V8KRo4EtHSP9MadRwPxDJBaOKe0OgG9qPascEcsHJdj-fhIFt_s45RMoCQJJZvuNMXhcvCL5CvC3JMX3_dfO9XT03kK7u8PVqx_XB159q8x4ZRkfdHDNt-lOcXVY9xH8uBsNF8LsBV6EXn1xNk1-_a2eCQzaTUbVpRjHb5O0O4vObFqhIF2BMZkpxLBc0biHMfIRc1l3_3JKiVS-mDLDtM_pCHQsovszDbtLXPEYalQhGjwN7YtsWs6xOhQ62qy1ISKkredof99Oj5dNc8e8zd9qY_eziiwnpcOu8T-qEs1hwHMHqaCClgiSPTjzYCT21SmlId7Z-J7dILVvMaH-TFqsqtLPrK0l6k7eCpkHdZEOpzf7VNX-4ptXdJS5D6KgVd6yMXEfdaTQqHNWaZMWhGBradYLpmFYwVWHDX_FIXz2aWJlj71Ki2Ni1J1eJdfGUbEcM'
    auth_access_token_expires = '%222025-08-22T12%3A51%3A47.658Z%22'
    refresh_token = 'c7M5toCbi6Jso2Pii2GsuVnK1I5bRqWJ5cMx16Dr2HIvKP3KwxtHwV9ot6m2s6T1DZkZElI9kdHr6XXRfe'
    
    
    
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
                access_token=access_token,
                refresh_token=refresh_token,
                auth_access_token_expires=auth_access_token_expires
            )
    
    # # Это работает
    # with Session() as s:
    #     token_response = request_refresh_token(s, refresh_token=refresh_token)
    #     pass
    
    pass