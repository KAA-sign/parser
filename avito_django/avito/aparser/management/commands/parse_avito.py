import datetime
import urllib.parse
from collections import namedtuple

import bs4
import requests
import time
from django.core.management.base import BaseCommand

from aparser.models import Product


InnerBlock = namedtuple('Block', 'title, price, currency, date, url')

class Block(InnerBlock):
    
    def __str__(self):
        return f'{self.title}\t{self.price}\t{self.currency}\t{self.date}\t{self.url}'


class AvitoParser:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'Accept-Language': 'ru',
        }

    def get_page(self, page: int = None):
        params = {
            'radius': 0,
            'user': 1,
        }
        if page and page > 1:
            params['p'] = page
        
        url = 'https://www.avito.ru/nizhniy_novgorod/tovary_dlya_kompyutera/komplektuyuschie/videokarty-ASgBAgICAkTGB~pm7gmmZw?f=ASgBAgECAkTGB~pm7gmmZwFFxpoMFXsiZnJvbSI6MCwidG8iOjMwMDAwfQ&q=gtx+1070'
        r = self.session.get(url, params=params)
        
        return r.text

    def parse_block(self, item):

        # выбрать блок со ссылкой
        url_block = item.select_one('a[itemprop]')
        href = url_block.get('href')
        if href:
            url = 'https://www.avito.ru' + href
        else:
            url = None

        # выбрать блок с названием

        title_blok = item.select_one('h3[itemprop]')
        title = title_blok.string.strip()
        
        # выбрать блок с ценой и валютой
        price_block = item.select_one('span.price-text-E1Y7h.text-text-LurtD.text-size-s-BxGpL')
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
            print(f'Что-то пошло не так при поиске цены: {price_block}, {url}')

        # выбрать блок с датой размещения объявления
        date = None

        date_block = item.select_one('div.date-text-VwmJG.text-text-LurtD.text-size-s-BxGpL.text-color-noaccent-P1Rfs')
        date = date_block.string.strip()
        # absolute_date = date_block('absolute_date')
        # if absolute_date:
        #     date = self.parse_date(item=absolute_date)

        p = Product(
            url = url,
            title = title,
            price=price,
            # currency=currency,
            # date=date,
        ).save()
        print(f'product {p}')

        return Block(
            url=url,
            title=title,
            price=price,
            currency=currency,
            date=date,
        )
        
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
        return int(params['p'][0])


    def get_blocks(self, page: int = None):
        text = self.get_page(page=page)
        soup = bs4.BeautifulSoup(text, 'lxml')

        # Запрос CSS-селектора, состоящего изх множества классовб производится через select
        container = soup.select('div[data-item-id]')
        

        for item in container:
            block = self.parse_block(item=item)
            print(block)

    def parse_all(self):
        limit = self.get_pagination_limit()
        print(f'Всего страниц: {limit}')

        for i in range(1, limit + 1):
            self.get_blocks(page=i)



class Command(BaseCommand):
    help = 'Парсинг Avito'

    def handle(self, *args, **options):
        p = AvitoParser()
        p.parse_all()