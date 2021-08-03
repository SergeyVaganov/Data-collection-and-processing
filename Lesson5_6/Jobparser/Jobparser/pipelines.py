from pymongo import MongoClient
from scrapy.pipelines.files import FilesPipeline


class JobparserPipeline(object):

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client['test']

    def process_item(self, item, spider):
        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item

