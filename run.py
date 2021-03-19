if __name__ == "__main__":
    from get_imoveis.data.preprocess import preprocess
    from get_imoveis._config import Configurations
    from get_imoveis.metro import MetroSpyder
    from get_imoveis.request import run_request
    from get_imoveis._log import Logger

    conf = Configurations()
    log = Logger("get_imoveis.log")

    MetroSpyder(conf).run()
    run_request(conf)
