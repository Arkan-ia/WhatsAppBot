import traceback

from marshmallow import ValidationError
from src.infrastructure.di.container import injector
from src.domain.errors.core_error import CoreError
from src.infrastructure.shared.logger.logger import LogAppManager

logger: LogAppManager = injector.get(LogAppManager)
logger.set_caller("Middlewares")
logger.set_max_json_length(1)


def register_middlewares(app):
    @app.errorhandler(CoreError)
    def handler(e: CoreError):
        logger.error(e.message, e.detailed_message)
        return e.message, e.code

    @app.errorhandler(Exception)
    def handler(e: Exception):
        logger.error(e, "\n", traceback.format_exc())
        return "An internal error has occurred", 500

    @app.errorhandler(ValidationError)
    def handler(e: ValidationError):
        logger.error(e, "\n", traceback.format_exc())
        return e.messages, 400
