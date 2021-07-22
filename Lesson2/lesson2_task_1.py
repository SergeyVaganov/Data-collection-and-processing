# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы)
# с сайтов Superjob и HH. Приложение должно анализировать несколько страниц сайта
# (также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:
# Наименование вакансии.
# Предлагаемую зарплату (отдельно минимальную и максимальную).
# Ссылку на саму вакансию.
# Сайт, откуда собрана вакансия.
# Структура должна быть одинаковая для вакансий с обоих сайтов.
# Общий результат можно вывести с помощью dataFrame через pandas.

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re

class parserVacanc:

    def __init__(self, max_page = 100):
        '''
        :param max_page - максимальное количество обрабатываемых страниц при парсинге
        по умолчанию = 100. (при отладке можно сократить время работы уменьшив число страниц)
        '''
        self.dataframe = None
        self.vacanc = None
        self.max_page = max_page
        pd.set_option('display.max_columns', 6)
        pd.set_option('display.max_colwidth', 150)
        pd.set_option('display.width', 900)

    def _salaryParse(self, salary):
        '''Парсер поля зарпалта'''
        smin = '0'
        smax = '0'
        result = re.match(r'^от\s*([\d\s]*)', salary)               # шаблон "от ddd ddd руб."
        if result is not None:
            smin = result.group(1)
        result = None
        result = re.match(r'^до\s*([\d\s]*)', salary)               # шаблон "до ddd ddd руб."
        if result is not None:
            smax = result.group(1)
        result = None
        result = re.match(r'^\s*([\d\s]+)[^\s\d]+([\d\s]+)', salary) # шаблон "ddd ddd - ddd ddd руб."
        if result is not None:
            smin = result.group(1)
            smax = result.group(2)
        result = None
        result = re.match(r'^\s*([\d\s]+)[^\d]+', salary)            # шаблон "ddd ddd руб."
        if result is not None:
            smin = result.group(1)
        pattern = re.compile(r'\s+')
        smin = int(re.sub(pattern, '', smin))
        smax = int(re.sub(pattern, '', smax))
        return smin, smax

    def _parseSuperjob(self):
        '''персер сайта Superjob'''
        params = {'keywords': self.vacanc}
        response = requests.get('https://russia.superjob.ru/vacancy/search/', params=params)
        soup = bs(response.content, "html.parser")
        mainUrl = response.url
        i = 1
        vacancie = []
        href = []
        smax = []
        smin = []
        while True:
            url = mainUrl + '?page=' + str(i)
            page = requests.get(url)
            soup = bs(page.content, 'html.parser')
            a_title = soup.find_all('div', class_="f-test-vacancy-item")
            if len(a_title) == 0 or i == self.max_page + 1:
                break
            for element in a_title:
                vacancie.append(element.find('a').text)
                href.append('https://russia.superjob.ru' + element.find('a')['href'])
                salary = element.find('span', class_="f-test-text-company-item-salary").text
                s_min, s_max = self._salaryParse(salary)
                smin.append(s_min)
                smax.append(s_max)
            i = i + 1
        data = {'vacancie': vacancie, 'href': href, 'salary_min':smin, 'salary_max':smax}
        df = pd.DataFrame(data)
        df['host'] = 'https://Superjob.ru'
        return df

    def _parseHH(self):
        '''персер сайта HeadHunter'''
        header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/79.0.3945.130 Safari/537.36'}
        params = {'L_save_area': 'true', 'clusters' : 'true', 'enable_snippets':'true',
                  'text': self.vacanc, 'showClusters':'true'}
        response = requests.get('https://hh.ru/search/vacancy', params=params, headers = header)
        soup = bs(response.content, "html.parser")
        mainUrl = response.url
        i = 0
        vacancie = []
        href = []
        smax = []
        smin = []
        while True:
            url = mainUrl + '&page=' + str(i)
            page = requests.get(url, headers=header)
            soup = bs(page.content, 'html.parser')
            a_title = soup.find_all('div', class_="vacancy-serp-item")
            if len(a_title) == 0 or i == self.max_page:
                break
            for element in a_title:
                vacancie.append(element.find('div', class_='vacancy-serp-item__info').text)
                href.append(element.find('a', class_='bloko-link')['href'])
                salary = element.find('div', class_="vacancy-serp-item__sidebar").text
                s_min, s_max = self._salaryParse(salary)
                smin.append(s_min)
                smax.append(s_max)
            i = i + 1
        data = {'vacancie': vacancie, 'href': href, 'salary_min': smin, 'salary_max': smax}
        df = pd.DataFrame(data)
        df['host'] = 'https://hh.ru'
        return df

    def parse(self, vacanc):
        '''Метод класса запускающий работу всех встроенных парсеров'''
        self.vacanc = vacanc
        data = [self._parseSuperjob(), self._parseHH()]
        self.dataframe = pd.concat(data, axis=0, ignore_index=True)

    def prn(self, list):
        '''Вывод датафрэйма на экран'''
        print(self.dataframe[list])


if __name__ == '__main__':
    vacanc = parserVacanc(max_page=2)
    vacanc.parse('программист')
    vacanc.prn(['vacancie','href', 'salary_min', 'salary_max', 'host'])
