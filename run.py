if __name__ == "__main__":
    from aluguel.util.context import Selenoid, timeit
    from aluguel.data.preprocess import preprocess
    from aluguel.util.config import Configurations
    from aluguel.fetcher.metro import MetroSpyder
    from aluguel.fetcher.imoveis import Imoveis
    from aluguel.util import remove_files
    from aluguel.util.log import Logger
    from time import sleep
    
    conf = Configurations()
    log_file = "aluguel.log"

    # MetroSpyder(conf).run()

    remove_files("./logs", [log_file])
    remove_files("./video")

    log = Logger(log_file)

    try:
        with Selenoid(log):
            imovel = Imoveis(conf, log)

            while True:
                with timeit(log, "Processo finalizado em {delta} segundos\n"):
                    imovel.run()
                    preprocess(conf)

                sleep(1*60*60) # Buscar dados novos a cada uma hora

    except KeyboardInterrupt:
        log.warning("Processo cancelado\n")

    except Exception as e:
        log.error(f"Proceso finalizado com erro: {str(e)}\n")
