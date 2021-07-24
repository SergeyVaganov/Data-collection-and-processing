# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую
# собранные вакансии в созданную БД.
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
# 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.

from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re


class ParserVacancy:

    def __init__(self, max_page=100):
        """
        :param max_page - максимальное количество обрабатываемых страниц при парсинге
        по умолчанию = 100. (при отладке можно сократить время работы уменьшив число страниц)
        """
        self.dataframe = None
        self.vacancy = None
        self.max_page = max_page
        pd.set_option('display.max_columns', 6)
        pd.set_option('display.max_colwidth', 150)
        pd.set_option('display.width', 900)

    @classmethod
    def _salary_parse(cls, text_salary):
        """Парсер поля зарпалта"""
        salary_min = '0'
        salary_max = '0'
        res_1 = re.match(r'^от\s*([\d\s]*)', text_salary)                   # шаблон "от ddd ddd руб."
        if res_1 is not None:
            salary_min = res_1.group(1)
        res_2 = re.match(r'^до\s*([\d\s]*)', text_salary)                   # шаблон "до ddd ddd руб."
        if res_2 is not None:
            salary_max = res_2.group(1)
        res_3 = re.match(r'^\s*([\d\s]+)[^\s\d]+([\d\s]+)', text_salary)    # шаблон "ddd ddd - ddd ddd руб."
        if res_3 is not None:
            salary_min = res_3.group(1)
            salary_max = res_3.group(2)
        res_4 = re.match(r'^\s*([\d\s]+)[^\d]+', text_salary)               # шаблон "ddd ddd руб."
        if res_4 is not None:
            salary_min = res_4.group(1)
        pattern = re.compile(r'\s+')
        salary_min = int(re.sub(pattern, '', salary_min))
        salary_max = int(re.sub(pattern, '', salary_max))
        return salary_min, salary_max

    def _parse_superjob(self):
        """персер сайта Superjob"""
        params = {'keywords': self.vacancy}
        response = requests.get('https://russia.superjob.ru/vacancy/search/', params=params)
        # soup = BeautifulSoup(response.content, "html.parser")
        main_url = response.url
        i = 1
        vacancy = []
        href = []
        salary_max = []
        salary_min = []
        while True:
            url = main_url + '?page=' + str(i)
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            a_title = soup.find_all('div', class_="f-test-vacancy-item")
            if len(a_title) == 0 or i == self.max_page + 1:
                break
            for element in a_title:
                vacancy.append(element.find('a').text)
                href.append('https://russia.superjob.ru' + element.find('a')['href'])
                pars_salary = element.find('span', class_="f-test-text-company-item-salary").text
                s_min, s_max = self._salary_parse(pars_salary)
                salary_min.append(s_min)
                salary_max.append(s_max)
            i = i + 1
        data = {'vacancy': vacancy, 'href': href, 'salary_min': salary_min, 'salary_max': salary_max}
        df = pd.DataFrame(data)
        df['host'] = 'https://Superjob.ru'
        return df

    def _parse_hh(self):
        """ персер сайта HeadHunter """
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                '(KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
        params = {'L_save_area': 'true', 'clusters': 'true', 'enable_snippets': 'true',
                  'text': self.vacancy, 'showClusters': 'true'}
        response = requests.get('https://hh.ru/search/vacancy', params=params, headers=header)
        # soup = BeautifulSoup(response.content, "html.parser")
        main_url = response.url
        i = 0
        vacancy = []
        href = []
        salary_max = []
        salary_min = []
        while True:
            url = main_url + '&page=' + str(i)
            page = requests.get(url, headers=header)
            soup = BeautifulSoup(page.content, 'html.parser')
            a_title = soup.find_all('div', class_="vacancy-serp-item")
            if len(a_title) == 0 or i == self.max_page:
                break
            for element in a_title:
                vacancy.append(element.find('div', class_='vacancy-serp-item__info').text)
                href.append(element.find('a', class_='bloko-link')['href'])
                pars_salary = element.find('div', class_="vacancy-serp-item__sidebar").text
                s_min, s_max = self._salary_parse(pars_salary)
                salary_min.append(s_min)
                salary_max.append(s_max)
            i = i + 1
        data = {'vacancy': vacancy, 'href': href, 'salary_min': salary_min, 'salary_max': salary_max}
        df = pd.DataFrame(data)
        df['host'] = 'https://hh.ru'
        return df

    def parse(self, pars_vacancy):
        """Метод класса запускающий работу всех встроенных парсеров"""
        self.vacancy = pars_vacancy
        data = [self._parse_superjob(), self._parse_hh()]
        self.dataframe = pd.concat(data, axis=0, ignore_index=True)

    def df_print(self, list_feature):
        """Вывод указанных полей датафрэйма на экран"""
        print(self.dataframe[list_feature])

    def df_get(self):
        """Получить dataframe"""
        return self.dataframe


class DbMongo:

    def __init__(self, base, coll):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[base]
        self.collection = self.db[coll]

    def db_add(self, df):
        """Добавляет не существующие записи в базу данных"""
        for index in range(0, len(df.index)):
            row = df.iloc[index]
            data = {'vacancy': row['vacancy'], 'href': row['href'], 'salary_min': int(row['salary_min']),
                    'salary_max': int(row['salary_max']), 'host': row['host']}
            result = self.collection.find_one(data)
            if result is None:
                new_row = {'vacancy': row['vacancy'], 'href': row['href'],
                           'salary_min': int(row['salary_min']), 'salary_max': int(row['salary_max']),
                           'host': row['host']}
                self.collection.insert_one(new_row)

    def db_print(self):
        """Выводит на экран все вакансии из базы вакансий"""
        result = self.collection.find({}).sort('vacancy')
        for row in result:
            print(row)

    def db_filter(self, filter_salary):
        """Производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы"""
        filter_max = {'$and': [{'salary_max': {'$gt': filter_salary}}, {'salary_max': {'$ne': 0}}]}
        filter_min = {'$and': [{'salary_mix': {'$gt': filter_salary}}, {'salary_mix': {'$ne': 0}}]}
        result = self.collection.find({'$or': [filter_min, filter_max]})
        for row in result:
            print(row)


if __name__ == '__main__':
    pars_vac = ParserVacancy(max_page=1)
    pars_vac.parse('программист')
    # pars_vac.df_print('vacancy')
    mongo = DbMongo('test', 'vacancy')
    mongo.db_add(pars_vac.df_get())
    salary = int(input('Введите минимальную зарплату: '))
    mongo.db_filter(salary)
