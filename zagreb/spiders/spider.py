import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import ZagrebItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class ZagrebSpider(scrapy.Spider):
	name = 'zagreb'
	start_urls = ['https://www.zaba.hr/home/o-nama/press/novosti']


	def parse(self, response):
		post_links = response.xpath('//article[@class="article-small"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="pagination-last"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)
		else:
			years = response.xpath('//select[@id="godina"]//text()').getall()
			years = [year.strip() for year in years if year.strip()]
			for year in years:
				yield scrapy.Request(f'https://www.zaba.hr/home/o-nama/press/novosti-arhiva/{year}/', self.parse)


	def parse_post(self, response):

		date = response.xpath('//div[@class="meta-field"]/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="single-article-content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=ZagrebItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
