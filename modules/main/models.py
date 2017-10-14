# -*- coding: utf-8 -*-
from collections import OrderedDict

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from jsonfield import JSONField

from common.diff import DiffByTypesDict


class BaseModel(models.Model):
    """ Базовый набор атрибутов для моделей """

    date_created = models.DateTimeField('Дата создания', auto_now_add=True)
    date_updated = models.DateTimeField('Дата обночления', auto_now=True)
    
    class Meta:
        abstract = True


class ParseResultQS(models.QuerySet):
    """ Вспомогательные методы для получения рейтинга товара """

    def available(self):
        """
        Выбирает те записи, в которых есть данные для отображения
        """

        return self.filter(received_data__isnull=False).exclude(
            received_data={})


class ParseResultLog(BaseModel):
    """ Сразу после парса результат сторится в этой модели - для дальнейшего
    анализа

    """

    received_data = JSONField('Полученные данные', null=True, blank=True)
    changes = JSONField('Внесенные изменения', null=True, blank=True)
    finish_time = models.DateTimeField('Время окончания парсинга', null=True,
                                       blank=True, default=None)
    objects = ParseResultQS.as_manager()

    def __str__(self):
        return 'Парсинг от {}'.format(
            timezone.localtime(self.date_created).strftime('%d.%m.%Y %H:%M')
        )

    class Meta:
        verbose_name = 'Результат парсинга'
        verbose_name_plural = 'Результаты парсинга'

    @property
    def stat_info(self):
        """ Рассчитывает статистику по результатам парсинга
        :return: словарь вида {
            'lenses': {'parsed': 250, 'new':12, 'updated':4, 'removed':3},
            ...
        }
        """
        result = OrderedDict()
        changes_dict = self.changes or {}
        if not self.received_data:
            return result
        for product_type, product_dict in self.received_data.items():
            product_changes = changes_dict.get(product_type)
            if not product_changes:
                continue
            count_elements = sum(map(
                lambda x: len(x[1].get('items', [0])), product_dict.items()
            ))
            result[product_type] = {'parsed': count_elements}
            for _type in ['new', 'updated', 'removed']:
                result[product_type][_type] = len(
                    changes_dict[product_type]['products'][_type]
                )
            result[product_type]['update_prices'] = len(
                changes_dict[product_type]['prices']
            )
        return result

    @property
    def grab_allowed(self):
        """ Определяет можно ли запускать новый таск
        :return: True|False, <сообщение>
        """

        if not self.finish_time:
            return False, 'не завершен предыдущий парсинг "{}"'.format(self)

        last_time = now() - self.finish_time
        if last_time.seconds < settings.ALLOWED_PARSE_TIMEDELTA:
            return False, 'не прошло еще указанное время от "{}"'.format(self)

        return True, ''

    @property
    def in_progress(self):
        return not bool(self.finish_time)

    @property
    def diff(self):
        return DiffByTypesDict(**self.changes)


class Brand(BaseModel):
    """ Бренды """

    name = models.CharField('Наименование', max_length=256)
    url = models.URLField('Урл на сайте', blank=True, default='')
    remote_id = models.CharField('ID на сайте', max_length=7, default='0')

    def __str__(self):
        return self.name

    class Meta(object):
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'


class Product(BaseModel):
    """ Товарная позиция """

    TYPE_CHOICES = (
        ('lenses', 'Линзы'),
        ('solutions', 'Растворы'),
        ('drops', 'Капли'),
        ('accessories', 'Аксессуары'),
    )
    PRODUCT_TYPES_BY_BRANDS = ('lenses',)
    SIMPLE_PRODUCT_TYPES = ('solutions', 'drops', 'accessories')

    name = models.CharField('Название товара', max_length=256)
    type = models.CharField('Тип', choices=TYPE_CHOICES, max_length=64)
    brand = models.ForeignKey('Brand', related_name='products', null=True,
                              blank=True, default=None)
    url = models.URLField('Урл на сайте', blank=True, default='')
    remote_id = models.CharField('ID на сайте', max_length=7, default='0')

    current_price = models.OneToOneField('Price', verbose_name='Текущая цена',
                                         related_name='price', null=True,
                                         blank=True)
    has_action = models.BooleanField('Акционный', default=False)

    def __str__(self):
        return self.name

    class Meta(object):
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Price(BaseModel):
    """ История цен """

    value = JSONField(verbose_name='Значение')
    product = models.ForeignKey('Product', related_name='history_prices')

    def __str__(self):
        return '{} = {}'.format(self.product.name, self.value)

    class Meta(object):
        verbose_name = 'Цена за товар'
        verbose_name_plural = 'Цены за товар'
        ordering = ('-date_created',)


class ProfileCustomization(BaseModel):
    """ Дополнительная натройка профиля пользователя """

    TEMPLATE_SIMPLE = 'simple'
    TEMPLATE_MATERIAL = 'materialize'

    TEMPLATE_CHOICES = (
        ('simple', 'Стандартный шаблон'),
        ('materialize', 'Материал дизайн')
    )

    template = models.CharField('Шаблон', max_length=28,
                                default=TEMPLATE_SIMPLE,
                                choices=TEMPLATE_CHOICES)
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='customize')

    def __str__(self):
        return '[{}] Кастомизация для пользователя {}'.format(
            self.id or '-', self.user
        )

    class Meta(object):
        verbose_name = 'Кастомизация для пользователя'
        verbose_name_plural = 'Кастомизация для пользователя'
