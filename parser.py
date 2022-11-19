import requests
from settings import cookies, headers
import json

def get_id(category_id):
    params = {
        'categoryId': category_id,
        'offset': '0',
        'limit': '24',
        'filterParams': [
            'WyJza2lka2EiLCIiLCJkYSJd',
            'WyJ0b2xrby12LW5hbGljaGlpIiwiIiwiZGEiXQ==',
        ],
        'doTranslit': 'true',
    }

    response = requests.get('https://www.mvideo.ru/bff/products/listing', params=params, cookies=cookies,
                            headers=headers).json()
    pages = int(response['body']['total'])
    id_list = response['body']['products']
    for i in range(23, pages, 23):
        params['offset'] = i
        response = requests.get('https://www.mvideo.ru/bff/products/listing', params=params, cookies=cookies,
                                headers=headers).json()
        for j in (response['body']['products']):
            if j not in id_list:
                id_list.append(j)
    return id_list


def get_product_info(id_list):
    json_data = {
        'productIds': id_list[0:50],
        'mediaTypes': [
            'images',
        ],
        'category': True,
        'status': True,
        'brand': True,
        'propertyTypes': [
            'KEY',
        ],
        'propertiesConfig': {
            'propertiesPortionSize': 5,
        },
        'multioffer': False,
    }

    response = requests.post('https://www.mvideo.ru/bff/product-details/list', cookies=cookies, headers=headers,
                             json=json_data).json()
    result_list = response['body']['products']
    f = len(id_list)
    z = 50
    while f - z > 50:
        z += 50
        json_data['productIds'] = id_list[z - 50:z]
        response = requests.post('https://www.mvideo.ru/bff/product-details/list', cookies=cookies, headers=headers,
                                 json=json_data).json()
        for i in response['body']['products']:
            result_list.append(i)
    else:
        json_data['productIds'] = id_list[z:f]
        response = requests.post('https://www.mvideo.ru/bff/product-details/list', cookies=cookies, headers=headers,
                                 json=json_data).json()
        for i in response['body']['products']:
            result_list.append(i)
    result_info = {}
    for i in result_list:
        result_info[i["productId"]] = {
            'name': i['name'],
            "img_link": f"https://img.mvideo.ru/{i['images'][0]}",
            "link": f"https://www.mvideo.ru/products/{i['nameTranslit']}-{i['productId']}"
        }
    return result_info


def get_product_price(id_list):
    f = 0
    resul_price = {}
    for z in range(50, len(id_list), 50):
        params = {
            'productIds': ','.join(id_list[f:z]),
            'addBonusRubles': 'true',
            'isPromoApplied': 'true',
        }
        response = requests.get('https://www.mvideo.ru/bff/products/prices', params=params, cookies=cookies,
                                headers=headers).json()
        f = z
        for i in response["body"]['materialPrices']:
            resul_price[i['productId']] = {
                "price": i["price"]["basePrice"],
                "salePrice": i["price"]["salePrice"],
                "discount": i["price"]["discounts"][0]['discount'],
                "discount_in_pr": round(
                    int(i["price"]["discounts"][0]['discount']) / int(i["price"]["basePrice"]) * 100, 2)
            }
    if len(id_list) - f > 0:
        params = {
            'productIds': ','.join(id_list[f:len(id_list)]),
            'addBonusRubles': 'true',
            'isPromoApplied': 'true',
        }
        response = requests.get('https://www.mvideo.ru/bff/products/prices', params=params, cookies=cookies,
                                headers=headers).json()
        for i in response["body"]['materialPrices']:
            resul_price[i['productId']] = {
                "price": i["price"]["basePrice"],
                "salePrice": i["price"]["salePrice"],
                "discount": i["price"]["discounts"][0]['discount'],
                "discount_in_pr": round(
                    int(i["price"]["discounts"][0]['discount']) / int(i["price"]["basePrice"]) * 100, 2)
            }

    return resul_price


def get_together(result_info, resul_price):
    count = 0
    for i in result_info:
        try:
            result_info[i].update(resul_price[i])
        except:
            count += 1
    with open("result.json", "w", encoding="utf8") as file:
        json.dump(result_info, file, indent=4, ensure_ascii=False)

