
class DiffDict(dict):
    """ Класс для хранения различий при сихронизации.
    удобен для быстрого определения наличия данных в словаре и подсловарях

    """

    def __init__(self, *args, **kwargs):
        super(DiffDict, self).__init__(*args, **kwargs)
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = DiffDict(value)

    def check_items(self, check_item_value, result=False):
        """
            Метод рекурсивно проверяет содержимое словаря с подсловарями
            для опрпеделения наличия данных
        """

        if isinstance(check_item_value, dict):
            for item_key, item_value in check_item_value.items():
                result |= self.check_items(item_value, result)
        elif isinstance(check_item_value, (list, tuple)):
            for sub_item in check_item_value:
                result |= self.check_items(sub_item, result)
        else:
            result |= bool(check_item_value)

        return result

    @property
    def has_content(self):
        return self.check_items(self)

    def __bool__(self):
        return self.has_content


class DiffByTypesDict(DiffDict):
    """ Класс для детализации диффов по типам товаров
    ( с быстрым доступом к каждому типу)

    """
    PRODUCT_TYPES_MAPPING = {
        'lenses': 'Линзы',
        'drops': 'Капли',
        'solutions': 'Растворы',
        'accessories': 'Аксессуары',
    }

    def get_by_key(self, key):
        res = self.get(key, [])
        if isinstance(res, dict):
            return DiffByTypesDict(**res)
        return res

    def _get_field(self, key):
        return self.PRODUCT_TYPES_MAPPING[key], self.get_by_key(key)

    @property
    def products_changed(self):
        return any([self.get_by_key(key).has_content
                    for key in self.PRODUCT_TYPES_MAPPING.keys()])

    @property
    def brands(self):
        return self._get_field('brands')

    @property
    def lenses(self):
        return self._get_field('lenses')

    @property
    def drops(self):
        return self._get_field('drops')

    @property
    def solutions(self):
        return self._get_field('solutions')

    @property
    def accessories(self):
        return self._get_field('accessories')
