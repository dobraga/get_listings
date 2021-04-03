from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy import Spider, Request
from os.path import join, exists
from os import remove
import logging

logging.getLogger("scrapy").setLevel(logging.WARNING)
logging.getLogger("scrapy").propagate = False
log = logging.getLogger(__name__)


class MetroSpyder(Spider):
    name = "metro"

    def __init__(self, conf):
        super().__init__()
        self.conf = conf
        self.allowed_domains = ["pt.wikipedia.org", "tools.wmflabs.org"]
        self.start_urls = conf["urls_metro_trem"]
        self.file = join(conf["dir_input"], "metro.jsonlines")

    def parse(self, response):
        base_xpath = (
            '(//table/tbody/tr/th[contains(text(), "erminais")]/../..)[1]/tr/td[1]//a'
        )

        links = response.xpath(base_xpath + "/@href").getall()
        linha = response.xpath(base_xpath + "/@title").getall()

        for i, link in enumerate(links):
            yield Request(
                response.urljoin(link),
                callback=self.parse_linha,
                cb_kwargs={"linha": linha[i]},
            )

    def parse_linha(self, response, linha):
        links = response.xpath(
            '//table/tbody/tr/td/a[contains(@href, "wiki/Esta")]/@href'
        ).getall()

        for link in links:
            yield Request(
                response.urljoin(link),
                callback=self.parse_estacao,
                cb_kwargs={"linha": linha},
            )

    def parse_estacao(self, response, linha):
        estacao = response.xpath('//*[@id="firstHeading"]/text()').get()
        link = response.xpath('//a[contains(@href, "tools.wmflabs.org")]/@href').get()

        if link:
            yield Request(
                link,
                callback=self.pase_latlng,
                cb_kwargs={"linha": linha, "estacao": estacao},
            )

    def pase_latlng(self, response, linha, estacao):
        latlng = response.xpath('//*[contains(@class, "geo")]/span/text()').getall()

        yield {
            "linha": linha,
            "estacao": estacao,
            "lat": float(latlng[0]),
            "lng": float(latlng[1]),
        }

        log.info(f'Busca "{linha}/{estacao}" ok')


def run(conf):
    file = join(conf["dir_input"], "metro.jsonlines")

    if not exists(file):
        log.info("Getting metro/trem information")

        settings = {
            "FEEDS": {
                file: {
                    "format": "jsonlines",
                    "encoding": "utf8",
                },
            }
        }

        runner = CrawlerRunner(settings)

        d = runner.crawl(MetroSpyder, conf=conf)
        d.addBoth(lambda _: reactor.stop())
        reactor.run()
