# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView

from main.views import \
    IndexView, \
    ProductListView, \
    ProductDetailsView, \
    ParsingHistoryView, \
    GenerateParsingFileView, \
    ProfileCustomizationView
from main.views.api import StartParsingView, CheckCompleteParsingView


# auth
urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
]

# main views
urlpatterns += [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^products/$', ProductListView.as_view(), name='product-list'),
    url(r'^products/(?P<product_id>\d+)/$',
        ProductDetailsView.as_view(), name='product-detail'),
    url(r'^products/(?P<type>\w+)/$',
        ProductListView.as_view(), name='product-list'),
    url(r'^parsing_history/$',
        ParsingHistoryView.as_view(), name='parsing_history'),
    url(r'^parsing_history/(?P<parsing_result_id>\d+)/download/$',
        GenerateParsingFileView.as_view(), name='parsing_download'),
    url(r'^themes/$',
        ProfileCustomizationView.as_view(), name='themes'),
]

# api
urlpatterns += [
    url(r'^parsing/start/$', StartParsingView.as_view(),
        name='start_parsing'),
    url(r'^parsing/check/$', CheckCompleteParsingView.as_view(),
        name='check_parsing_result'),
]
