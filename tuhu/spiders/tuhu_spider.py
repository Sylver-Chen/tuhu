from scrapy.loader import ItemLoader
import scrapy
from tuhu.items import TuhuItem


def get_urls(domain):
    urls = []
    for province in get_provinces():
        urls.append(domain + '/' + province + '.aspx')
    return urls


def get_provinces():
    provinces = []
    with open('provinceFile', 'rt') as f:
        for line in f:
            line = line.strip('\n')
            print(line)
            provinces.append(line)
    return provinces


class TuhuSpider(scrapy.Spider):
    name = "tuhu"
    domain = "https://www.tuhu.cn/shops"

    start_urls = get_urls(domain)

    def parse(self, response):
        xpath = '//div[@class="shop-list"]//a[@class="carparname"]/@href'
        urls = response.xpath(xpath).extract()

        headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        for url in urls:
            request = scrapy.Request(url=url, callback=self.parse_shop,
                                     headers=headers)
            request.meta['url'] = url
            yield request

    def parse_shop(self, response):
        il = ItemLoader(item=TuhuItem(), response=response)
        il.add_value('url', response.meta['url'])
        il.add_xpath('name', '//div[@class="shop-info"]/div[@class="name"]/h1/text()')
        il.add_xpath('shoplevel', '//div[@class="shop-info"]/div[@class="name"]/h1/text()')
        il.add_xpath('shophours', '//div[@class="shop-info"]/p[1]/span/text()')
        il.add_xpath('shoptype', '//div[@class="shop-info"]/p[2]/span/text()')
        il.add_xpath('paymenttype', '//div[@class="shop-info"]/p[3]/span/text()')
        il.add_xpath('tel', '//div[@class="shop-info"]/p[4]/span/text()')
        il.add_xpath('addr', '//div[@class="shop-info"]/div[@class="address clearfix"]//span[@class="text"]/text()')

        xpath_tire_yes = '//div[@class="shop-service"]//i[@class="i-shop i-tire"]/parent::div[@class="title"]/following-sibling::ul[@class="list clearfix"]/li[not(@class)]/text()'
        xpath_tire_no = '//div[@class="shop-service"]//i[@class="i-shop i-tire"]/parent::div[@class="title"]/following-sibling::ul[@class="list clearfix"]/li[@class]/text()'
        for service in response.xpath(xpath_tire_yes).extract():
            il.add_value('tireservice_yes', service)
        for service in response.xpath(xpath_tire_no).extract():
            il.add_value('tireservice_no', service)

        xpath_maintenance_yes = '//div[@class="shop-service"]//i[@class="i-shop i-baoyang"]/parent::div[@class="title"]/following-sibling::ul[@class="list clearfix"]/li[not(@class)]/text()'
        xpath_maintenance_no = '//div[@class="shop-service"]//i[@class="i-shop i-baoyang"]/parent::div[@class="title"]/following-sibling::ul[@class="list clearfix"]/li[@class]/text()'
        for service in response.xpath(xpath_maintenance_yes).extract():
            il.add_value('maintenance_yes', service)
        for service in response.xpath(xpath_maintenance_no).extract():
            il.add_value('maintenance_no', service)

        return il.load_item()
