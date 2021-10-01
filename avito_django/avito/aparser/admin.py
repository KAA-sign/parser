from django.contrib import admin

from .models import Product
from .forms import ProductForm
from .models import Task


PRICE_FILTER_STEPS = 10

class PriceFilter(admin.SimpleListFilter):
    title = 'Цена'
    parameter_name = 'price'

    def lookups(self, request, model_admin):
        # Вытащить полный список цен
        prices = [c.price for c in model_admin.model.objects.all()]
        prices = filter(None, prices)

        # Побить на 10 интервалов
        max_price = max(prices)
        chunk = int(max_price / PRICE_FILTER_STEPS)
        print(f'max_price = {max_price}, chunk = {chunk}')

        intervals = [
            (f'{chunk * i},{chunk * (i + 1)}', f'{chunk * i} - {chunk * (i + 1)}')
            for i in range(PRICE_FILTER_STEPS)
        ]
        return intervals

    def queryset(self, request, queryset):
        choice = self.value() or ''
        if not choice:
            return queryset
        choice = choice.split(',')
        if not len(choice) == 2:
            return queryset
        price_from, price_to = choice
        return queryset.distinct().filter(price__gte=price_from, price__lt=price_to)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'price', 'currency', 'published_date', 'url')
    list_filter = ('currency', 'published_date', PriceFilter)
    form = ProductForm

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('pk', 'url', 'status')
    list_filter = ('status')
