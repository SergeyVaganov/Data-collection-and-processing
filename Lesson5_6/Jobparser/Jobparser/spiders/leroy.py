import scrapy
from Jobparser.Jobparser.items import LeroyItem, ItemLoader
from scrapy.loader.processors import TakeFirst


class LeryoMerlin(scrapy.Spider):
    # Леруа Мерлен каталог - Краска для стен и потолка
    name = 'leroy'
    start_urls = [f'https://leroymerlin.ru/catalogue/kraski-dlya-sten-i-potolkov/']

    def parse(self, response, **kwargs):
        url_pages = response.xpath('//*[@data-qa-pagination-item = "right"]/@href').extract()
        for url_page in url_pages:
            url = response.urljoin(url_page)
            yield scrapy.Request(url)
        url_pages_product = response.xpath('//a[@data-qa="product-name"]/@href').extract()
        for url_page in url_pages_product:
            url = response.urljoin(url_page)
            yield scrapy.Request(url, callback=self.parse_page)

    @classmethod
    def parse_page(cls, response):
        product = ItemLoader(item=LeroyItem(), response=response)
        product.add_xpath("name", '//h1[@class = "header-2"]/text()')
        product.add_value("href", response.url)
        product.add_xpath("file_urls", '//*[@slot="media-content"]//@src')
        product.add_xpath("volume", '//uc-variants[@slot = "variants"][1]/uc-variant-card/a/text()')
        product.add_xpath("base", '//uc-variants[@slot = "variants"][2]/uc-variant-card/a/text()')
        product.add_xpath("price", '//span[@slot = "price"]/text()', TakeFirst())
        yield product.load_item()
