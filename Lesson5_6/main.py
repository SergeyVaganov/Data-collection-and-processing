from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from Jobparser.Jobparser import settings
from Jobparser.Jobparser.spiders.hhru import HhruSpider
from Jobparser.Jobparser.spiders.superjob import SuperjobSpider
from Jobparser.Jobparser.spiders.leroy import LeryoMerlin


if __name__ == '__main__':
	crawler_settings = Settings()
	crawler_settings.setmodule(settings)
	process = CrawlerProcess(settings=crawler_settings)
	process.crawl(HhruSpider, mark='Программист')				# HeadHunter
	# process.crawl(SuperjobSpider, mark='Программист')			# SuperJob
	# process.crawl(LeryoMerlin)								# Леруа Мерлен
	process.start()
