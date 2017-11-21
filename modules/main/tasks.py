# coding=utf-8
import copy
import json
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.timezone import now

from app_celery import app
from common.diff import DiffByTypesDict
from common.get_data import parse_site_data
from common.helpers import system_notification
from main.models import ParseResultLog, Product, Brand, Price

log = logging.getLogger(__name__)


@app.task(name="global_sync")
def global_sync():
    last_parse_result = ParseResultLog.objects.last()
    _grab_allowed, _message = True, ''
    if last_parse_result:
        _grab_allowed, _message = last_parse_result.grab_allowed
    if not _grab_allowed:
        system_notification('Парсинг не запущен, так как ' + _message)
        return
    log.info('Start parsing...')
    (parse_and_generation.si() | sync_product_and_prices.si()).apply()


@app.task(name="parse_and_generation")
def parse_and_generation():
    # создаем объект парс-лога
    parse = ParseResultLog.objects.create()
    # получаем данные с сайта и обновляем запись в базе
    parse.received_data = parse_site_data()
    parse.finish_time = now()
    parse.save()


@app.task(name="sync_product_and_prices")
def sync_product_and_prices():
    """ На основе полученный от парсинга данных - создаем или обновляем
        объекты в базе
    """

    diff_dict = {}

    # получаем из базы результат последнего парсинга
    last_parse_log = ParseResultLog.objects.last()
    if not getattr(last_parse_log, 'received_data', None):
        system_notification(
            'Обновление данных не запущено, так как парсинг не дал результатов'
        )
        return
    parse_data = last_parse_log.received_data

    # идем по пунктам (линзы|капли|растворы|аксессуары)
    for product_type, parsed_brands_dict in parse_data.items():
        # для каждого перебираем итемы (бренды)

        if product_type in Product.PRODUCT_TYPES_BY_BRANDS:
            # обрабатываем набор товаров по брендно

            diff_dict['brands'] = sync_brands(parsed_brands_dict)

            # для каждого бренда формируем набор товаров
            parsed_product_items = {}
            brands_ids_dict = dict(Brand.objects.filter(
                remote_id__in=parsed_brands_dict.keys()
            ).values_list('remote_id', 'id'))

            # создаем единый словарь товаров по всем брендам
            for brand_info in parsed_brands_dict.values():
                for product_info in brand_info['items'].values():
                    product_info['brand_id'] = \
                        brands_ids_dict.get(brand_info['remote_id'])
                parsed_product_items.update(brand_info['items'])
        else:
            # иначе. если простой набор товаров - проходим по всем товарам
            parsed_product_items = parsed_brands_dict

        if not parsed_product_items:
            continue

        # опередяем - какие надо добавить | удалить | обновить (ключ - id)
        diff_products, diff_prices = \
            sync_products(parsed_product_items, product_type)

        diff_dict[product_type] = {'products': diff_products,
                                   'prices': diff_prices}
        del diff_products
        del diff_prices

    last_parse_log.changes = diff_dict
    last_parse_log.save()
    send_notification.apply_async(args=[diff_dict])


@transaction.atomic
def sync_products(parsed_product_items, product_type):
    """Синхронизация Товаров (линзы, капли, растворы)

    :param product_type: тип товара: линзы|капли|расстворы|аксессуары
    :param parsed_product_items: спарсеный список из словарей с товарамми
    :return: словарь изменений: добавленые,изменные,удаленные товары

    """
    if not parsed_product_items:
        message = 'Products list [{}] from parsing is empty!!! skip product ' \
                  'parsing'.format(product_type)
        log.error(message)
        system_notification(message)
        return {}

    diff_products = {'new': [], 'updated': [], 'removed': []}
    diff_prices = []

    parsed_product_ids = set(parsed_product_items.keys())
    exists_product_ids = set(
        Product.objects.filter(
            type=product_type).values_list('remote_id', flat=True)
    )
    new_product_ids = parsed_product_ids - exists_product_ids
    old_product_ids = exists_product_ids - parsed_product_ids
    update_product_ids = exists_product_ids & parsed_product_ids

    # создаем новые товары
    products = []
    for remote_pid in new_product_ids:
        products.append(Product(
            name=parsed_product_items[remote_pid]['name'],
            type=product_type,
            brand_id=parsed_product_items[remote_pid].get('brand_id', None),
            url=parsed_product_items[remote_pid]['url'],
            remote_id=parsed_product_items[remote_pid]['remote_id'],
            has_action=parsed_product_items[remote_pid].get('has_action', False)
        ))
        diff_products['new'].append(parsed_product_items[remote_pid]['name'])

    Product.objects.bulk_create(products)

    # удаляем отсутствующие
    products_to_remove = Product.objects.filter(remote_id__in=old_product_ids)
    diff_products['removed'].extend(
        products_to_remove.values_list('name', flat=True)
    )
    products_to_remove.delete()

    # Обновляем имеющиеся
    for stored_product_dict in Product.objects.filter(
        remote_id__in=update_product_ids, type=product_type
    ).values('url', 'name', 'brand_id', 'remote_id', 'has_action'):
        parsed_product_dict = copy.deepcopy(
            parsed_product_items[stored_product_dict['remote_id']])

        parsed_product_dict.setdefault('has_action', False)
        parsed_product_dict.setdefault('brand_id', None)
        del parsed_product_dict['prices']

        if stored_product_dict != parsed_product_dict:
            Product.objects.filter(
                remote_id=parsed_product_dict['remote_id'], type=product_type
            ).update(**parsed_product_dict)
            diff_products['updated'].append(parsed_product_dict['name'])

    # делаем выборку текущих сохраненных цен
    stored_prices_dict = dict(
        Product.objects.filter(
            type=product_type, current_price__isnull=False
        ).values_list('remote_id', 'current_price__value'))

    # и актуализируем те которые изменились
    for remote_pid, price_value in stored_prices_dict.items():
        parsed_price = parsed_product_items.get(
            remote_pid, {}).get('prices', [])
        price_value = json.loads(price_value)
        if parsed_price and price_value != parsed_price:
            product = Product.objects.get(type=product_type,
                                          remote_id=remote_pid)
            price = Price.objects.create(
                value=parsed_price, product=product
            )
            product.current_price = price
            product.save(update_fields=['current_price'])
            diff_prices.append({'product_id': product.id,
                                'product_name': product.name,
                                'new_value': parsed_price})

    # ищем товары для которых не проставлена текущая цена
    without_price_products = Product.objects.filter(
        current_price__isnull=True
    )
    for product in without_price_products:
        parsed_price = parsed_product_items.get(
            product.remote_id, {}).get('prices', [])
        price = Price.objects.create(value=parsed_price, product=product)
        product.current_price = price
        product.save(update_fields=['current_price'])

        diff_prices.append({'product_id': product.id,
                            'product_name': product.name,
                            'new_value': parsed_price})

    return diff_products, diff_prices


@transaction.atomic
def sync_brands(parsed_brands_dict):
    """Синхронизация брендов

    :param parsed_brands_dict: спарсеный словарь с брендами
    :return: словарь изменений: добавленые,изменные,удаленные бренды

    """
    if not parsed_brands_dict:
        log.error('Brands dict from parsing is empty!!! skip parsing')
        system_notification(
            'Brands dict from parsing is empty!!! skip parsing'
        )
        return {}

    diff_dict = {'new': [], 'removed': [], 'updated': []}

    # определяем какие бренды надо добавить | удалить | обновить
    exists_brand_ids = set(
        Brand.objects.all().values_list('remote_id', flat=True)
    )
    parsed_brand_ids = set(parsed_brands_dict.keys())
    new_brand_ids = parsed_brand_ids - exists_brand_ids
    old_brand_ids = exists_brand_ids - parsed_brand_ids
    update_brand_ids = parsed_brand_ids & exists_brand_ids

    # добавляем новые бренды:
    brands = []
    for brand_id in new_brand_ids:
        brand_info = parsed_brands_dict[brand_id]
        brands.append(Brand(
            name=brand_info['name'], url=brand_info['url'],
            remote_id=brand_id
        ))
        diff_dict['new'].append(brand_info)

    Brand.objects.bulk_create(brands)

    # удаляем старые
    brands_to_remove = Brand.objects.filter(remote_id__in=old_brand_ids)
    diff_dict['removed'] = \
        list(brands_to_remove.values_list('name', flat=True))
    brands_to_remove.delete()

    # обновляем существующие
    for stored_brand_dict in Brand.objects.filter(
            remote_id__in=update_brand_ids).values('url', 'name', 'remote_id'):
        parsed_brand_dict = copy.deepcopy(
            parsed_brands_dict[stored_brand_dict['remote_id']]
        )
        del parsed_brand_dict['items']
        if stored_brand_dict != parsed_brand_dict:
            Brand.objects.filter(
                remote_id=parsed_brand_dict['remote_id']
            ).update(**parsed_brand_dict)
            diff_dict['updated'].append(parsed_brand_dict['name'])

    return diff_dict


@app.task(name="send_notification")
def send_notification(diff_dict=None):
    """ Email нотификация после завершения парсинга и синхронизаций """

    try:
        diff_dict = diff_dict or ParseResultLog.objects.last().changes
    except ParseResultLog.DoesNotExist:
        log.error('Parse result does not exists')
        return

    if not diff_dict:
        log.warning('send notification was skip')
        return

    diff_by_types = DiffByTypesDict(**diff_dict)
    subject = 'Изменения на сайте lenses'
    text_message = ''
    html_message = render_to_string(
        'email_notification/base.html', {'diff': diff_by_types}
    )

    send_mail(
        subject, text_message,
        settings.DEFAULT_FROM_EMAIL,
        settings.MANAGERS,
        html_message=html_message
    )
    log.info('email was sent')
