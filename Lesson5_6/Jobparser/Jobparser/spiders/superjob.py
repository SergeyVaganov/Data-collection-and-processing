import scrapy
from Jobparser.Jobparser.items import JobparserItem, MyItemLoaderSuper


class SuperjobSpider(scrapy.Spider):
    # SuperJob
    name = 'superjob'
    allowed_domains = ['superjob.ru']

    def __init__(self, mark, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://russia.superjob.ru/vacancy/search/?keywords={mark}']

    def parse(self, response, **kwargs):
        url_pages = response.xpath('//*[@rel = "next"]/@href').extract()
        for url_page in url_pages:
            url = response.urljoin(url_page)
            yield scrapy.Request(url)
        url_pages = response.xpath('//div[@class = "f-test-search-result-item"]/div/div/div/div/'
                                   'div[3]/div/div[1]/div/a/@href').extract()
        for url_page in url_pages:
            url = response.urljoin(url_page)
            yield scrapy.Request(url, callback=self.parse_page)

    @classmethod
    def parse_page(cls, response):
        vacancy = MyItemLoaderSuper(item=JobparserItem(), response=response)
        vacancy.add_xpath("name", '//h1[1]/text()')
        vacancy.add_xpath("salary_min", '//h1[1]/parent::*/span//text()')
        vacancy.add_xpath("salary_max", '//h1[1]/parent::*/span//text()')
        vacancy.add_value("href", response.url)
        vacancy.add_value('host', 'http://superjob.ru')
        yield vacancy.load_item()
