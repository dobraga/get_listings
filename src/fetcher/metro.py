import scrapy


class MetroSpyder(scrapy.Spider):
    name = "metrospyder"

    def __init__(self):
        super(MetroSpyder).__init__()
        self.allowed_domains = ["pt.wikipedia.org", "tools.wmflabs.org"]
        self.start_urls = [
            "https://pt.wikipedia.org/wiki/Metr%C3%B4_do_Rio_de_Janeiro",
            "https://pt.wikipedia.org/wiki/SuperVia",
        ]

    def parse(self, response):
        links = response.xpath(
            '//*[@id="mw-content-text"]/div[1]/table/tbody/tr/td/small/a/@href'
        ).getall()

        linha = response.xpath(
            '//*[@id="mw-content-text"]/div[1]/table/tbody/tr/td/small/a//@title'
        ).getall()

        for i, link in enumerate(links):
            yield scrapy.Request(
                response.urljoin(link),
                callback=self.parse_linha,
                cb_kwargs={"linha": linha[i]},
            )

    def parse_linha(self, response, linha):
        links = response.xpath(
            '//*[@id="mw-content-text"]/div[1]//table/tbody/tr/td/a[contains(@href, "wiki/Esta")]/@href'
        ).getall()

        for link in links:
            yield scrapy.Request(
                response.urljoin(link),
                callback=self.parse_estacao,
                cb_kwargs={"linha": linha},
            )

    def parse_estacao(self, response, linha):
        estacao = response.xpath('//*[@id="firstHeading"]/text()').get()
        link = response.xpath(
            '//*[@id="mw-content-text"]//a[contains(@href, "tools.wmflabs.org")]/@href'
        ).get()

        if link:
            yield scrapy.Request(
                link,
                callback=self.pase_latlng,
                cb_kwargs={"linha": linha, "estacao": estacao},
            )

    def pase_latlng(self, response, linha, estacao):
        latlng = response.xpath(
            '//*[@id="mw-content-text"]/div/div[1]/table/tbody/tr[1]/td[1]/span[3]/span/text()'
        ).getall()

        yield {
            "linha": linha,
            "estacao": estacao,
            "lat": float(latlng[0]),
            "lng": float(latlng[1]),
        }

