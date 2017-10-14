# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Product, Price, Brand, ParseResultLog, ProfileCustomization


class PriceAdminInline(admin.TabularInline):
    model = Price
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    inlines = [PriceAdminInline]
    list_display = ('id', 'name', 'type', 'brand', 'has_action')
    list_display_links = list_display
    list_filter = ('type', 'has_action', 'brand', )


class ProductAdminInline(admin.TabularInline):
    model = Product
    extra = 0


class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'remote_id', 'name', 'url')
    list_display_links = ('id', 'name')
    inlines = (ProductAdminInline,)


class PriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'value')
    list_display_links = list_display


class ParserLogAdmin(admin.ModelAdmin):
    pass


class ProfileCustomizationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Product, ProductAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(ParseResultLog, ParserLogAdmin)
admin.site.register(ProfileCustomization, ProfileCustomizationAdmin)
