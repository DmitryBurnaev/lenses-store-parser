# coding=utf-8
import random
import logging
import re
import time as system_time

from urllib.request import urlopen
from urllib.parse import urljoin

from lxml.html import fromstring

log = logging.getLogger(__name__)


RAND_TIME = 5

BASE_URL = 'http://lensgo.ru'
CATALOG_URL = 'http://lensgo.ru/catalog/'
LENSES_URL = 'http://lensgo.ru/catalog/lenses'
SOLUTIONS_URL = 'http://lensgo.ru/catalog/solutions'
ACCESSORIES_URL = 'http://lensgo.ru/catalog/accessories'
DROPS_URL = 'http://lensgo.ru/catalog/drops'

LENSES_BRAND_ITEM_SELECTOR = '.brend_table a.user_brand'
LENSES_CATALOG_MENU_ITEMS = '.left_menu ul > li:first-child ul li'
LENSES_BRAND_ITEMS = '.tovar_block_01'


def parse_site_data():
    """ Выполняет простой обход по страницам сайта и коллектит информацию в
    словарь
    :return: словарь с полученными данными

    """
    result = {
        'lenses': {},
        'solutions': {},
        'accessories': {},
        'drops': {}
    }

    try:
        f = urlopen(CATALOG_URL)
    except Exception as error:
        log.error('Error parsing of {}: {}'.format(CATALOG_URL, error))
        return result

    list_html = f.read().decode('utf-8')
    list_doc = fromstring(list_html)

    # parse lenses
    for catalog_item in list_doc.cssselect(LENSES_BRAND_ITEM_SELECTOR):
        a = catalog_item.cssselect('a')[0]
        url = a.get('href')
        try:
            brand_id = re \
                .search(r'brands=(?P<brand_id>\d{3,7})', url)\
                .group('brand_id')
        except AttributeError:
            log.error('href {} does not contains brand_id'.format(url))
            continue

        brand_info = {
            'remote_id': brand_id,
            'name': a.text,
            'url': url,
        }
        if 'http' not in brand_info['url'] \
                or 'lenses' not in brand_info['url']:
            continue

        # заходим в каждый бренд и забираем ссылки на товары и инф об акциях
        brand_info['items'] = parse_catalog(brand_info['url'])
        result['lenses'][brand_id] = brand_info

    # parse solutions
    result['solutions'] = parse_catalog(SOLUTIONS_URL)
    # parse accessories
    result['accessories'] = parse_catalog(ACCESSORIES_URL)
    # parse drops
    result['drops'] = parse_catalog(DROPS_URL)

    return result


def parse_catalog(catalog_url):
    """ парсим отдельно каталог по указанному урлу
        (растворы, капли, аксессуары)

    :param catalog_url: урл для парсинга
    :return: словарь с изменениями (ключ - артикул товара)
    """

    log.info('Parse catalog {} ...'.format(catalog_url))
    result_items = {}
    system_time.sleep(random.randint(1, RAND_TIME))

    try:
        items_html = urlopen(catalog_url).read().decode('utf-8')
    except Exception as error:
        log.error('Error parsing of {}: {}'.format(catalog_url, error))
        return result_items

    items_doc = fromstring(items_html)
    catalog_items = items_doc.cssselect(LENSES_BRAND_ITEMS)
    log.info('[{} items]'.format(len(catalog_items)))

    for i, catalog_item in enumerate(catalog_items):
        try:
            item_a = catalog_item.cssselect('.td_3 a')[0]
        except IndexError:
            continue

        item_href = item_a.get('href')
        item_id = item_href.rpartition('/')[2]
        item_info = {
            'remote_id': item_id,
            'url': urljoin(BASE_URL, item_href),
            'name': item_a.text_content(),
            'prices': []
        }

        # check item on has_action
        try:
            catalog_item.cssselect('.td_1 img.akcii')[0]
        except IndexError:
            pass
        else:
            item_info['has_action'] = True

        system_time.sleep(random.randint(1, RAND_TIME))

        try:
            item_html = urlopen(item_info['url']).read().decode('utf-8')
        except Exception as error:
            log.error('Error parsing of {} (pass this): {}'.format(
                item_info['url'], error
            ))
            continue

        item_doc = fromstring(item_html)
        # 1st string - head of table
        price_table = item_doc.cssselect('.big_tovar_upakovka table tr')[1:]

        for price_tr in price_table:
            try:
                price_category, price_value = price_tr.cssselect('td')
                item_info['prices'].append(
                    (price_category.text_content(), price_value.text_content())
                )
            except (AttributeError, ValueError) as err:
                log.error('Price TR isn`t valid: {}'.format(item_info['name']))

        result_items[item_id] = item_info

    log.info('----- Catalog parse finish. -----')
    return result_items
