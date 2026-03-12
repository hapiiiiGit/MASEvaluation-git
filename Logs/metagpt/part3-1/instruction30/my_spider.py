import scrapy
from bs4 import BeautifulSoup
import json

class MySpider(scrapy.Spider):
    name = 'my_spider'
    start_urls = ['http://example.com']  # Replace with the target URL

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        headings = soup.find_all('h1')
        scraped_data = [{'heading': heading.get_text()} for heading in headings]
        
        # Save the scraped data to a JSON file
        with open('scraped_data.json', 'w') as f:
            json.dump(scraped_data, f)

# Run the spider (this should be done in a Scrapy command line, not in this script)
# scrapy runspider my_spider.py
