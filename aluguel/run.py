import argparse
from fetcher.imoveis import Imoveis
from fetcher.metro import MetroSpyder
from data.preprocess import preprocess
from config import Configurations

config = Configurations()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        "--site", choices=["zap", "vivareal"], default=["zap", "vivareal"], nargs="+",
    )
    p.add_argument("--max_page", default="5")
    p.add_argument("--tipo_contrato", choices=["Alugar"], default="Alugar")
    p.add_argument("--tipo_propriedade", choices=["Apartamento"], default="Apartamento")
    # p.add_argument("--local", required=True)
    p.add_argument("--local", default="Tijuca")
    p.add_argument("--teste", action="store_true")

    arguments = vars(p.parse_args())

    MetroSpyder(conf=config).run()

    imovel = Imoveis(conf=config, **arguments)
    imovel.run()

    df = preprocess()


    # from aluguel.fetcher.aux import *
    # from selenium.webdriver import Chrome

    # driver = Chrome(config["dir_webdriver"])
    # driver.maximize_window()
    # url = "https://www.vivareal.com.br"
    # driver.get(url)

    # tipo_contrato = "Alugar"
    # tipo_propriedade = "Casa"
    # local = "Tijuca"



