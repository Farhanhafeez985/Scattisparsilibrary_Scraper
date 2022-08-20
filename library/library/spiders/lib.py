import scrapy
from scrapy import Request


class LibSpider(scrapy.Spider):
    name = 'lib'
    allowed_domains = ['https://www.scattisparsi-libreria.com']
    start_urls = ['https://www.scattisparsi-libreria.com/']
    custom_settings = {'ROBOTSTXT_OBEY': False, 'LOG_LEVEL': 'INFO',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': 5,
                       'RETRY_TIMES': 5,
                       'DOWNLOAD_DELAY': 1,
                       'FEED_URI': r'output.xlsx',
                       'FEED_FORMAT': 'xlsx',
                       'FEED_EXPORTERS': {'xlsx': 'scrapy_xlsx.XlsxItemExporter'},
                       }

    def parse(self, response):
        sidebar_nav = response.xpath("//div[@class='top-wrapper']/div/div/div/ul/li[contains(@id,'czcategory')][a]")
        for category in sidebar_nav:
            sub_categories = category.xpath("./div/ul/li/a")
            for sub_category in sub_categories:
                url = sub_category.xpath("./@href").get()
                yield Request(url, callback=self.parse_listing, dont_filter=True)

    def parse_listing(self, response):
        book_listing = response.xpath("//a[@class='thumbnail product-thumbnail']/@href").extract()
        for book_url in book_listing:
            yield Request(book_url, callback=self.parse_detail, dont_filter=True)

        next_page_url = response.xpath("//a[@rel='next']/@href").get()
        if next_page_url:
            print(next_page_url)
            yield Request(next_page_url, callback=self.parse_listing, dont_filter=True)

    def parse_detail(self, response):
        yield {
            "title": response.xpath(
                "//div[@id='product-description-short']//td[contains(b/text(),'Titolo')]/following-sibling::td/text()").get(
                ''),
            'price': response.xpath("//div[@class='current-price']/span/text()").get(''),
            "isbn": response.xpath(
                "//div[@id='product-description-short']//td[contains(b/text(),'Ean')]/following-sibling::td/text()").get(
                ''),
            "url": response.url
        }
