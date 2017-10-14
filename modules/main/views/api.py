# -*- coding: utf-8 -*-
from django.http import JsonResponse
from celery.result import AsyncResult
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from main.models import ParseResultLog
from main.tasks import global_sync


class ApiMixIn(object):
    """ Миксин для стандартных json ответов """

    @staticmethod
    def api_response(status, response_type, data=None):
        response_data = {
            'status': status,
            'type': response_type,
            'data': data or {}
        }
        return JsonResponse(data=response_data, encoder=DjangoJSONEncoder)


class BaseApiView(LoginRequiredMixin, View, ApiMixIn):
    """ Базовый класс с минимальным набором классов необходимых для работы с
        API
    """

    kwargs = None
    CLIENT_NOTICE = 0
    CLIENT_WARN = 1
    CLIENT_ERROR = 2

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(BaseApiView, self).dispatch(request, *args, **kwargs)

    def notice(self, message, data):
        return self.api_response(message, self.CLIENT_NOTICE, data)

    def warning(self, message, data):
        return self.api_response(message, self.CLIENT_WARN, data)

    def error(self, message, data):
        return self.api_response(message, self.CLIENT_ERROR, data)


class StartParsingView(BaseApiView):
    """ Запуск на выполнение парсинга """

    def get(self, request):
        global_sync.apply_async()
        return self.notice('Запущена задача на экспорт данных', {})


class CheckCompleteParsingView(BaseApiView):
    """ Проверка на завершение выполнения парсинга: может выполняться
        периодически по запросу от клиента
    """

    def get(self, request):
        continue_parsing = ParseResultLog.objects.last()
        if continue_parsing and continue_parsing.in_progress:
            status = 'IN_PROGRESS'
        else:
            status = 'READY'
        return self.notice('Статус выполнения задачи', {'status': status})


class CheckCeleryResultView(BaseApiView):
    """ Проверка статуса выполнение селери задачи """

    def get(self, request):
        celery_task_uuid = request.GET.get('celery_task_uuid')
        task_result = AsyncResult(celery_task_uuid)
        process_status = 'READY' if task_result.ready() else 'PENDING'
        return self.notice(
            'Запущена задача на экспорт данных',
            {
                'process_status': process_status,
                'celery_task_uuid': celery_task_uuid,
                'result': task_result.result
            }
        )
