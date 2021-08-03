BOT_NAME = 'Jobparser.Jobparser'

SPIDER_MODULES = ['Jobparser.Jobparser.spiders']
NEWSPIDER_MODULE = 'Jobparser.Jobparser.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
             '(KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'

ROBOTSTXT_OBEY = False

LOG_ENABLED = True
LOG_LEVEL = 'DEBUG'

FEED_EXPORT_ENCODING = 'utf-8'

ITEM_PIPELINES = {
    'Jobparser.Jobparser.pipelines.JobparserPipeline': 300,
    'Jobparser.Jobparser.pipelines.FilesPipeline': 1,
}

FILES_STORE = r'downloaded'

CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 0
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 8
