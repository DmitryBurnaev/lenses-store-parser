# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import UpdateView

from common.xlsx import UploadXlsx
from main.forms import FilterForm, ProfileCustomizationForm
from main.models import ParseResultLog, Product


class DynamicTemplateMixin(object):
    """ Миксин использутся для динамического определения шаблонов той темы,
        которая указана у пользователя
    """
    template_name = None
    request = None

    def get_template_names(self):
        try:
            customize = self.request.user.customize
        except AttributeError:
            _prefix = 'simple'
        else:
            _prefix = customize.template

        template_prefix = 'dashboard_{}'.format(_prefix)
        return ['{}/{}'.format(template_prefix, self.template_name)]


class IndexView(LoginRequiredMixin, DynamicTemplateMixin, TemplateView):
    """ Индексная страница """

    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        ctx = super(IndexView, self).get_context_data(**kwargs)
        _parse = ParseResultLog.objects.filter(finish_time__isnull=True).last()
        ctx.update({
            'process_parsing': _parse,
            'last_parsing': ParseResultLog.objects.available().last(),
        })
        return ctx


class ProductListView(LoginRequiredMixin, DynamicTemplateMixin, ListView):
    """ View дял отображения товаров - с возможностью фильтрации и поиска """

    model = Product
    context_object_name = 'products'
    template_name = 'products/list.html'
    _current_type = 'lenses'
    _current_filters = {}
    _search_query = None

    def _process_query(self):
        self.form = FilterForm(self.request.GET)
        if self.form.is_valid():
            self._current_filters = self.form.cleaned_data
            self._search_query = self.form.cleaned_data.get('name__icontains', '')

    def get_queryset(self):
        qs = super(ProductListView, self).get_queryset()
        self._current_type = self.kwargs.get('type')
        self._process_query()

        if self._current_type:
            qs = qs.filter(type=self._current_type)
        if self._current_filters:
            qs = qs.filter(**self._current_filters)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(ProductListView, self).get_context_data(**kwargs)
        ctx.update({
            'form': self.form,
            'presentation_types': Product.TYPE_CHOICES,
            'current_type': self.event_type,
            'search_query': self._search_query,
        })
        return ctx

    @property
    def event_type(self):
        return 'search_result' if self._search_query else self._current_type


class ProductDetailsView(LoginRequiredMixin, DynamicTemplateMixin, DetailView):
    """ Карточка товара """
    model = Product
    template_name = 'products/details.html'
    pk_url_kwarg = 'product_id'


class ParsingHistoryView(LoginRequiredMixin, DynamicTemplateMixin, ListView):
    """ Список результатов парсинга - с возможностью пагинации """

    template_name = 'parsing_history.html'
    context_object_name = 'parsing_results'
    ordering = ('-date_created',)
    paginate_by = settings.PARSE_RESULT_PAGINATE_BY
    queryset = ParseResultLog.objects.available()


class ProfileCustomizationView(LoginRequiredMixin, DynamicTemplateMixin,
                               UpdateView):
    """ Возможность настройки профиля. на данный момент - выбор темы """

    form_class = ProfileCustomizationForm
    template_name = 'profile_customization.html'

    def get_success_url(self):
        return reverse('main:themes')

    def get_context_data(self, **kwargs):
        ctx = super(ProfileCustomizationView, self).get_context_data(**kwargs)
        ctx['current_template'] = getattr(self.object, 'template', '')
        return ctx

    def get_object(self, queryset=None):
        user = self.request.user
        return getattr(user, 'customize', None)

    def get_initial(self):
        initial = super(ProfileCustomizationView, self).get_initial()
        initial['user'] = self.request.user
        return initial


class GenerateParsingFileView(DetailView):
    """ Формирование файла в памяти для скачивания пользователем """

    pk_url_kwarg = 'parsing_result_id'
    model = ParseResultLog
    object = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = HttpResponse(content_type="application/vnd.ms-excel")
        response['Content-Disposition'] = \
            'attachment; filename="ParseResult_{0}.xlsx"' \
            .format(self.object.date_created.strftime('%d.%m.%Y_%H-%M'))
        UploadXlsx(self.object.received_data, response=response).get_workbook()
        return response
