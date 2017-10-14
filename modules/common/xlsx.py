# -*- coding: utf-8 -*-
import os
import logging

from xlsxwriter import Workbook
from datetime import datetime
from django.conf import settings

from operator import itemgetter

log = logging.getLogger(__name__)


def write_xlsx(data):
    folder = settings.GENERATED_FILE_ROOT
    file_name = '{}.xlsx'.format(datetime.now().strftime('%d%m%Y_%H%M%S'))
    UploadXlsx(data, filename=os.path.join(folder, file_name)).get_workbook()
    return file_name


class UploadXlsx(object):
    """ Формирует на выходе объект xlsx-книги для записи в файл или отдачи в
    респонс
    """
    _worksheet = None
    _workbook = None
    _uploaded_data = None
    _current_string_number = 0

    # поля
    _field_names = ('Артикул', 'Название', 'Участие в акции', 'Цены')

    # форматы отображения
    _default_format = None
    _data_format = None
    _merge_format = None
    _merge_format_2 = None
    _caption_format = None

    def __init__(self, uploaded_data, filename=None, response=None):
        """
        Формирует объект для выгрузки в файл

        :param response: респонс (если отдаем на скачивание)
        :param filename: имя файла (если пишем в ФС)
        :param uploaded_data: данные для выгрузки
        """

        if filename is not None:
            self._workbook = Workbook(filename)
        elif response is not None:
            self._workbook = Workbook(response, {'in_memory': True})
        else:
            raise RuntimeError('work book must be save to file or response')
        self._worksheet = self._workbook.add_worksheet('Получено с сайта')
        self._uploaded_data = uploaded_data
        self._init_formats()

    @staticmethod
    def _action_label(item):
        return '*' if item.get('has_action') else ''

    def _init_formats(self):
        self._merge_format = self._workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'yellow'})
        self._merge_format_2 = self._workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
        })
        self._data_format = self._workbook.add_format({'valign': 'vcenter'})
        self._data_format.set_text_wrap()

        self._default_format = self._workbook.add_format({'valign': 'vcenter'})
        self._default_format.set_text_wrap()
        self._caption_format = self._workbook.add_format(
            {'bold': True, 'italic': True}
        )

    def get_workbook(self):
        """ Формирует на выходе объект xlsx-книги
        :return: объект <xlsxwriter.Workbook>

        """
        log.info('Writing workbook ....')

        self._worksheet.set_column('B:D', 12)
        self._worksheet.set_row(0, 30)

        self._worksheet.set_column(0, 0, width=10)
        self._worksheet.set_column(1, 1, width=40)
        self._worksheet.set_column(2, 2, width=20)
        self._worksheet.set_column(3, 10, width=17)

        self._current_string_number = 0

        # Merge 3 cells.
        self._current_string_number += 1

        # lenses
        self._worksheet.merge_range(
            'A{0}:D{0}'.format(self._current_string_number),
            'Линзы', self._merge_format
        )
        self._current_string_number += 1
        brand_items = sorted(self._uploaded_data['lenses'].values(),
                             key=itemgetter('name'))

        for brand_info in brand_items:
            if not brand_info['items']:
                continue
            self._current_string_number += 2
            self._worksheet.set_row(self._current_string_number - 1, 30)
            self._worksheet.merge_range(
                'A{0}:D{0}'.format(self._current_string_number),
                brand_info['name'], self._merge_format_2
            )
            self._current_string_number += 1
            for col_number, field in enumerate(self._field_names):
                self._worksheet.write(
                    self._current_string_number, col_number, field,
                    self._caption_format
                )
            self._current_string_number += 2
            self._write_catalog_items(
                brand_info['items'], self._data_format, self._default_format
            )

        self._write_section('solutions', 'Растворы')
        self._write_section('accessories', 'Аксессуары')
        self._write_section('drops', 'Капли')

        self._workbook.close()

        log.info('Workbook created ....')
        return self._workbook

    def _write_section(self, products_type, section_title):
        self._current_string_number += 4
        self._worksheet.set_row(self._current_string_number - 1, 30)
        self._worksheet.merge_range(
            'A{0}:D{0}'.format(self._current_string_number),
            section_title, self._merge_format
        )
        self._current_string_number += 1
        for col_number, field in enumerate(self._field_names):
            self._worksheet.write(self._current_string_number, col_number,
                                  field, self._caption_format)
        self._current_string_number += 2
        self._write_catalog_items(
            self._uploaded_data[products_type], self._data_format,
            self._default_format
        )

    def _write_catalog_items(self, items, string_format, default_format=None):
        string_format.set_fg_color('#A5ADA4')
        items = sorted(items.values(), key=itemgetter('name'))

        for index, catalog_item in enumerate(items):

            str_format = string_format if index % 2 == 0 else default_format

            self._worksheet.write(
                self._current_string_number, 0, catalog_item['remote_id'],
                str_format
            )
            self._worksheet.write(
                self._current_string_number, 1, catalog_item['name'],
                str_format
            )
            self._worksheet.write(
                self._current_string_number, 2,
                self._action_label(catalog_item), str_format
            )
            price_items = []

            for i, price_item in enumerate(catalog_item['prices']):
                price_items.append(' - '.join(price_item))

            self._worksheet.write(
                self._current_string_number, 3,
                "{}".format('\n'.join(price_items)), str_format
            )
            if len(price_items) > 1:
                self._worksheet.set_row(self._current_string_number,
                                        len(price_items) * 17)

            elif len(catalog_item['name']) > 40:
                self._worksheet.set_row(
                    self._current_string_number,
                    ((int(len(catalog_item['name']) / 40) + 1) * 17)
                )
            self._current_string_number += 1
