import logging


def init_app(app):
    gunicorn_logger = logging.getLogger("gunicorn.error")

    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    return app
