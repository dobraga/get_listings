import os
import requests
from math import log
from time import time
from . import str_flat
from selenium.webdriver import Remote

class timeit():
    def __init__(self, log, msg:str):
        self.log = log
        self.msg = msg

    def __enter__(self):
        self.ini = time()

    def __exit__(self, *args):
        fim = time()
        self.log.info(self.msg.format(delta = (fim - self.ini)))



class RemoteLogger():
    def __init__(
        self, config:dict, log, what:str = None,
        url:str = None, implicitly_wait:int = 30
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


    def __enter__(self):
        return self.driver


    def __exit__(self, type, value, traceback):
        self.driver.quit()

        if type:
            self.log.error(f"{self.msg}: {str_flat(str(value), ' ')}")
        else:
            self.log.debug(f"{self.msg}: com sucesso")

        return True



class Selenoid():
    def __init__(self, log):
        self.log = log


    def __enter__(self):
        if not os.path.exists("cm"):
            self.log.info("Baixando Selenoid ...")
            r = requests.get("https://github.com/aerokube/cm/releases/download/1.7.2/cm_linux_amd64")
            with open("cm", "wb") as file:
                file.write(r.content)
            os.system("chmod +x cm")
            self.log.info("Selenoid baixado com sucesso")
        else:
            self.log.debug("Selenoid já existente")

        os.system("./cm selenoid start")
        os.system("./cm selenoid-ui start")
        self.log.info("Selenoid iniciou com sucesso")
        return self


    def __exit__(self, *args):
        os.system("./cm selenoid-ui stop")
        os.system("./cm selenoid stop")
        self.log.info("Selenoid parou com sucesso")

