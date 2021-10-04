import datetime
import urllib.parse
from logging import getLogger

import bs4
import requests
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from aparser.constants import STATUS_NEW, STATUS_READY
from aparser.models import Product
from aparser.models import Task



logger = getLogger(__name__)


class AvitoParser:
    PAGE_LIMIT = 10

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'Accept-Language': 'ru',
        }
        self.task = None

    def find_task(self):
        obj = Task.objects.filter(status=STATUS_NEW).first()
        if not obj:
            raise BaseCommand('Task not found')
        self.task = obj
        logger.info(f'Работаем над заданием {self.task}')

    def finish_task(self):
        self.task = STATUS_READY
        self.task.save()
        logger.info(f'Закончили задание {self.task}')

    def get_page(self, page: int = None):
        params = {
            'radius': 0,
            'user': 1,
        }
        if page and page > 1:
            params['p'] = page

        url = self.task.url
        
        # url = 'https://www.avito.ru/nizhniy_novgorod/zemelnye_uchastki/prodam-ASgBAgICAUSWA9oQ?f=ASgBAgECAUSWA9oQAUXGmgwWeyJmcm9tIjowLCJ0byI6NDAwMDAwfQ'
        # url = 'https://www.avito.ru/nizhniy_novgorod/tovary_dlya_kompyutera/komplektuyuschie-ASgBAgICAUTGB~pm?cd=1&q=gtx+1070'
        r = self.session.get(url, params=params)
        r.raise_for_status()
        return r.text

    def parse_block(self, item):

        # выбрать блок со ссылкой
        url_block = item.select_one('a[itemprop]')
        if not url_block:
            raise CommandError('bad "url_block" css')

        href = url_block.get('href')
        if href:
            url = 'https://www.avito.ru' + href
        else:
            url = None

        # выбрать блок с названием

        title_blok = item.select_one('h3[itemprop]')
        if not title_blok:
            raise CommandError('bad "title_blok" css')

        title = title_blok.string.strip()
        
        # выбрать блок с ценой и валютой
        price_block = item.select_one('span.price-text-E1Y7h.text-text-LurtD.text-size-s-BxGpL')
        if not price_block:
            raise CommandError('bad "price_block" css')

        price_block = price_block.get_text('\n')
        # price_block_ = "".join(c for c in price_block if  c.isdecimal())
        # price_block = price_block_
        price_block = list(filter(None, map(lambda i: i.strip(), price_block.split('\n'))))
        if len(price_block) == 2:
            price, currency = price_block
            pr = "".join(c for c in price if  c.isdecimal())
            price = pr
            # price = int(price.replace(' ', ''))
        elif len(price_block) == 1:
            price, currency = 0, None
        else:
            price, currency = None, None
            logger.error(f'Что-то пошло не так при поиске цены: {price_block}, {url}')

        # выбрать блок с датой размещения объявления
        date = None

        date_block = item.select_one('div.date-text-VwmJG.text-text-LurtD.text-size-s-BxGpL.text-color-noaccent-P1Rfs')
        if not date_block:
            raise CommandError('bad "date_block" css')

        date = date_block.string.strip()
        # absolute_date = date_block('absolute_date')
        # if absolute_date:
        #     date = self.parse_date(item=absolute_date)

        # bbb = Block(
        #     url=url,
        #     title=title,
        #     price=price,
        #     currency=currency,
        #     date=date,
        # )
        # print(bbb)

        try:
            p = Product.objects.get(url=url)
            p.task = self.task
            p.title = title
            p.price = price
            p.currency = currency
            p.save()
        except Product.DoesNotExist:
            p = Product(
                task = self.task,
                url = url,
                title = title,
                price=price,
                currency=currency,
                published_date=date,
            ).save()

        logger.debug(f'product {p}')

        # return Block(
        #     url=url,
        #     title=title,
        #     price=price,
        #     currency=currency,
        #     date=date,
        # )
        
    def get_pagination_limit(self):
        text = self.get_page()
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('a.pagination-page')
        last_batton = container[-1]
        href = last_batton.get('href')
        if not href:
            return 1
        r = urllib.parse.urlparse(href)
    
        params = urllib.parse.parse_qs(r.query)
        return min(int(params['p'][0]), self.PAGE_LIMIT)


    def get_blocks(self, page: int = None):
        text = self.get_page(page=page)
        soup = bs4.BeautifulSoup(text, 'lxml')

        # Запрос CSS-селектора, состоящего изх множества классовб производится через select
        container = soup.select('div[data-item-id]')
        

        for item in container:
            block = self.parse_block(item=item)
            # print(block)

    def parse_all(self):
        # Выбор задания
        self.find_task()

        limit = self.get_pagination_limit()
        logger.info(f'Всего страниц: {limit}')

        for i in range(1, limit + 1):
            logger.info(f'Работаем над страницей {i}')
            self.get_blocks(page=i)

        # Завершить задание
        self.find_task()




class Command(BaseCommand):
    help = 'Парсинг Avito'

    def handle(self, *args, **options):
        p = AvitoParser()
        p.parse_all()