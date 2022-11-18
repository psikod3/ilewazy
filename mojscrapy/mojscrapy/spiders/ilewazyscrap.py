import scrapy
import pandas as pd


class IlewazyscrapSpider(scrapy.Spider):
    name = 'ilewazyscrap'
    # allowed_domains = ['example.com']
    start_urls = ['http://www.ilewazy.pl/produkty/page/' + str(i) for i in range(1, 352)]

    def parse(self, response, **kwargs):
        # url = 'https://justjoin.it/api/offers'
        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.products_list)

    def products_list(self, response):
        base = 'http://www.ilewazy.pl'
        link_list = response.xpath('//li[@class="span3"]/a/@href').getall()
        for link in link_list:
            whole_link = base + link
            yield scrapy.Request(whole_link, callback=self.reader)

    def reader(self, response):
        product_name = response.xpath('//h1/text()').getall()
        table = response.xpath('//table[@id="ilewazy-ingedients"]').get()
        composition_df = pd.read_html(table)[0]
        results = composition_df.rename(columns={'Unnamed: 0': product_name[0]}).to_dict()
        # import pdb
        # pdb.set_trace()
        yield {product_name[0]: results}

# Add FEED_EXPORT_ENCODING = 'utf-8' to settings.py if saving as .json
# https://doc.scrapy.org/en/master/topics/feed-exports.html#std-setting-FEED_EXPORT_ENCODING
