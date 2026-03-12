import scrapy


class SampleSpiderSpider(scrapy.Spider):
    name = "sample_spider"
    allowed_domains = ["example.com"]
    start_urls = ["http://example.com"]

    def parse(self, response):
        pass
