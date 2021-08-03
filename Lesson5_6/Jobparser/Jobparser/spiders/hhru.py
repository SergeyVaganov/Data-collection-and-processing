import scrapy
from Jobparser.Jobparser.items import JobparserItem, MyItemLoaderHh


class HhruSpider(scrapy.Spider):
    # HeadHunter
    name = 'hhru'
    allowed_domains = ['hh.ru']

    def __init__(self, mark, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://hh.ru/search/vacancy?'
                           f'clusters=true&enable_snippets=true&salary=&st=searchVacancy&text={mark}']

    def parse(self, response, **kwargs):
        url_pages = response.css('span.bloko-form-spacer a.bloko-button::attr(href)').extract()
        for url_page in url_pages:
            url = response.urljoin(url_page)
            yield scrapy.Request(url)
        url_pages = response.xpath('//*[@class = "vacancy-serp-item__info"]/span/span/span/a/@href').extract()
        for url_page in url_pages:
            url = response.urljoin(url_page)
            yield scrapy.Request(url, callback=self.parse_page)

    @classmethod
    def parse_page(cls, response):
        vacancy = MyItemLoaderHh(item=JobparserItem(), response=response)
        vacancy.add_xpath("name", '//*[@class = "vacancy-title"]/h1/text()')
        vacancy.add_xpath("salary_min", '//*[@class = "vacancy-title"]/p/span/text()[1]')
        vacancy.add_xpath("salary_max", '//*[@class = "vacancy-title"]/p/span/text()[1]')
        vacancy.add_value("href", response.url)
        vacancy.add_value('host', 'http://hh.ru')
        yield vacancy.load_item()
