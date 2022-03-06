from time import time
import logging


log = logging.getLogger(__name__)


class timeit:
    def __init__(self, text, log=log, level_log="info") -> None:
        self.text, self.log, self.level_log = text, log, level_log

    def __enter__(self):
        self.ini = time()
        self.log.debug(f"{self.text} - started")
        return self

    def __exit__(self, type, value, traceback):
        elapsed = int(round(time() - self.ini, 0))
        self.elapsed = elapsed
        if value is None:
            if self.level_log == "info":
                self.log.info(f"{self.text} - finished in {elapsed} seconds")
            else:
                self.log.debug(f"{self.text} - finished in {elapsed} seconds")
        else:
            self.log.error(
                f"{self.text} - finished with errors in {elapsed} seconds: {value}"
            )
