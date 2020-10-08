# from multiprocessing.pool import ThreadPool as Pool
from multiprocessing import Pool

import argparse
from scrapy.crawler import CrawlerProcess, CrawlerRunner

from fetcher.zap import ZapSpyder
from fetcher.vivareal import VivaRealSpyder
from fetcher.metro import MetroSpyder

from os.path import join, abspath, dirname

dir_src = dirname(__file__)
dir_project = abspath(join(dir_src, ".."))
dir_data = join(dir_project, "data")
dir_input = join(dir_data, "input")
dir_output = join(dir_data, "output")

conf = {
    "zap": {
        "crawler": ZapSpyder,
        "url": "https://www.zapimoveis.com.br/{tipo_contrato0}/{tipo_propriedade0}/{uf}+{cidade}+{zona}+{bairro}/?transacao={tipo_contrato1}&tipoUnidade={tipo_propriedade1}",
        "tipo_contrato": {"aluguel": ["aluguel", "Aluguel"]},
        "tipo_propriedade": {
            "apartamento": ["apartamentos", "Residencial,Apartamento"]
        },
    },
    "vivareal": {
        "crawler": VivaRealSpyder,
        "url": "https://www.vivareal.com.br/{tipo_contrato}/{uf}/{cidade}/{zona}/{bairro}/{tipo_propriedade}/?tipos={tipo_propriedade}",
        "tipo_contrato": {"aluguel": ["aluguel"]},
        "tipo_propriedade": {"apartamento": ["apartamento_residencial"]},
    },
    "metro": {"crawler": MetroSpyder,},
}


def format(site, tipo_contrato, tipo_propriedade, uf, cidade, zona, bairro):
    conf_site = conf[site]

    tp = {
        "tipo_contrato": conf_site["tipo_contrato"][tipo_contrato],
        "tipo_propriedade": conf_site["tipo_propriedade"][tipo_propriedade],
    }

    f = {"uf": uf, "cidade": cidade, "zona": zona, "bairro": bairro}

    for key, value in tp.items():
        for i, val in enumerate(value):
            new_key = key + str(i) if len(value) > 1 else key
            f[new_key] = val
    return f


def make_url(site, tipo_contrato, tipo_propriedade, uf, cidade, zona, bairro):
    conf_site = conf[site]
    url = conf_site["url"]
    f = format(site, tipo_contrato, tipo_propriedade, uf, cidade, zona, bairro)
    return url.format_map(f)


def make_function(site, arguments=None):
    file = join(dir_input, site + ".jsonlines")

    settings = {
        "FEEDS": {file: {"format": "jsonlines", "encoding": "utf8",},},
        "HTTPERROR_ALLOWED_CODES": [403],
        "LOG_LEVEL": arguments.log_level,
    }

    if site not in ["metro"]:
        url = make_url(
            site,
            arguments.tipo_contrato,
            arguments.tipo_propriedade,
            arguments.uf,
            arguments.cidade,
            arguments.zona,
            arguments.bairro,
        )

        print(f"Página Inicial '{url}' salvando no arquivo {file}")

        def crawler_func():
            crawler_process = CrawlerProcess(settings)
            crawler_process.crawl(
                conf[site]["crawler"],
                url=url,
                max_page=int(arguments.max_page),
                teste=arguments.teste,
            )
            crawler_process.start()

    else:

        def crawler_func():
            crawler_process = CrawlerProcess(settings)
            crawler_process.crawl(conf[site]["crawler"])
            crawler_process.start()

    return crawler_func()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--site",
        choices=["zap", "vivareal", "metro"],
        default=["zap", "vivareal", "metro"],
        nargs="+",
    )

    parser.add_argument("--max_page", default="1")

    parser.add_argument("--tipo_contrato", choices=["aluguel"], default="aluguel")

    parser.add_argument(
        "--tipo_propriedade", choices=["apartamento"], default="apartamento"
    )

    parser.add_argument("--uf", choices=["rj"], default="rj")

    parser.add_argument(
        "--cidade", choices=["rio-de-janeiro"], default="rio-de-janeiro"
    )

    parser.add_argument("--zona", choices=["zona-norte"], default="zona-norte")

    parser.add_argument("--bairro", choices=["tijuca"], default="tijuca")

    parser.add_argument("--teste", action="store_true")

    parser.add_argument(
        "--log_level", choices=["DEBUG", "INFO", "WARN"], default="WARN"
    )

    arguments = parser.parse_args()

    def make(site, arguments=arguments):
        return make_function(site, arguments)

    pool = Pool(3)

    try:
        pool.map(make, arguments.site)

    except KeyboardInterrupt:
        pool.terminate()
        pool.close()
        print("Cancelado")
    except Exception as e:
        print(e)
