# Написать приложение, которое собирает основные новости с сайтов mail.ru, lenta.ru, yandex-новости.
# Для парсинга использовать XPath. Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.

import requests
from lxml import html
import pandas as pd
from datetime import datetime


class ParserNews:

    def __init__(self):
        pass

    @classmethod
    def _request(cls, url):
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
        response = requests.get(url, headers=header)
        return html.fromstring(response.text)

    @classmethod
    def _parser_mail(cls):
        now = datetime.today().strftime("%Y-%m-%d")
        paths_news = ['//*[@class="daynews__item daynews__item_big"]/a/span/span[1]/text()',
                      '//*[@class="daynews__item"]/a/span/span[1]/text()',
                      '//*[@class="list__item"]/a/text()',
                      '//*[@class="list__item"]/span/a/span/text()',
                      '//*[@class="cell"]/a/span/text()']
        paths_href = ['//*[@class="daynews__item daynews__item_big"]/a/@href',
                      '//*[@class="daynews__item"]/a/@href',
                      '//*[@class="list__item"]/a/@href',
                      '//*[@class="list__item"]/span/a/@href',
                      '//*[@class="cell"]/a/@href']
        parsed = cls._request('https://news.mail.ru')
        news = [i for el in paths_news for i in parsed.xpath(el)]
        href = [i for el in paths_href for i in parsed.xpath(el)]
        time = []
        for url in href:
            parsed = cls._request(url)
            paths_time = '//*[@class="note"]/span/@datetime'
            time.append(str(parsed.xpath(paths_time))[13:18] + ' ' + now)
        data = {'News': news, 'Href': href, 'Time': time}
        data_frame = pd.DataFrame(data)
        data_frame['Host'] = 'https://news.mail.ru'
        return data_frame

    @classmethod
    def _parser_lenta(cls):
        now = datetime.today().strftime("%Y-%m-%d")
        paths_news = ['//*[@id="root"]/section[2]/div/div/div/section[1]/div/div/h2/a/text()',
                      '//*[@id="root"]/section[2]/div/div/div/section[1]/div/div/a/text()']
        paths_href = ['//*[@id="root"]/section[2]/div/div/div/section[1]/div/div/a/@href']
        paths_time = ['//*[@id="root"]/section[2]/div/div/div/section[1]/div/div/h2/a/time/text()',
                      '//*[@id="root"]/section[2]/div/div/div/section[1]/div/div/a/time/text()']
        parsed = cls._request('https://lenta.ru')
        news = [i for el in paths_news for i in parsed.xpath(el)]
        news.pop()
        href = []
        for path in paths_href:
            result = parsed.xpath(path)
            for element in result:
                if str(element).split(sep='//')[0] != 'https:':
                    href.append('https://lenta.ru' + element)
                else:
                    href.append(element)
        href.pop()
        time = [i + ' ' + now for el in paths_time for i in parsed.xpath(el)]
        data = {'News': news, 'Href': href, 'Time': time}
        data_frame = pd.DataFrame(data)
        data_frame['Host'] = 'https://lenta.ru'
        return data_frame

    @classmethod
    def _parser_yandex(cls):
        now = datetime.today().strftime("%Y-%m-%d")
        paths_news = ['//*[@class="mg-grid__col mg-grid__col_xs_8"]/article/div[2]/a/h2/text()',
                      '//*[@class="mg-grid__col mg-grid__col_xs_6"]/article/div[1]/div[1]/div/a/h2/text()',
                      '//*[@class="mg-grid__col mg-grid__col_xs_4"]/article/div[1]/div/a/h2/text()']
        paths_href = ['//*[@class="mg-grid__col mg-grid__col_xs_8"]/article/div[2]/a/@href',
                      '//*[@class="mg-grid__col mg-grid__col_xs_6"]/article/div[1]/div[1]/div/a/@href',
                      '//*[@class="mg-grid__col mg-grid__col_xs_4"]/article/div/div/a/@href']
        paths_time = ['//*[@class="mg-grid__col mg-grid__col_xs_8"]/article/div[2]/div[2]/div[1]/div/span[2]/text()',
                      '//*[@class="mg-grid__col mg-grid__col_xs_6"]/article/div[2]/div[1]/div/span[2]/text()',
                      '//*[@class="mg-grid__col mg-grid__col_xs_4"]/article/div[3]/div[1]/div/span[2]/text()']
        parsed = cls._request('https://yandex.ru/news')
        news = [i for el in paths_news for i in parsed.xpath(el)]
        href = [i for el in paths_href for i in parsed.xpath(el)]
        time = [i + ' ' + now for el in paths_time for i in parsed.xpath(el)]
        data = {'News': news, 'Href': href, 'Time': time}
        data_frame = pd.DataFrame(data)
        data_frame['Host'] = 'https://yandex.ru/news'
        return data_frame

    @classmethod
    def parse(cls, save=None):
        """Метод класса запускающий работу всех встроенных парсеров"""
        data = [cls._parser_mail(), cls._parser_lenta(), cls._parser_yandex()]
        data_frame = pd.concat(data, axis=0, ignore_index=True)
        if save is not None:
            data_frame.to_csv(save)
        return data_frame


if __name__ == '__main__':
    df = ParserNews.parse()
    for index in range(len(df.index)):
        print(df.iloc[index])
