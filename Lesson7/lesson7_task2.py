# Написать программу, которая собирает «Хиты продаж» с сайтов техники М.видео, ОНЛАЙН ТРЕЙД и складывает данные в БД.
# Магазины можно выбрать свои. Главный критерий выбора: динамически загружаемые товары.

from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.request import urlretrieve
import os
import datetime


class HitSaleParse:

    def __init__(self, path_of_driver):
        self.option = Options()
        self.option.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})
        self.path_of_driver = path_of_driver

    def parse(self):
        """
        метод собирает иведения о товарах из рубрики Хит продаж сайта компании ОнлайнТрэйд.
        Изображения товара складвает в папку ./download, которую создает в каталоге исполняемого файла
        """
        driver = webdriver.Chrome(chrome_options=self.option, executable_path=self.path_of_driver)
        wait = WebDriverWait(driver, 10)
        driver.get("https://www.onlinetrade.ru/")
        driver.implicitly_wait(10)
        elements = driver.find_elements_by_xpath('//div[@class = "indexGoods"][2]'
                                                 '/div/div[2]/div[2]/div/div/div/div[2]/a')
        hrefs = []
        list_products = []
        for element in elements:
            hrefs.append(element.get_attribute("href"))
        if not os.path.exists('download'):
            os.mkdir('download')
        os.chdir('download')
        for href in hrefs:
            driver.get(href)
            name = wait.until(ec.visibility_of_all_elements_located(
                (By.XPATH, '//h1[@itemprop="name"]')))
            price = driver.find_element_by_xpath('//div[@class = "productPage__priceCover"]/div/span/span')
            img = driver.find_element_by_xpath('//div[@class="productPage__displayedItem__images__big"]/a/img')
            src = img.get_attribute('src')
            file = str(datetime.datetime.today().strftime("%Y%m%d_%H_%M_%S_%f")) + '.jpg'
            urlretrieve(src, file)
            list_products.append({'product': name[0].text, 'price': price.text,
                                  'href': href, 'file_path': os.path.join(os.getcwd(), file)})
        driver.quit()
        return list_products


class DbMongo:

    def __init__(self, base, coll):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[base]
        self.collection = self.db[coll]

    def db_add(self, list_row):
        for new_row in list_row:
            self.collection.insert_one(new_row)


if __name__ == '__main__':
    parser = HitSaleParse(r'C:\chromedriver.exe')
    product = parser.parse()
    mongo = DbMongo('test', 'HitSale')
    mongo.db_add(product)
