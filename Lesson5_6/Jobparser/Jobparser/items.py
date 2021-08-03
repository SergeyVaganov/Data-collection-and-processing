import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader
import re


def parse_salary(text_salary):
    """Парсер поля зарпалта"""
    salary_min = '0'
    salary_max = '0'
    res_1 = re.match(r'^от\s*([\d\s]*)', text_salary)  # шаблон "от ddd ddd руб."
    if res_1 is not None:
        salary_min = res_1.group(1)
    res_2 = re.match(r'^до\s*([\d\s]*)', text_salary)  # шаблон "до ddd ddd руб."
    if res_2 is not None:
        salary_max = res_2.group(1)
    res_3 = re.match(r'^[от]*\s*([\d\s]+)[^\s\d]+([\d\s]+)', text_salary)  # шаблон "ddd ddd - ddd ddd руб."
    if res_3 is not None:
        salary_min = res_3.group(1)
        salary_max = res_3.group(2)
    res_4 = re.match(r'^\s*([\d\s]+)[^\d]+$', text_salary)  # шаблон "ddd ddd руб."
    if res_4 is not None:
        salary_min = res_4.group(1)
        salary_max = 0
    pattern = re.compile(r'\s+')
    salary_min = int(re.sub(pattern, '', salary_min))
    salary_max = int(re.sub(pattern, '', salary_max))
    return salary_min, salary_max


def get_min(text_salary):
    return parse_salary(text_salary)[0]


def get_max(text_salary):
    return parse_salary(text_salary)[1]


class JobparserItem(scrapy.Item):
    name = scrapy.Field()
    salary_min = scrapy.Field()
    salary_max = scrapy.Field()
    href = scrapy.Field()
    host = scrapy.Field()
    _id = scrapy.Field()


class MyItemLoaderHh(ItemLoader):
    default_output_processor = TakeFirst()
    salary_min_in = MapCompose(get_min)
    salary_max_in = MapCompose(get_max)


class MyItemLoaderSuper(ItemLoader):
    default_output_processor = TakeFirst()
    default_input_processor = Join(separator='')
    salary_min_out = MapCompose(lambda x: str(x).replace('\xa0', ''), get_min)
    salary_max_out = MapCompose(lambda x: str(x).replace('\xa0', ''), get_max)


class LeroyItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    href = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()
    volume = scrapy.Field()
    price = scrapy.Field()
    base = scrapy.Field()