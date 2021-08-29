import logging


def init_app(app):

    if app.config["ENV"] != "development":
        gunicorn_logger = logging.getLogger("gunicorn.error")

        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(logging.INFO)

    else:
        logging.basicConfig(
            filename="logger.log",
            format="%(asctime)s %(levelname)8s (%(name)s:%(lineno)s): %(message)s",
            filemode="w",
            level=logging.DEBUG,
        )

    return app
