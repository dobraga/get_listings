import os
from time import time
from . import str_flat
from ..fetcher.aux import get_sleep
from selenium.webdriver import Remote


class timeit:
    def __init__(self, log, msg: str):
        self.log = log
        self.msg = msg

    def __enter__(self):
        self.ini = time()

    def __exit__(self, *args):
        fim = time()
        self.log.info(self.msg.format(delta=(fim - self.ini)))


class RemoteLogger:
    def __init__(
        self,
        config: dict,
        log,
        what: str = None,
        url: str = None,
        implicitly_wait: int = 45,
    ):
        self.log = log
        self.driver = Remote(**config)
        self.driver.implicitly_wait(implicitly_wait)
        msg = self.driver.session_id

        if what:
            msg = f"{what}: {msg}"
        if url:
            msg = f"{msg}: {url}"

        self.msg = msg

        if url:
            get_sleep(self.driver, url)

    def __enter__(self):
        return self.driver

    def __exit__(self, type, value, traceback):
        self.driver.quit()

        if type:
            self.log.error(f"{self.msg}: {str_flat(str(value), ' ')}")
        else:
            self.log.debug(f"{self.msg}: com sucesso")

        return True


class Selenoid:
    def __init__(self, log):
        self.log = log

    def __enter__(self):
        os.system("docker pull selenoid/firefox:84.0")
        os.system('docker-compose -f "docker-compose.yml" up -d --build')
        self.log.info("Selenoid iniciou com sucesso")
        return self

    def __exit__(self, *args):
        os.system('docker-compose -f "docker-compose.yml" down')
        self.log.info("Selenoid parou com sucesso")
