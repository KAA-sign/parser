import datetime
from collections import namedtuple

from bs4 import BeautifulSoup
import bs4
import requests


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
        
        url = 'https://www.avito.ru/nizhniy_novgorod/zemelnye_uchastki/prodam-ASgBAgICAUSWA9oQ'
        r = self.session.get(url, params=params)
        return r.text

    


    def parse_block(self, item):

        # выбрать блок со ссылкой
        url_block = item.select_one('a.link-link-39EVK')
        href = url_block.get('href')
        if href:
            url = 'https://www.avito.ru/' + href
        else:
            url = None

        # выбрать блок с названием
        title_blok = item.select_one('div.iva-item-titleStep-2bjuh h3')
        title = title_blok.string.strip()
        
        # выбрать блок с ценой и валютой
        price_block = item.select_one('span.price-text-1HrJ_')
        price_block = price_block.get_text('\n')
        price_block = list(filter(None, map(lambda i: i.strip(), price_block.split('\n'))))
        if len(price_block) == 2:
            price, currency = price_block
        else:
            price, currency = None, None
            print('Что-то пошло не так при поиске цены:', price_block)

        # выбрать блок с датой размещения объявления
        date = None
        date_block = item.select_one('span.tooltip-target-wrapper-XcPdv div.date-text-2jSvU.text-text-1PdBw.text-size-s-1PUdo.text-color-noaccent-bzEdI')
        date = date_block.string.strip()
        # absolute_date = date_block('absolute_date')
        # if absolute_date:
        #     date = self.parse_date(item=absolute_date)


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

        container = soup.select('span.pagination-item-1WyVp')
        last_batton = container[-2]
        print(last_batton)

    def get_blocks(self):
        text = self.get_page(page=2)
        soup = bs4.BeautifulSoup(text, 'lxml')

        # Запрос CSS-селектора, состоящего изх множества классовб производится через select
        container = soup.select('div.iva-item-root-G3n7v.photo-slider-slider-3tEix.iva-item-list-2_PpT.iva-item-redesign-1OBTh.iva-item-responsive-1z8BG.items-item-1Hoqq.items-listItem-11orH.js-catalog-item-enum')
        for item in container:
            block = self.parse_block(item=item)
            print(block)


def main():
    p = AvitoParser()
    p.get_pagination_limit()
    # p.get_blocks()

if __name__ == '__main__':
    main()