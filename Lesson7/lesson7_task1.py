# Написать программу, которая собирает входящие письма из своего или тестового почтового ящика, и сложить информацию
# о письмах в базу данных(от кого, дата отправки, тема письма, текст письма).

from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re
import datetime


class MailParse:

    def __init__(self, path_of_driver):
        self.option = Options()
        self.option.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})
        self.path_of_driver = path_of_driver

    @classmethod
    def date_transform(cls, data):
        condition = r'^сегодня'
        if re.match(condition, data):
            data_trans = str(datetime.datetime.today().strftime("%d %b")) + data[7:]
        else:
            data_trans = data
        return data_trans

    def parse(self, login, passwd,):
        driver = webdriver.Chrome(chrome_options=self.option, executable_path=self.path_of_driver)
        wait = WebDriverWait(driver, 10)
        driver.get("https://passport.yandex.ru/auth?origin=home_yandexid&retpath=https%3A%2F%2Fyandex.ru&"
                   "backpath=https%3A%2F%2Fyandex.ru")
        element = wait.until(ec.element_to_be_clickable((By.XPATH, "//input[@name='login']")))
        element.send_keys(login)
        element.send_keys(Keys.ENTER)
        element = wait.until(ec.element_to_be_clickable((By.XPATH, "//input[@name='passwd']")))
        element.send_keys(passwd)
        element.send_keys(Keys.ENTER)
        element = wait.until(ec.element_to_be_clickable(
            (By.XPATH, '//div[@class = "desk-notif-card__details"]/div[1]/a')))
        element.send_keys(Keys.ENTER)
        driver.switch_to.window(driver.window_handles[1])
        elements = wait.until(ec.visibility_of_all_elements_located(
            (By.XPATH, '//div[@class = "mail-MessageSnippet-Content"]/parent::a')))
        letters = []
        for el in elements:
            el.click()
            title = wait.until(ec.visibility_of_all_elements_located(
                (By.XPATH, '//div[@class = "mail-Message-Toolbar-Content '
                           'js-mail-Message-Toolbar-Content"]/span/div')))
            date = driver.find_element_by_xpath('//div[@class = "mail-Message-Head-Floor '
                                                'mail-Message-Head-Floor_top"]/div[3]')
            date = self.date_transform(date.text)
            sender = driver.find_element_by_xpath('//span[@class = "mail-Message-Sender-Email '
                                                  'mail-ui-HoverLink-Content"]')
            txt = driver.find_element_by_xpath('//div[@class = "js-message-body-content '
                                               'mail-Message-Body-Content"]')
            letters.append({'title': title[0].text, 'data': date, 'sender': sender.text, 'txt': txt.text})
            driver.back()
        driver.quit()
        return letters


class DbMongo:

    def __init__(self, base, coll):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[base]
        self.collection = self.db[coll]

    def db_add(self, list_row):
        for new_row in list_row:
            self.collection.insert_one(new_row)


if __name__ == '__main__':
    parser = MailParse(r'C:\chromedriver.exe')
    let = parser.parse('vaganovtest2021@yandex.ru', 'GeekBrains')
    mongo = DbMongo('test', 'MailParse')
    mongo.db_add(let)
