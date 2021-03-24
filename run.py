if __name__ == "__main__":
    from get_listings._config import Configurations
    from get_listings.preprocess import preprocess
    from get_listings.request import run_request
    from get_listings.metro import MetroSpyder
    from get_listings._log import setup_logger
    from get_listings.model import run_model

    setup_logger()
    conf = Configurations()

    run_request(conf)
    MetroSpyder(conf).run()
    preprocess(conf)
    run_model(conf)
