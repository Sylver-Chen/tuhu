from scrapy.loader import ItemLoader
import scrapy
import itertools
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
        xpath = '//div[@class="row dealer-list"]//h6/a/@href'
        urls = response.xpath(xpath).extract()

        headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        for url in urls:
            url = url[:url.find('?leads')] + 'about.html'
            request = scrapy.Request(url=url, callback=self.parse_about,
                                     headers=headers)
            request.meta['url'] = url
            yield request
        # for url in urls:
        #     url = url[:url.find('?leads')] + 'contact.html'
        #     request = scrapy.Request(url=url, callback=self.parse_contact,
        #                              headers=headers)
        #     request.meta['url'] = url
        #     yield request

    def parse_about(self, response):
        il = ItemLoader(item=DealerinfoItem(), response=response)
        il.add_value('url', response.meta['url'])
        il.add_xpath('name', '//div[@class="info"]/h1/text()')
        il.add_xpath('description', '//div[@class="article"]')
        il.add_xpath('tel', '//div[@class="info"]/div[@class="tel"]/strong/text()')
        il.add_xpath('addr', '//div[@class="info"]/div[@class="adress"]/text()')
        return il.load_item()

    def parse_contact(self, response):
         il = ItemLoader(item=DealerinfoItem(), response=response)
         il.add_value('url', response.meta['url'])
         contactdetail = ''
         xpathtitle = '//ul[@class="telways"]/li/span/text()'
         xpathinfo = '//ul[@class="telways"]/li/text()'
         contactdetail = map(lambda title, info: title.extract()+info.extract(),
                             response.xpath(xpathtitle), response.xpath(xpathinfo))
         il.add_value('detail', contactdetail)


         
         pass
