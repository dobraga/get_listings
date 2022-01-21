from time import time
import logging


log = logging.getLogger(__name__)


class timeit:
    def __init__(self, text, log=log, level_log="debug") -> None:
        self.text, self.log, self.level_log = text, log, level_log

    def __enter__(self):
        self.ini = time()
        self.log.debug(f"{self.text} - started")

    def __exit__(self, type, value, traceback):
        finished = round(time() - self.ini, 0)
        if value is None:
            if self.level_log == "info":
                self.log.info(f"{self.text} - finished in {finished} seconds")
            else:
                self.log.debug(f"{self.text} - finished in {finished} seconds")
        else:
            self.log.error(
                f"{self.text} - finished with errors in {finished} seconds: {value}"
            )
