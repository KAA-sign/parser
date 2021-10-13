import logging
import collections
import csv
from os import write

import bs4
import requests


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wb')


ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'brand_name',
        'goods_name',
        'url',
    ),
)

HEADERS = (
    'Бренд',
    'Товар',
    'Ссылка',
)

class WbParser:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'Accept-Language': 'ru',
        }
        self.result = []

    def load_page(self):
        url = 'https://www.wildberries.ru/catalog/muzhchinam/odezhda/verhnyaya-odezhda?sort=priceup&page=4&xsubject=171&bid=d6e5b23d-63f7-4564-af76-a15210b5f4b6'
        res = self.session.get(url=url)
        res.raise_for_status()
        return res.text

    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.product-card.j-card-item')
        for block in container:
            self.parse_block(block=block)

    def parse_block(self, block):

        url_block = block.select_one('a.product-card__main.j-open-full-product-card')
        if not url_block:
            logger.error('No url block found')
            return

        href = url_block.get('href')
        if href:
            url = 'https://www.wildberries.ru' + href
        else:
            logger.error('no href')
            return


        name_block = block.select_one('div.product-card__brand-name')
        if not name_block:
            logger.error(f'no name block {url}')
            return


        brand_name = name_block.select_one('strong.brand-name')
        if not brand_name:
            logger.error(f'no brand_name {url}')
            return

        brand_name = brand_name.text
        brand_name = brand_name.replace('/', '').strip()

        goods_name = name_block.select_one('span.goods-name')
        if not brand_name:
            logger.error(f'no goods_name {url}')
            return

        goods_name = goods_name.text.strip()


        self.result.append(ParseResult(
            url=url,
            brand_name=brand_name,
            goods_name=goods_name,
        ))

        logger.debug('%s, %s, %s', url, brand_name, goods_name)
        logger.debug('-' * 150)

    def save_result(self):
        path = '/home/anthony/projects/parser/wildberries/test.csv'
        with open(path, 'w') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)

    def run(self):
        text = self.load_page()
        self.parse_page(text=text)
        logger.info(f'Получили {len(self.result)} элементов')

        self.save_result()


if __name__ == '__main__':
    parser = WbParser()
    parser.run()
